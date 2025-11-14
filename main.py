from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm import Model, generate_response
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from benchmarks.pheno_benchmark import evaluate_phenotype_annotations
from benchmarks.drug_benchmark import evaluate_drug_annotations
from benchmarks.fa_benchmark import evaluate_functional_analysis

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File paths
PROMPTS_FILE = "stored_prompts.json"
BENCHMARK_OUTPUT_FILE = "benchmark_output.json"
OUTPUT_DIR = "outputs"
BENCHMARK_RESULTS_DIR = "benchmark_results"
GROUND_TRUTH_FILE = "persistent_data/benchmark_annotations.json"


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
            "output": parsed_output,
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
                "output": parsed_output,
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
    try:
        # Format prompt with annotation details
        formatted_prompt = citation_prompt_template.format(
            variant=annotation.get("Variant/Haplotypes", ""),
            gene=annotation.get("Gene", ""),
            drug=annotation.get("Drug(s)", annotation.get("Drug(s", "")),  # Handle typo
            sentence=annotation.get("Sentence", ""),
            notes=annotation.get("Notes", ""),
            full_text=full_text,
        )

        # Call LLM with JSON output format
        response = await generate_response(
            prompt=formatted_prompt,
            text="",
            model=model,
            response_format={
                "type": "object",
                "properties": {
                    "citations": {
                        "type": "array",
                        "items": {"type": "string"},
                    }
                },
                "required": ["citations"],
            },
        )

        # Parse and return citations
        citations_data = json.loads(response)
        return citations_data.get("citations", [])
    except Exception as e:
        print(f"Error generating citations: {e}")
        return []


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


class RunBenchmarksRequest(BaseModel):
    """Request to run benchmarks on best prompts."""
    text: str
    pmcid: str


@app.post("/run-benchmarks")
async def run_benchmarks(request: RunBenchmarksRequest):
    """
    Run benchmarks on the best prompts configuration.

    This endpoint:
    1. Loads best prompts configuration
    2. Runs each prompt to generate predictions
    3. Loads ground truth from persistent_data/benchmark_annotations.json
    4. Compares predictions to ground truth using benchmark modules
    5. Saves results to benchmark_results/{timestamp}.json
    """
    try:
        # Validate input
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Input text cannot be empty")

        if not request.pmcid or not request.pmcid.strip():
            raise HTTPException(status_code=400, detail="PMCID cannot be empty")

        # Load best prompts configuration
        best_prompts_file = "best_prompts.json"
        if not os.path.exists(best_prompts_file):
            raise HTTPException(status_code=404, detail="best_prompts.json not found")

        with open(best_prompts_file, "r") as f:
            best_prompts_config = json.load(f)

        # Load stored prompts to get full prompt details
        if not os.path.exists(PROMPTS_FILE):
            raise HTTPException(status_code=404, detail="stored_prompts.json not found")

        with open(PROMPTS_FILE, "r") as f:
            all_prompts = json.load(f)

        # Build map of task -> prompt details
        prompt_details_map = {}
        for task, prompt_name in best_prompts_config.items():
            # Find the prompt in stored prompts
            matching_prompts = [
                p for p in all_prompts
                if p["task"] == task and p["name"] == prompt_name
            ]
            if matching_prompts:
                prompt_details_map[task] = matching_prompts[0]
            else:
                print(f"Warning: Could not find prompt '{prompt_name}' for task '{task}'")

        # Run each prompt to generate predictions
        predictions = {}
        print(f"Running {len(prompt_details_map)} prompts...")

        for task, prompt_data in prompt_details_map.items():
            try:
                # Validate required fields
                if "prompt" not in prompt_data:
                    raise ValueError(f"Missing 'prompt' field in stored prompt for task '{task}'")

                # Get model with fallback to default
                model_str = prompt_data.get("model", "gpt-4o-mini")
                if not model_str:
                    model_str = "gpt-4o-mini"
                    print(f"  ⚠ No model specified for {task}, using default: {model_str}")

                # Convert string to Model enum
                try:
                    model = Model(model_str)
                except ValueError:
                    print(f"  ⚠ Unknown model '{model_str}' for {task}, using gpt-4o-mini")
                    model = Model.OPENAI_GPT_4O_MINI

                output = await generate_response(
                    prompt=prompt_data["prompt"],
                    text=request.text,
                    model=model,
                    response_format=prompt_data.get("response_format"),
                )

                # Parse output as JSON
                try:
                    parsed_output = json.loads(output)
                    predictions[task] = parsed_output
                except json.JSONDecodeError as e:
                    print(f"  ⚠ JSON parse error for {task}: {e}")
                    predictions[task] = {"error": f"JSON parse failed: {str(e)}"}

                print(f"✓ Completed task: {task}")
            except KeyError as e:
                print(f"✗ Task '{task}' failed: Missing required field {e}")
                predictions[task] = {"error": f"Missing required field: {str(e)}"}
            except Exception as e:
                print(f"✗ Task '{task}' failed: {e}")
                predictions[task] = {"error": str(e)}

        # Load ground truth
        if not os.path.exists(GROUND_TRUTH_FILE):
            raise HTTPException(
                status_code=404,
                detail=f"Ground truth file not found at {GROUND_TRUTH_FILE}"
            )

        with open(GROUND_TRUTH_FILE, "r") as f:
            ground_truth_data = json.load(f)

        # Get ground truth for this PMCID
        if request.pmcid not in ground_truth_data:
            raise HTTPException(
                status_code=404,
                detail=f"No ground truth found for PMCID: {request.pmcid}"
            )

        ground_truth = ground_truth_data[request.pmcid]

        # Debug logging: Show what's in predictions dict
        print(f"\n=== Predictions Summary ===")
        print(f"Total tasks predicted: {len(predictions)}")
        for task, pred in predictions.items():
            if isinstance(pred, dict):
                if "error" in pred:
                    print(f"  ✗ {task}: ERROR - {pred['error']}")
                else:
                    print(f"  ✓ {task}: dict with keys {list(pred.keys())[:5]}")
            elif isinstance(pred, list):
                print(f"  ✓ {task}: list with {len(pred)} items")
            else:
                print(f"  ? {task}: {type(pred).__name__}")
        print(f"=== End Predictions Summary ===\n")

        # Run benchmarks for each task
        benchmark_results = {}

        # Phenotype annotations
        if "var-pheno" in predictions:
            pred_pheno = predictions["var-pheno"]

            # Check for prompt errors first
            if isinstance(pred_pheno, dict) and "error" in pred_pheno:
                benchmark_results["var-pheno"] = {
                    "error": f"Prompt failed: {pred_pheno['error']}",
                    "overall_score": 0.0,
                    "total_samples": 0
                }
                print(f"✗ Phenotype benchmark skipped: prompt failed")
            elif "var_pheno_ann" not in ground_truth:
                benchmark_results["var-pheno"] = {
                    "error": "No ground truth available for this PMCID",
                    "overall_score": 0.0,
                    "total_samples": 0
                }
                print(f"✗ Phenotype benchmark skipped: no ground truth")
            else:
                gt_pheno = ground_truth["var_pheno_ann"]

                # Handle both dict and list formats
                pred_list = pred_pheno if isinstance(pred_pheno, list) else pred_pheno.get("var_pheno_ann", [])

                if not pred_list:
                    benchmark_results["var-pheno"] = {
                        "error": "Empty predictions list",
                        "overall_score": 0.0,
                        "total_samples": 0
                    }
                    print(f"✗ Phenotype benchmark skipped: empty predictions")
                elif not gt_pheno:
                    benchmark_results["var-pheno"] = {
                        "error": "Empty ground truth list",
                        "overall_score": 0.0,
                        "total_samples": 0
                    }
                    print(f"✗ Phenotype benchmark skipped: empty ground truth")
                else:
                    try:
                        # Phenotype benchmark accepts lists directly
                        score = evaluate_phenotype_annotations([gt_pheno, pred_list])
                        benchmark_results["var-pheno"] = {
                            "overall_score": score / 100.0,  # Convert to 0-1 scale
                            "raw_score": score,
                            "total_samples": len(pred_list)
                        }
                        print(f"✓ Phenotype benchmark score: {score}/100")
                    except Exception as e:
                        print(f"✗ Phenotype benchmark failed: {e}")
                        benchmark_results["var-pheno"] = {
                            "error": f"Evaluation failed: {str(e)}",
                            "overall_score": 0.0,
                            "total_samples": 0
                        }

        # Drug annotations
        if "var-drug" in predictions:
            pred_drug = predictions["var-drug"]

            # Check for prompt errors first
            if isinstance(pred_drug, dict) and "error" in pred_drug:
                benchmark_results["var-drug"] = {
                    "error": f"Prompt failed: {pred_drug['error']}",
                    "overall_score": 0.0,
                    "total_samples": 0
                }
                print(f"✗ Drug benchmark skipped: prompt failed")
            elif "var_drug_ann" not in ground_truth:
                benchmark_results["var-drug"] = {
                    "error": "No ground truth available for this PMCID",
                    "overall_score": 0.0,
                    "total_samples": 0
                }
                print(f"✗ Drug benchmark skipped: no ground truth")
            else:
                gt_drug = ground_truth["var_drug_ann"]

                # Handle both dict and list formats
                pred_list = pred_drug if isinstance(pred_drug, list) else pred_drug.get("var_drug_ann", [])

                if not pred_list:
                    benchmark_results["var-drug"] = {
                        "error": "Empty predictions list",
                        "overall_score": 0.0,
                        "total_samples": 0
                    }
                    print(f"✗ Drug benchmark skipped: empty predictions")
                elif not gt_drug:
                    benchmark_results["var-drug"] = {
                        "error": "Empty ground truth list",
                        "overall_score": 0.0,
                        "total_samples": 0
                    }
                    print(f"✗ Drug benchmark skipped: empty ground truth")
                else:
                    try:
                        # Wrap lists in dicts with proper keys for benchmark function
                        gt_dict = {"var_drug_ann": gt_drug}
                        pred_dict = {"var_drug_ann": pred_list}
                        result = evaluate_drug_annotations([gt_dict, pred_dict])
                        benchmark_results["var-drug"] = {
                            "overall_score": result.get("overall_score", 0.0),
                            "field_scores": result.get("field_scores", {}),
                            "total_samples": result.get("total_samples", len(pred_list))
                        }
                        print(f"✓ Drug benchmark score: {result.get('overall_score', 0)}")
                    except Exception as e:
                        print(f"✗ Drug benchmark failed: {e}")
                        benchmark_results["var-drug"] = {
                            "error": f"Evaluation failed: {str(e)}",
                            "overall_score": 0.0,
                            "total_samples": 0
                        }

        # Functional analysis annotations
        if "var-fa" in predictions:
            pred_fa = predictions["var-fa"]

            # Check for prompt errors first
            if isinstance(pred_fa, dict) and "error" in pred_fa:
                benchmark_results["var-fa"] = {
                    "error": f"Prompt failed: {pred_fa['error']}",
                    "overall_score": 0.0,
                    "total_samples": 0
                }
                print(f"✗ FA benchmark skipped: prompt failed")
            elif "var_fa_ann" not in ground_truth:
                benchmark_results["var-fa"] = {
                    "error": "No ground truth available for this PMCID",
                    "overall_score": 0.0,
                    "total_samples": 0
                }
                print(f"✗ FA benchmark skipped: no ground truth")
            else:
                gt_fa = ground_truth["var_fa_ann"]

                # Handle both dict and list formats
                pred_list = pred_fa if isinstance(pred_fa, list) else pred_fa.get("var_fa_ann", [])

                if not pred_list:
                    benchmark_results["var-fa"] = {
                        "error": "Empty predictions list",
                        "overall_score": 0.0,
                        "total_samples": 0
                    }
                    print(f"✗ FA benchmark skipped: empty predictions")
                elif not gt_fa:
                    benchmark_results["var-fa"] = {
                        "error": "Empty ground truth list",
                        "overall_score": 0.0,
                        "total_samples": 0
                    }
                    print(f"✗ FA benchmark skipped: empty ground truth")
                else:
                    try:
                        # Wrap lists in dicts with proper keys for benchmark function
                        gt_dict = {"var_fa_ann": gt_fa}
                        pred_dict = {"var_fa_ann": pred_list}
                        result = evaluate_functional_analysis([gt_dict, pred_dict])
                        benchmark_results["var-fa"] = {
                            "overall_score": result.get("overall_score", 0.0),
                            "field_scores": result.get("field_scores", {}),
                            "total_samples": result.get("total_samples", len(pred_list))
                        }
                        print(f"✓ FA benchmark score: {result.get('overall_score', 0)}")
                    except Exception as e:
                        print(f"✗ FA benchmark failed: {e}")
                        benchmark_results["var-fa"] = {
                            "error": f"Evaluation failed: {str(e)}",
                            "overall_score": 0.0,
                            "total_samples": 0
                        }

        # Calculate average score (excluding tasks with errors)
        valid_scores = [
            r["overall_score"] for r in benchmark_results.values()
            if "overall_score" in r and "error" not in r
        ]
        average_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0

        print(f"\n=== Benchmark Summary ===")
        print(f"Total tasks: {len(benchmark_results)}")
        print(f"Successful: {len(valid_scores)}")
        print(f"Failed/Skipped: {len(benchmark_results) - len(valid_scores)}")
        print(f"Average score: {average_score:.2%}")
        print(f"=========================\n")

        # Create benchmark result document
        timestamp = datetime.now().isoformat()
        benchmark_result = {
            "timestamp": timestamp,
            "pmcid": request.pmcid,
            "prompts_used": best_prompts_config,
            "results": benchmark_results,
            "metadata": {
                "ground_truth_file": GROUND_TRUTH_FILE,
                "total_tasks": len(benchmark_results),
                "average_score": average_score,
                "tasks_with_errors": sum(1 for r in benchmark_results.values() if "error" in r)
            }
        }

        # Save to benchmark_results directory
        os.makedirs(BENCHMARK_RESULTS_DIR, exist_ok=True)
        filename = f"{BENCHMARK_RESULTS_DIR}/benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, "w") as f:
            json.dump(benchmark_result, f, indent=2)

        print(f"✓ Benchmark results saved to {filename}")
        print(f"Average score: {average_score:.2%}")

        return {
            "status": "success",
            "message": "Benchmarks completed successfully",
            "filename": filename,
            "results": benchmark_result
        }

    except Exception as e:
        print(f"Benchmark error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/benchmark-results")
async def list_benchmark_results():
    """List all benchmark result files."""
    try:
        if not os.path.exists(BENCHMARK_RESULTS_DIR):
            return {"files": []}

        files = []
        for filename in os.listdir(BENCHMARK_RESULTS_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(BENCHMARK_RESULTS_DIR, filename)

                # Read file to get metadata
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)

                    files.append({
                        "filename": filename,
                        "timestamp": data.get("timestamp"),
                        "pmcid": data.get("pmcid"),
                        "average_score": data.get("metadata", {}).get("average_score", 0),
                        "total_tasks": data.get("metadata", {}).get("total_tasks", 0),
                        "prompts_used": data.get("prompts_used", {})
                    })
                except:
                    # If file can't be read, just include basic info
                    stat = os.stat(filepath)
                    files.append({
                        "filename": filename,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })

        # Sort by timestamp, newest first
        files.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return {"files": files}

    except Exception as e:
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
