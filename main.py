from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm import Model, generate_response
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

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
