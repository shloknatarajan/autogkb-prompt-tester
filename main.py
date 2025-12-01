from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from llm import Model, generate_response
import asyncio
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

# Import utility modules
from utils.config import (
    PROMPTS_FILE,
    BEST_PROMPTS_FILE,
    OUTPUT_DIR,
    BENCHMARK_RESULTS_DIR,
    GROUND_TRUTH_FILE,
    GROUND_TRUTH_NORMALIZED_FILE,
    MARKDOWN_DIR,
)
from utils.benchmark_runner import BenchmarkRunner
from utils.prompt_manager import PromptManager
from utils.citation_generator import generate_citations
from utils.output_manager import save_output, combine_outputs
from utils.normalization import normalize_outputs_in_directory

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pipeline job management
class PipelineJob:
    def __init__(self, job_id: str, config: dict):
        self.id = job_id
        self.status: Literal[
            "pending", "running", "completed", "failed", "cancelled"
        ] = "pending"
        self.current_stage: str = "initializing"
        self.progress: float = 0.0
        self.pmcids_processed: int = 0
        self.pmcids_total: int = 0
        self.current_pmcid: Optional[str] = None
        self.messages: list[str] = []
        self.result: Optional[dict] = None
        self.error: Optional[str] = None
        self.config = config
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.cancelled: bool = False

    def add_message(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages.append(f"[{timestamp}] {message}")
        self.updated_at = datetime.now().isoformat()

    def cancel(self):
        self.cancelled = True
        self.status = "cancelled"
        self.add_message("Pipeline cancelled by user")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "status": self.status,
            "current_stage": self.current_stage,
            "progress": self.progress,
            "pmcids_processed": self.pmcids_processed,
            "pmcids_total": self.pmcids_total,
            "current_pmcid": self.current_pmcid,
            "messages": self.messages[-50:],  # Last 50 messages
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# In-memory job store
pipeline_jobs: dict[str, PipelineJob] = {}


class PipelineStartRequest(BaseModel):
    data_dir: str = MARKDOWN_DIR
    model: str = "gpt-4o-mini"
    concurrency: int = 3


class PromptRequest(BaseModel):
    prompt: str
    text: str
    model: Model
    response_format: dict | None = None


class PromptResponse(BaseModel):
    output: str


class SavePromptRequest(BaseModel):
    task: str
    name: str
    prompt: str
    text: str
    model: Model
    response_format: dict | None = None
    output: str


class SaveAllPromptsRequest(BaseModel):
    prompts: list[dict]
    text: str


class BestPrompt(BaseModel):
    task: str
    prompt: str
    model: Model
    response_format: dict | None = None
    name: str


class RunBestPromptsRequest(BaseModel):
    text: str
    best_prompts: list[BestPrompt]
    pmcid: str | None = None
    citation_prompt: str | None = None


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@app.post("/test-prompt", response_model=PromptResponse)
async def test_prompt(request: PromptRequest):
    try:
        response_format = None

        # Use custom response format if provided, otherwise fall back to structured_output flag
        if request.response_format:
            response_format = request.response_format

        output = await generate_response(
            prompt=request.prompt,
            text=request.text,
            model=request.model,
            response_format=response_format,
        )
        return {"output": output}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/save-prompt")
async def save_prompt(request: SavePromptRequest):
    try:
        # Read existing prompts
        if os.path.exists(PROMPTS_FILE):
            with open(PROMPTS_FILE, "r") as f:
                prompts = json.load(f)
        else:
            prompts = []

        # Try to parse output as JSON if possible
        try:
            parsed_output = json.loads(request.output)
        except:
            parsed_output = request.output

        # Create new prompt entry
        new_prompt = {
            "task": request.task,
            "name": request.name,
            "prompt": request.prompt,
            "model": request.model,
            "response_format": request.response_format,
            # "output": parsed_output,  # Removed to reduce file size
            "timestamp": datetime.now().isoformat(),
        }

        # Append new prompt
        prompts.append(new_prompt)

        # Save back to file
        with open(PROMPTS_FILE, "w") as f:
            json.dump(prompts, f, indent=2)

        return {"status": "success", "message": "Prompt saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/prompts")
async def get_prompts():
    try:
        if os.path.exists(PROMPTS_FILE):
            with open(PROMPTS_FILE, "r") as f:
                prompts = json.load(f)
            return {"prompts": prompts}
        else:
            return {"prompts": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/best-prompts")
async def get_best_prompts():
    """Return the best prompts configuration from best_prompts.json."""
    try:
        best_prompts_file = "best_prompts.json"
        if os.path.exists(best_prompts_file):
            with open(best_prompts_file, "r") as f:
                return json.load(f)
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/save-all-prompts")
async def save_all_prompts(request: SaveAllPromptsRequest):
    try:
        saved_prompts = []

        for prompt_data in request.prompts:
            # Try to parse output as JSON if possible
            try:
                parsed_output = (
                    json.loads(prompt_data["output"])
                    if prompt_data.get("output")
                    else None
                )
            except:
                parsed_output = prompt_data.get("output")

            # Try to parse response format if it's a string
            response_format = prompt_data.get("responseFormat")
            if response_format and isinstance(response_format, str):
                try:
                    response_format = json.loads(response_format)
                except:
                    response_format = None

            saved_prompt = {
                "task": prompt_data.get("task", "Default"),
                "name": prompt_data.get("name", "Untitled Prompt"),
                "prompt": prompt_data.get("prompt", ""),
                "model": prompt_data.get("model", "gpt-4o-mini"),
                "response_format": response_format,
                # "output": parsed_output,  # Removed to reduce file size
                "timestamp": datetime.now().isoformat(),
            }
            saved_prompts.append(saved_prompt)

        # Overwrite the file with current prompts
        with open(PROMPTS_FILE, "w") as f:
            json.dump(saved_prompts, f, indent=2)

        return {
            "status": "success",
            "message": f"Saved {len(saved_prompts)} prompts successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def generate_citations_for_annotation(
    annotation: dict, full_text: str, citation_prompt_template: str, model: Model
) -> list[str]:
    """Generate citations for a single annotation by finding supporting quotes in the text."""
    # Use the shared utility function
    return await generate_citations(
        annotation, full_text, model, citation_prompt_template
    )


async def run_single_task(best_prompt: BestPrompt, text: str) -> tuple:
    """Run a single task and return (task_name, prompt_name, output, error)."""
    try:
        output = await generate_response(
            prompt=best_prompt.prompt,
            text=text,
            model=best_prompt.model,
            response_format=best_prompt.response_format,
        )

        # Parse output as JSON
        try:
            parsed_output = json.loads(output)
        except:
            parsed_output = {best_prompt.name: output}

        return (best_prompt.task, best_prompt.name, parsed_output, None)
    except Exception as e:
        return (best_prompt.task, best_prompt.name, None, str(e))


async def generate_single_citation(
    ann_type: str,
    index: int,
    annotation: dict,
    text: str,
    citation_prompt: str,
    model: Model,
) -> tuple:
    """Generate citation for one annotation and return (ann_type, index, citations, error)."""
    try:
        citations = await generate_citations_for_annotation(
            annotation, text, citation_prompt, model
        )
        return (ann_type, index, citations, None)
    except Exception as e:
        return (ann_type, index, [], str(e))


@app.get("/outputs")
async def list_outputs():
    """List all output files in the outputs directory."""
    try:
        if not os.path.exists(OUTPUT_DIR):
            return {"files": []}

        files = []
        for filename in os.listdir(OUTPUT_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(OUTPUT_DIR, filename)
                stat = os.stat(filepath)
                files.append(
                    {
                        "filename": filename,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "size": stat.st_size,
                    }
                )

        # Sort by modification time, newest first
        files.sort(key=lambda x: x["modified"], reverse=True)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/outputs/{filename}")
async def get_output(filename: str):
    """Get the contents of a specific output file."""
    try:
        # Sanitize filename to prevent directory traversal
        filename = os.path.basename(filename)
        filepath = os.path.join(OUTPUT_DIR, filename)

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")

        with open(filepath, "r") as f:
            content = json.load(f)

        return content
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run-best-prompts")
async def run_best_prompts(request: RunBestPromptsRequest):
    try:
        task_results = {}
        prompts_used = {}

        # Run all tasks in parallel
        print(f"Running {len(request.best_prompts)} tasks in parallel...")
        task_coroutines = [
            run_single_task(best_prompt, request.text)
            for best_prompt in request.best_prompts
        ]
        task_execution_results = await asyncio.gather(*task_coroutines)

        # Process results
        for task_name, prompt_name, output, error in task_execution_results:
            if error:
                task_results[task_name] = {"error": error}
                print(f"✗ Task '{task_name}' failed: {error}")
            else:
                task_results.update(output)
                print(f"✓ Completed task: {task_name} using prompt: {prompt_name}")
            prompts_used[task_name] = prompt_name

        # Generate citations if citation prompt is provided
        total_annotations = 0
        citations_generated = 0

        if request.citation_prompt:
            print("Generating citations for annotations...")

            # Collect all citation tasks
            citation_tasks = []

            if "var_pheno_ann" in task_results and isinstance(
                task_results["var_pheno_ann"], list
            ):
                for i, annotation in enumerate(task_results["var_pheno_ann"]):
                    citation_tasks.append(
                        generate_single_citation(
                            "var_pheno_ann",
                            i,
                            annotation,
                            request.text,
                            request.citation_prompt,
                            request.best_prompts[0].model,
                        )
                    )

            if "var_drug_ann" in task_results and isinstance(
                task_results["var_drug_ann"], list
            ):
                for i, annotation in enumerate(task_results["var_drug_ann"]):
                    citation_tasks.append(
                        generate_single_citation(
                            "var_drug_ann",
                            i,
                            annotation,
                            request.text,
                            request.citation_prompt,
                            request.best_prompts[0].model,
                        )
                    )

            if "var_fa_ann" in task_results and isinstance(
                task_results["var_fa_ann"], list
            ):
                for i, annotation in enumerate(task_results["var_fa_ann"]):
                    citation_tasks.append(
                        generate_single_citation(
                            "var_fa_ann",
                            i,
                            annotation,
                            request.text,
                            request.citation_prompt,
                            request.best_prompts[0].model,
                        )
                    )

            if citation_tasks:
                print(f"Generating {len(citation_tasks)} citations in parallel...")
                citation_results = await asyncio.gather(*citation_tasks)

                # Apply results
                successful = 0
                failed = 0
                for ann_type, index, citations, error in citation_results:
                    task_results[ann_type][index]["Citations"] = citations
                    if error:
                        task_results[ann_type][index]["Citation_Error"] = error
                        failed += 1
                    else:
                        successful += 1

                citations_generated = len(citation_results)
                total_annotations = len(citation_results)
                print(f"✓ Citations complete: {successful} successful, {failed} failed")

        # Combine outputs
        combined_output = {
            **task_results,
            "input_text": request.text,
            "timestamp": datetime.now().isoformat(),
            "prompts_used": prompts_used,
        }

        # Save to file
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Extract PMCID from task results (set by summary/metadata task)
        extracted_pmcid = task_results.get("pmcid", None)

        # Determine filename: use extracted PMCID, fall back to request.pmcid, then timestamp
        if extracted_pmcid:
            filename = f"{OUTPUT_DIR}/{extracted_pmcid}.json"
            print(f"Using extracted PMCID: {extracted_pmcid}")
        elif request.pmcid:
            filename = f"{OUTPUT_DIR}/{request.pmcid}.json"
            print(f"Using provided PMCID: {request.pmcid}")
        else:
            # Fallback to timestamp-based filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{OUTPUT_DIR}/output_{timestamp}.json"
            print(f"No PMCID found, using timestamp: output_{timestamp}.json")

        with open(filename, "w") as f:
            json.dump(combined_output, f, indent=2)

        return {
            "status": "success",
            "message": f"Ran {len(request.best_prompts)} prompts successfully",
            "output_file": filename,
            "total_annotations": total_annotations,
            "citations_generated": citations_generated,
            "results": combined_output,
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


class BenchmarkFromOutputRequest(BaseModel):
    """Request to benchmark an existing output file."""

    filename: str


@app.post("/benchmark-from-output")
async def benchmark_from_output(request: BenchmarkFromOutputRequest):
    """
    Benchmark an existing output file against ground truth.

    This endpoint:
    1. Loads the output file from /outputs/
    2. Extracts PMCID and predictions from the file
    3. Compares predictions to ground truth
    4. Saves results to /benchmark_results/
    """
    try:
        # Load the output file
        filename = os.path.basename(request.filename)  # Sanitize
        filepath = os.path.join(OUTPUT_DIR, filename)

        if not os.path.exists(filepath):
            raise HTTPException(
                status_code=404, detail=f"Output file not found: {filename}"
            )

        with open(filepath, "r") as f:
            output_data = json.load(f)

        # Extract PMCID from the output file
        pmcid = output_data.get("pmcid")
        if not pmcid:
            raise HTTPException(
                status_code=400, detail="Output file does not contain PMCID"
            )

        print(f"\n=== Benchmarking from Output File ===")
        print(f"File: {filename}")
        print(f"PMCID: {pmcid}")
        print(f"Timestamp: {output_data.get('timestamp', 'unknown')}")

        # Debug logging
        print(f"\n=== Predictions from File ===")
        print(f"  var-pheno: {len(output_data.get('var_pheno_ann', []))} annotations")
        print(f"  var-drug: {len(output_data.get('var_drug_ann', []))} annotations")
        print(f"  var-fa: {len(output_data.get('var_fa_ann', []))} annotations")
        print(f"=== End Predictions ===\n")

        # Use BenchmarkRunner utility
        try:
            runner = BenchmarkRunner()
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

        # Check if ground truth exists for this PMCID
        if not runner.has_ground_truth(pmcid):
            raise HTTPException(
                status_code=404, detail=f"No ground truth found for PMCID: {pmcid}"
            )

        # Run benchmark
        benchmark_results = runner.benchmark_pmcid(pmcid, output_data, verbose=True)

        # Calculate average score
        task_scores, sample_counts = runner.calculate_task_averages({pmcid: benchmark_results})
        average_score = runner.calculate_overall_score(task_scores, sample_counts)

        # Calculate successful tasks
        successful = sum(1 for r in benchmark_results.values() if "error" not in r)
        failed = len(benchmark_results) - successful

        print(f"\n=== Benchmark Summary ===")
        print(f"Total tasks: {len(benchmark_results)}")
        print(f"Successful: {successful}")
        print(f"Failed/Skipped: {failed}")
        print(f"Average score: {average_score:.2%}")
        print(f"=========================\n")

        # Create benchmark result document
        timestamp = datetime.now().isoformat()
        benchmark_result = {
            "timestamp": timestamp,
            "pmcid": pmcid,
            "source_file": filename,
            "source_timestamp": output_data.get("timestamp"),
            "prompts_used": output_data.get("prompts_used", {}),
            "results": benchmark_results,
            "metadata": {
                "ground_truth_file": GROUND_TRUTH_FILE,
                "total_tasks": len(benchmark_results),
                "average_score": average_score,
                "tasks_with_errors": sum(
                    1 for r in benchmark_results.values() if "error" in r
                ),
            },
        }

        # Save to benchmark_results directory
        os.makedirs(BENCHMARK_RESULTS_DIR, exist_ok=True)
        result_filename = f"{BENCHMARK_RESULTS_DIR}/benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(result_filename, "w") as f:
            json.dump(benchmark_result, f, indent=2)

        print(f"✓ Benchmark results saved to {result_filename}")

        return {
            "status": "success",
            "message": f"Benchmarked output file {filename}",
            "filename": result_filename,
            "results": benchmark_result,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Benchmark from output error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/benchmark-results")
async def list_benchmark_results():
    """List all benchmark result files."""
    try:
        if not os.path.exists(BENCHMARK_RESULTS_DIR):
            return {"files": []}

        files = []
        for filename in os.listdir(BENCHMARK_RESULTS_DIR):
            # Skip pipeline benchmark files - they have a different format
            if filename.startswith("pipeline_benchmark_"):
                continue
            if filename.endswith(".json"):
                filepath = os.path.join(BENCHMARK_RESULTS_DIR, filename)

                # Read file to get metadata
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)

                    files.append(
                        {
                            "filename": filename,
                            "timestamp": data.get("timestamp"),
                            "pmcid": data.get("pmcid"),
                            "average_score": data.get("metadata", {}).get(
                                "average_score", 0
                            ),
                            "total_tasks": data.get("metadata", {}).get(
                                "total_tasks", 0
                            ),
                            "prompts_used": data.get("prompts_used", {}),
                        }
                    )
                except:
                    # If file can't be read, just include basic info
                    stat = os.stat(filepath)
                    files.append(
                        {
                            "filename": filename,
                            "timestamp": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                            "pmcid": None,
                            "average_score": 0,
                            "total_tasks": 0,
                            "prompts_used": {},
                        }
                    )

        # Sort by timestamp, newest first
        files.sort(key=lambda x: x.get("timestamp") or "", reverse=True)
        return {"files": files}

    except Exception as e:
        print("error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/benchmark-results/{filename}")
async def get_benchmark_result(filename: str):
    """Get the contents of a specific benchmark result file."""
    try:
        # Sanitize filename to prevent directory traversal
        filename = os.path.basename(filename)
        filepath = os.path.join(BENCHMARK_RESULTS_DIR, filename)

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")

        with open(filepath, "r") as f:
            content = json.load(f)

        return content

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Pipeline endpoints
async def process_single_pmcid(
    pmcid: str,
    data_dir: str,
    output_dir: str,
    prompt_details_map: dict,
    semaphore: asyncio.Semaphore,
) -> tuple[str, dict]:
    """
    Process a single PMCID with all prompts.
    Returns (pmcid, results_dict)
    """
    async with semaphore:
        # Load markdown file
        md_path = os.path.join(data_dir, f"{pmcid}.md")
        with open(md_path, "r") as f:
            text = f.read()

        # Run all prompts in parallel for this PMCID
        async def run_prompt(task: str, prompt_data: dict) -> tuple[str, dict]:
            try:
                model_str = prompt_data.get("model", "gpt-4o-mini")
                try:
                    model = Model(model_str)
                except ValueError:
                    model = Model.OPENAI_GPT_4O_MINI

                output = await generate_response(
                    prompt=prompt_data["prompt"],
                    text=text,
                    model=model,
                    response_format=prompt_data.get("response_format"),
                )

                try:
                    parsed_output = json.loads(output)
                    return (task, parsed_output)
                except json.JSONDecodeError:
                    return (task, {"error": "JSON parse failed"})

            except Exception as e:
                return (task, {"error": str(e)})

        # Run all tasks in parallel
        prompt_tasks = [
            run_prompt(task, prompt_data)
            for task, prompt_data in prompt_details_map.items()
        ]
        task_results = await asyncio.gather(*prompt_tasks)

        # Combine results
        pmcid_results = {"pmcid": pmcid}
        prompts_used = {}

        for task, result in task_results:
            if isinstance(result, dict) and "error" in result:
                pmcid_results[task] = result
            else:
                pmcid_results.update(result)
            prompts_used[task] = prompt_details_map[task].get("name", "unknown")

        # Generate citations for annotations
        from utils.citation_generator import CITATION_PROMPT_TEMPLATE

        citation_tasks = []
        for ann_type in ["var_pheno_ann", "var_drug_ann", "var_fa_ann"]:
            if ann_type in pmcid_results and isinstance(pmcid_results[ann_type], list):
                for i, annotation in enumerate(pmcid_results[ann_type]):
                    citation_tasks.append(
                        generate_single_citation(
                            ann_type,
                            i,
                            annotation,
                            text,
                            CITATION_PROMPT_TEMPLATE,
                            Model.OPENAI_GPT_4O_MINI,
                        )
                    )

        if citation_tasks:
            citation_results = await asyncio.gather(*citation_tasks)
            for ann_type, index, citations, error in citation_results:
                pmcid_results[ann_type][index]["Citations"] = citations
                if error:
                    pmcid_results[ann_type][index]["Citation_Error"] = error

        # Add metadata
        pmcid_results["timestamp"] = datetime.now().isoformat()
        pmcid_results["prompts_used"] = prompts_used

        # Save individual output
        output_file = os.path.join(output_dir, f"{pmcid}.json")
        with open(output_file, "w") as f:
            json.dump(pmcid_results, f, indent=2)

        return (pmcid, pmcid_results)


async def run_pipeline_task(job: PipelineJob):
    """Background task to run the full benchmark pipeline."""
    try:
        job.status = "running"
        job.current_stage = "loading_configuration"
        job.add_message("Starting pipeline...")

        # Load best prompts using PromptManager utility
        try:
            prompt_manager = PromptManager()
            prompt_details_map = prompt_manager.get_best_prompts()
            job.add_message(f"Loaded {len(prompt_details_map)} prompts")
        except Exception as e:
            raise Exception(f"Failed to load prompts: {e}")

        # Get list of PMCIDs to process
        data_dir = job.config.get("data_dir", MARKDOWN_DIR)
        if not os.path.exists(data_dir):
            raise Exception(f"Data directory not found: {data_dir}")

        markdown_files = [f for f in os.listdir(data_dir) if f.endswith(".md")]
        pmcids = [os.path.splitext(f)[0] for f in markdown_files]

        if not pmcids:
            raise Exception(f"No markdown files found in {data_dir}")

        job.pmcids_total = len(pmcids)
        job.add_message(f"Found {len(pmcids)} PMCIDs to process")

        # Create output directory for this run
        run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"outputs/pipeline_run_{run_timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        job.add_message(f"Output directory: {output_dir}")

        # Stage 1: Process PMCIDs in parallel with concurrency control
        job.current_stage = "processing_pmcids"
        concurrency = job.config.get("concurrency", 3)
        semaphore = asyncio.Semaphore(concurrency)
        job.add_message(f"Processing with concurrency: {concurrency}")

        # Create tasks for all PMCIDs
        pmcid_tasks = [
            process_single_pmcid(
                pmcid, data_dir, output_dir, prompt_details_map, semaphore
            )
            for pmcid in pmcids
        ]

        # Process with progress tracking
        all_outputs = {}
        completed = 0

        for coro in asyncio.as_completed(pmcid_tasks):
            # Check for cancellation
            if job.cancelled:
                job.add_message("Pipeline cancelled during PMCID processing")
                return

            pmcid, results = await coro
            all_outputs[pmcid] = results
            completed += 1
            job.pmcids_processed = completed
            job.current_pmcid = pmcid
            job.progress = (completed / len(pmcids)) * 0.8
            job.add_message(f"Completed {pmcid} ({completed}/{len(pmcids)})")

        # Check for cancellation before combining
        if job.cancelled:
            job.add_message("Pipeline cancelled")
            return

        job.add_message(f"Completed processing {len(pmcids)} PMCIDs")

        # Stage 1.5: Normalize terms using utility
        # job.current_stage = "normalizing_terms"
        # job.progress = 0.83
        # job.add_message("Normalizing terms in outputs...")
        #
        # normalized_count, failed_count = normalize_outputs_in_directory(
        #     output_dir, in_place=True, verbose=True
        # )
        #
        # # Reload normalized data
        # for pmcid in pmcids:
        #     output_file = Path(output_dir) / f"{pmcid}.json"
        #     if output_file.exists():
        #         with open(output_file, "r") as f:
        #             all_outputs[pmcid] = json.load(f)
        #
        # job.add_message(
        #     f"Term normalization complete: {normalized_count} successful, {failed_count} failed"
        # )

        # Stage 2: Combine outputs using utility
        job.current_stage = "combining_outputs"
        job.progress = 0.85
        job.add_message("Combining outputs...")

        combined_file = os.path.join(output_dir, f"combined_{run_timestamp}.json")
        combine_outputs(output_dir, combined_file, pmcids=pmcids)

        job.add_message(f"Saved combined output to {combined_file}")

        # Stage 3: Run benchmarks using BenchmarkRunner utility
        job.current_stage = "running_benchmarks"
        job.progress = 0.90
        job.add_message("Running benchmarks...")

        try:
            runner = BenchmarkRunner()
            job.add_message(
                f"Using ground truth: {os.path.basename(runner.ground_truth_source)}"
            )

            # Benchmark all PMCIDs
            (
                all_benchmark_results,
                average_scores,
                overall_score,
            ) = runner.benchmark_multiple(all_outputs, verbose=False)

            # Add messages for missing ground truth
            for pmcid, result in all_benchmark_results.items():
                if result is None:
                    job.add_message(f"Warning: No ground truth for {pmcid}, skipped")

            job.add_message(f"Benchmark complete. Overall score: {overall_score:.2%}")

        except Exception as e:
            raise Exception(f"Benchmark failed: {e}")

        # Stage 4: Save results
        job.current_stage = "saving_results"
        job.progress = 0.95
        job.add_message("Saving benchmark results...")

        os.makedirs(BENCHMARK_RESULTS_DIR, exist_ok=True)
        results_file = (
            f"{BENCHMARK_RESULTS_DIR}/pipeline_benchmark_{run_timestamp}.json"
        )

        pipeline_result = {
            "timestamp": datetime.now().isoformat(),
            "config": job.config,
            "output_directory": output_dir,
            "combined_file": combined_file,
            "summary": {
                "total_pmcids": len(pmcids),
                "benchmarked_pmcids": len(all_benchmark_results),
                "scores": average_scores,
                "overall": overall_score,
                "timestamp": datetime.now().isoformat(),
            },
            "pmcid_results": all_benchmark_results,
        }

        with open(results_file, "w") as f:
            json.dump(pipeline_result, f, indent=2)

        job.add_message(f"Results saved to {results_file}")

        # Complete
        job.status = "completed"
        job.current_stage = "completed"
        job.progress = 1.0
        job.result = {
            "output_directory": output_dir,
            "combined_file": combined_file,
            "results_file": results_file,
            "total_pmcids": len(pmcids),
            "overall_score": overall_score,
            "task_scores": average_scores,
        }
        job.add_message(
            f"Pipeline completed successfully! Overall score: {overall_score:.2%}"
        )

    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        job.add_message(f"Pipeline failed: {str(e)}")


@app.post("/pipeline/start")
async def start_pipeline(request: PipelineStartRequest):
    """Start a new pipeline job."""
    try:
        # Create new job
        job_id = str(uuid.uuid4())
        config = {
            "data_dir": request.data_dir,
            "model": request.model,
            "concurrency": request.concurrency,
        }

        job = PipelineJob(job_id, config)
        pipeline_jobs[job_id] = job

        # Start background task
        asyncio.create_task(run_pipeline_task(job))

        return {
            "status": "started",
            "job_id": job_id,
            "message": "Pipeline job started",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pipeline/status/{job_id}")
async def get_pipeline_status(job_id: str):
    """Get the current status of a pipeline job."""
    if job_id not in pipeline_jobs:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    job = pipeline_jobs[job_id]
    return job.to_dict()


@app.post("/pipeline/cancel/{job_id}")
async def cancel_pipeline_job(job_id: str):
    """Cancel a running pipeline job."""
    if job_id not in pipeline_jobs:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    job = pipeline_jobs[job_id]

    if job.status not in ["pending", "running"]:
        raise HTTPException(
            status_code=400, detail=f"Cannot cancel job with status: {job.status}"
        )

    job.cancel()
    return {"message": f"Job {job_id} cancelled", "status": job.status}


@app.get("/pipeline/events/{job_id}")
async def pipeline_events(job_id: str):
    """
    Server-Sent Events endpoint for real-time pipeline progress.

    Returns SSE stream with job status updates every second.
    """
    if job_id not in pipeline_jobs:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    async def event_generator():
        last_message_count = 0

        while True:
            if job_id not in pipeline_jobs:
                yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                break

            job = pipeline_jobs[job_id]
            job_data = job.to_dict()

            # Only send updates if there are new messages or status changed
            current_message_count = len(job.messages)

            yield f"data: {json.dumps(job_data)}\n\n"

            # Stop streaming if job is done
            if job.status in ["completed", "failed"]:
                break

            last_message_count = current_message_count
            await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/pipeline/jobs")
async def list_pipeline_jobs():
    """List all pipeline jobs."""
    jobs = []
    for job_id, job in pipeline_jobs.items():
        jobs.append(
            {
                "id": job.id,
                "status": job.status,
                "current_stage": job.current_stage,
                "progress": job.progress,
                "pmcids_processed": job.pmcids_processed,
                "pmcids_total": job.pmcids_total,
                "created_at": job.created_at,
                "updated_at": job.updated_at,
            }
        )

    # Sort by creation time, newest first
    jobs.sort(key=lambda x: x["created_at"], reverse=True)
    return {"jobs": jobs}


@app.get("/pipeline/results")
async def list_pipeline_results():
    """List all pipeline benchmark result files."""
    try:
        if not os.path.exists(BENCHMARK_RESULTS_DIR):
            return {"files": []}

        files = []
        for filename in os.listdir(BENCHMARK_RESULTS_DIR):
            if filename.startswith("pipeline_benchmark_") and filename.endswith(
                ".json"
            ):
                filepath = os.path.join(BENCHMARK_RESULTS_DIR, filename)

                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)

                    files.append(
                        {
                            "filename": filename,
                            "timestamp": data.get("timestamp", ""),
                            "total_pmcids": data.get("summary", {}).get(
                                "total_pmcids", 0
                            ),
                            "overall_score": data.get("summary", {}).get("overall", 0),
                            "config": data.get("config", {}),
                        }
                    )
                except Exception:
                    stat = os.stat(filepath)
                    files.append(
                        {
                            "filename": filename,
                            "timestamp": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                            "total_pmcids": 0,
                            "overall_score": 0,
                            "config": {},
                        }
                    )

        files.sort(key=lambda x: x.get("timestamp") or "", reverse=True)
        return {"files": files}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pipeline/results/{filename}")
async def get_pipeline_result(filename: str):
    """Get the contents of a specific pipeline benchmark result file."""
    try:
        filename = os.path.basename(filename)
        filepath = os.path.join(BENCHMARK_RESULTS_DIR, filename)

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")

        with open(filepath, "r") as f:
            content = json.load(f)

        return content

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
