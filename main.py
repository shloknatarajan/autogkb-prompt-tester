from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm import Model, generate_response
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple
from benchmarks.fa_benchmark import evaluate_functional_analysis, expand_annotations_by_variant, normalize_variant

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
BENCHMARK_ANNOTATIONS_FILE = "persistent_data/benchmark_annotations.json"
BENCHMARK_RESULTS_DIR = "benchmark_results"
BENCHMARK_HISTORY_FILE = f"{BENCHMARK_RESULTS_DIR}/history.json"


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


class RunBenchmarkRequest(BaseModel):
    pmcid: str
    predictions: Dict[str, Any]  # Full output with var_fa_ann


class BenchmarkWithPromptsRequest(BaseModel):
    pmcid: str
    text: str  # Article text
    prompts: List[Dict[str, Any]]  # List of prompts to run
    citation_prompt: str | None = None


def align_annotations_for_evaluation(
    gt_annotations: List[Dict[str, Any]],
    pred_annotations: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Align ground truth and prediction annotations.
    Since LLM predictions may use different variant nomenclature (rsID vs HGVS vs star alleles),
    we use a permissive matching strategy and rely on the evaluation function's
    variant_coverage scoring to handle nomenclature differences.

    Strategy: Match by gene only, then use a greedy pairing algorithm.
    The evaluation function will then properly score variant similarity.

    Returns:
        Tuple of (aligned_gt, aligned_pred) with equal lengths
    """
    # Don't expand yet - match at annotation level first
    print(f"Alignment: GT has {len(gt_annotations)} annotations, Pred has {len(pred_annotations)} annotations")

    # Group by gene
    def group_by_gene(annotations: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        groups = {}
        for ann in annotations:
            gene = ann.get("Gene", "")
            gene_norm = gene.strip().upper() if gene else "UNKNOWN"
            if gene_norm not in groups:
                groups[gene_norm] = []
            groups[gene_norm].append(ann)
        return groups

    gt_by_gene = group_by_gene(gt_annotations)
    pred_by_gene = group_by_gene(pred_annotations)

    print(f"GT genes: {list(gt_by_gene.keys())}")
    print(f"Pred genes: {list(pred_by_gene.keys())}")

    # For each gene, pair GT and Pred annotations
    aligned_gt = []
    aligned_pred = []

    for gene, gt_anns in gt_by_gene.items():
        pred_anns = pred_by_gene.get(gene, [])

        if not pred_anns:
            print(f"Warning: No predictions found for gene {gene} (GT has {len(gt_anns)} annotations)")
            continue

        # Greedy pairing: pair each GT annotation with a pred annotation
        # Use simple strategy: pair in order
        num_pairs = min(len(gt_anns), len(pred_anns))

        for i in range(num_pairs):
            aligned_gt.append(gt_anns[i])
            aligned_pred.append(pred_anns[i])

        if len(gt_anns) != len(pred_anns):
            print(f"Note: For gene {gene}, GT has {len(gt_anns)} annotations but Pred has {len(pred_anns)} annotations. Using {num_pairs} pairs.")

    print(f"Matched {len(aligned_gt)} annotation pairs")

    if len(aligned_gt) == 0:
        print("No matches found! Genes don't match between GT and predictions.")
    else:
        print(f"Example GT variant: {aligned_gt[0].get('Variant/Haplotypes', 'N/A')}")
        print(f"Example Pred variant: {aligned_pred[0].get('Variant/Haplotypes', 'N/A')}")

    # Normalize field names and handle None values
    def normalize_annotation(ann: Dict[str, Any]) -> Dict[str, Any]:
        """Fix common field name issues and convert None to empty string."""
        normalized = {}
        for key, value in ann.items():
            # Fix typo in field name
            if key == "Comparison Allele(s) or Genotype(s":
                key = "Comparison Allele(s) or Genotype(s)"

            # Convert None to empty string to prevent subscript errors
            if value is None:
                value = ""

            normalized[key] = value
        return normalized

    aligned_gt = [normalize_annotation(ann) for ann in aligned_gt]
    aligned_pred = [normalize_annotation(ann) for ann in aligned_pred]

    return aligned_gt, aligned_pred


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


@app.get("/benchmark-articles")
async def get_benchmark_articles():
    """Get list of available benchmark articles (PMCIDs) from benchmark_annotations.json."""
    try:
        if not os.path.exists(BENCHMARK_ANNOTATIONS_FILE):
            return {"articles": []}

        with open(BENCHMARK_ANNOTATIONS_FILE, "r") as f:
            benchmark_data = json.load(f)

        articles = []
        for pmcid, data in benchmark_data.items():
            # Count annotations
            var_fa_count = len(data.get("var_fa_ann", []))
            var_pheno_count = len(data.get("var_pheno_ann", []))
            var_drug_count = len(data.get("var_drug_ann", []))

            articles.append({
                "pmcid": pmcid,
                "title": data.get("title", "Unknown"),
                "pmid": data.get("pmid", ""),
                "annotation_counts": {
                    "var_fa_ann": var_fa_count,
                    "var_pheno_ann": var_pheno_count,
                    "var_drug_ann": var_drug_count,
                },
            })

        return {"articles": articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run-benchmark")
async def run_benchmark(request: RunBenchmarkRequest):
    """Evaluate predictions against ground truth for a specific PMCID."""
    try:
        # Load ground truth
        if not os.path.exists(BENCHMARK_ANNOTATIONS_FILE):
            raise HTTPException(
                status_code=404, detail="Benchmark annotations file not found"
            )

        with open(BENCHMARK_ANNOTATIONS_FILE, "r") as f:
            ground_truth_data = json.load(f)

        # Get ground truth for this PMCID
        if request.pmcid not in ground_truth_data:
            raise HTTPException(
                status_code=404,
                detail=f"PMCID {request.pmcid} not found in benchmark data",
            )

        gt_article = ground_truth_data[request.pmcid]
        gt_var_fa = gt_article.get("var_fa_ann", [])

        if not gt_var_fa:
            raise HTTPException(
                status_code=400,
                detail=f"No var_fa_ann annotations in ground truth for {request.pmcid}",
            )

        # Get predictions
        pred_var_fa = request.predictions.get("var_fa_ann", [])

        if not pred_var_fa:
            raise HTTPException(
                status_code=400,
                detail="No var_fa_ann annotations in predictions",
            )

        # Debug logging
        print(f"Ground truth count: {len(gt_var_fa)}")
        print(f"Predictions count: {len(pred_var_fa)}")
        print(f"Ground truth first item keys: {list(gt_var_fa[0].keys()) if gt_var_fa else 'empty'}")
        print(f"Predictions first item keys: {list(pred_var_fa[0].keys()) if pred_var_fa else 'empty'}")

        # Align annotations by Variant Annotation ID
        aligned_gt, aligned_pred = align_annotations_for_evaluation(gt_var_fa, pred_var_fa)

        if not aligned_gt or not aligned_pred:
            raise HTTPException(
                status_code=400,
                detail=f"No matching annotations found. GT has {len(gt_var_fa)} annotations, predictions have {len(pred_var_fa)} annotations, but none matched by Variant Annotation ID."
            )

        # Run evaluation
        try:
            # Print first annotation pair for debugging
            if aligned_gt and aligned_pred:
                print("\nFirst GT annotation:")
                for key, value in aligned_gt[0].items():
                    print(f"  {key}: {repr(value)[:100]}")
                print("\nFirst Pred annotation:")
                for key, value in aligned_pred[0].items():
                    print(f"  {key}: {repr(value)[:100]}")

            results = evaluate_functional_analysis(aligned_gt, aligned_pred)
        except Exception as e:
            print(f"\n!!! Error in evaluate_functional_analysis: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Evaluation failed: {str(e)}"
            )

        # Save results
        os.makedirs(BENCHMARK_RESULTS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_filename = f"{BENCHMARK_RESULTS_DIR}/{timestamp}_{request.pmcid}_eval.json"

        result_data = {
            "timestamp": datetime.now().isoformat(),
            "pmcid": request.pmcid,
            "evaluation_results": results,
            "ground_truth_count": len(gt_var_fa),
            "predictions_count": len(pred_var_fa),
        }

        with open(result_filename, "w") as f:
            json.dump(result_data, f, indent=2)

        # Update history
        history = []
        if os.path.exists(BENCHMARK_HISTORY_FILE):
            with open(BENCHMARK_HISTORY_FILE, "r") as f:
                history = json.load(f)

        history.append({
            "timestamp": datetime.now().isoformat(),
            "pmcid": request.pmcid,
            "overall_score": results["overall_score"],
            "result_file": result_filename,
        })

        with open(BENCHMARK_HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)

        return {
            "status": "success",
            "pmcid": request.pmcid,
            "results": results,
            "result_file": result_filename,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/benchmark-history")
async def get_benchmark_history():
    """Get historical benchmark results."""
    try:
        if not os.path.exists(BENCHMARK_HISTORY_FILE):
            return {"history": []}

        with open(BENCHMARK_HISTORY_FILE, "r") as f:
            history = json.load(f)

        # Sort by timestamp, newest first
        history.sort(key=lambda x: x["timestamp"], reverse=True)

        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/benchmark-with-prompts")
async def benchmark_with_prompts(request: BenchmarkWithPromptsRequest):
    """Run prompts on benchmark article text and evaluate against ground truth."""
    try:
        # Load ground truth
        if not os.path.exists(BENCHMARK_ANNOTATIONS_FILE):
            raise HTTPException(
                status_code=404, detail="Benchmark annotations file not found"
            )

        with open(BENCHMARK_ANNOTATIONS_FILE, "r") as f:
            ground_truth_data = json.load(f)

        # Get ground truth for this PMCID
        if request.pmcid not in ground_truth_data:
            raise HTTPException(
                status_code=404,
                detail=f"PMCID {request.pmcid} not found in benchmark data",
            )

        gt_article = ground_truth_data[request.pmcid]
        gt_var_fa = gt_article.get("var_fa_ann", [])

        if not gt_var_fa:
            raise HTTPException(
                status_code=400,
                detail=f"No var_fa_ann annotations in ground truth for {request.pmcid}",
            )

        # Run prompts to generate predictions
        predictions = {}
        prompts_used = {}

        for prompt_config in request.prompts:
            task = prompt_config.get("task")
            prompt = prompt_config.get("prompt")
            model = prompt_config.get("model", "gpt-4o-mini")
            response_format = prompt_config.get("response_format")
            name = prompt_config.get("name", "unnamed")

            print(f"Running prompt for task: {task}")

            try:
                output = await generate_response(
                    prompt=prompt,
                    text=request.text,
                    model=model,
                    response_format=response_format,
                )

                # Parse output
                try:
                    parsed_output = json.loads(output)
                except:
                    parsed_output = {task: output}

                # Store in predictions
                if task in parsed_output:
                    predictions[task] = parsed_output[task]
                else:
                    predictions[task] = parsed_output

                prompts_used[task] = name

            except Exception as e:
                print(f"Error running prompt for {task}: {e}")
                predictions[task] = []

        # Get var_fa_ann from predictions
        pred_var_fa = predictions.get("var_fa_ann", [])

        if not pred_var_fa:
            raise HTTPException(
                status_code=400,
                detail="No var_fa_ann annotations generated by prompts",
            )

        # Align annotations by Variant Annotation ID
        aligned_gt, aligned_pred = align_annotations_for_evaluation(gt_var_fa, pred_var_fa)

        if not aligned_gt or not aligned_pred:
            raise HTTPException(
                status_code=400,
                detail=f"No matching annotations found. GT has {len(gt_var_fa)} annotations, predictions have {len(pred_var_fa)} annotations, but none matched by Variant Annotation ID."
            )

        # Run evaluation
        results = evaluate_functional_analysis(aligned_gt, aligned_pred)

        # Save results
        os.makedirs(BENCHMARK_RESULTS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_names = "_".join([p.get("name", "unnamed")[:10] for p in request.prompts])
        result_filename = f"{BENCHMARK_RESULTS_DIR}/{timestamp}_{request.pmcid}_{prompt_names}.json"

        result_data = {
            "timestamp": datetime.now().isoformat(),
            "pmcid": request.pmcid,
            "prompts_used": prompts_used,
            "evaluation_results": results,
            "ground_truth_count": len(gt_var_fa),
            "predictions_count": len(pred_var_fa),
            "predictions": predictions,
        }

        with open(result_filename, "w") as f:
            json.dump(result_data, f, indent=2)

        # Update history
        history = []
        if os.path.exists(BENCHMARK_HISTORY_FILE):
            with open(BENCHMARK_HISTORY_FILE, "r") as f:
                history = json.load(f)

        history.append({
            "timestamp": datetime.now().isoformat(),
            "pmcid": request.pmcid,
            "prompts_used": prompts_used,
            "overall_score": results["overall_score"],
            "result_file": result_filename,
        })

        with open(BENCHMARK_HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)

        return {
            "status": "success",
            "pmcid": request.pmcid,
            "results": results,
            "predictions": predictions,
            "result_file": result_filename,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
