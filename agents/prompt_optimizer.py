"""
Autonomous Prompt Optimization Agent using Claude SDK.

This agent analyzes benchmark results, identifies prompt weaknesses,
generates improved prompts, and verifies improvements through benchmarking.
"""

import asyncio
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from anthropic import Anthropic

# Add parent directory to path to import project modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.benchmark_runner import BenchmarkRunner
from utils.prompt_manager import PromptManager
from utils.config import (
    BENCHMARK_RESULTS_DIR,
    PROMPTS_DIR,
    GROUND_TRUTH_NORMALIZED_FILE,
    GROUND_TRUTH_FILE,
)


@dataclass
class OptimizationConfig:
    """Configuration for the optimization agent."""

    # Target task to optimize (or "auto" to pick lowest scoring)
    target_task: str = "auto"

    # Target score improvement threshold (stop when reached)
    target_score: float = 0.90

    # Maximum optimization iterations
    max_iterations: int = 5

    # Minimum score improvement per iteration to continue
    min_improvement: float = 0.01

    # Model for quick iteration benchmarks
    quick_model: str = "openai/gpt-5-mini"

    # Model for validation benchmarks
    validation_model: str = "openai/gpt-5.2"

    # Threshold for triggering validation (improvement on quick model)
    validation_threshold: float = 0.03

    # Number of test PMCIDs to evaluate (for faster iteration)
    sample_pmcids: int = 5

    # Full benchmark on final prompt
    full_benchmark_on_final: bool = True

    # Working directory for the agent
    cwd: Path = field(default_factory=lambda: Path("."))

    # Log file path
    log_file: Path = field(default_factory=lambda: Path("logs/optimization_log.jsonl"))


@dataclass
class OptimizationResult:
    """Result of an optimization run."""

    task: str
    initial_score: float
    final_score: float
    iterations: int
    prompt_versions: List[str]
    score_history: List[float]
    changelogs: List[Dict[str, Any]]
    success: bool
    error: Optional[str] = None


# Tool definitions for the agent
TOOLS = [
    {
        "name": "analyze_benchmark",
        "description": "Analyze benchmark results to identify worst-performing articles and fields. Returns detailed statistics about which PMCIDs and fields have the lowest scores, common mismatch patterns, and dependency issues.",
        "input_schema": {
            "type": "object",
            "properties": {
                "results_file": {
                    "type": "string",
                    "description": "Path to benchmark results JSON file (e.g., 'benchmark_results/pipeline_benchmark_20251216_113624.json')",
                },
                "task": {
                    "type": "string",
                    "description": "Task to analyze (var-pheno, var-drug, var-fa, study-parameters)",
                },
            },
            "required": ["results_file", "task"],
        },
    },
    {
        "name": "write_analysis",
        "description": "Document analysis findings to a markdown file for audit trail. Should be called after analyze_benchmark to record hypotheses and recommended changes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Task being analyzed",
                },
                "iteration": {
                    "type": "integer",
                    "description": "Current iteration number",
                },
                "current_score": {
                    "type": "number",
                    "description": "Current benchmark score",
                },
                "analysis_content": {
                    "type": "string",
                    "description": "Full markdown content for the analysis document",
                },
            },
            "required": ["task", "iteration", "current_score", "analysis_content"],
        },
    },
    {
        "name": "read_prompt",
        "description": "Read an existing prompt's content, schema, and config from the prompts folder.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Task name (var-pheno, var-drug, var-fa, study-parameters, summary)",
                },
                "name": {
                    "type": "string",
                    "description": "Prompt name (e.g., 'var-pheno-v6', 'improved_v2')",
                },
            },
            "required": ["task", "name"],
        },
    },
    {
        "name": "write_prompt",
        "description": "Write a new prompt version to the prompts folder. Creates prompt.md, schema.json, config.json, and changelog.md.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Task name",
                },
                "name": {
                    "type": "string",
                    "description": "New prompt name (e.g., 'var-pheno-v7')",
                },
                "prompt": {
                    "type": "string",
                    "description": "Full prompt markdown content",
                },
                "schema": {
                    "type": "object",
                    "description": "JSON schema for response format (copy from previous version)",
                },
                "model": {
                    "type": "string",
                    "description": "Model name (default: gpt-4o-mini)",
                },
                "temperature": {
                    "type": "number",
                    "description": "Temperature setting (default: 0.0)",
                },
                "changelog": {
                    "type": "object",
                    "description": "Changelog entry with keys: changes, issues_addressed, expected_improvements, previous_version, previous_score, target_score, fields_targeted",
                },
            },
            "required": ["task", "name", "prompt", "schema", "changelog"],
        },
    },
    {
        "name": "run_benchmark",
        "description": "Run benchmark on a specific prompt version. Uses batch processing to generate outputs and then benchmarks against ground truth.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Task to benchmark",
                },
                "prompt_name": {
                    "type": "string",
                    "description": "Prompt name to use",
                },
                "sample_pmcids": {
                    "type": "integer",
                    "description": "Number of PMCIDs to test (0 = all). Default: 5 for quick iteration.",
                },
                "model": {
                    "type": "string",
                    "description": "Model for inference (e.g., 'openai/gpt-4o-mini')",
                },
            },
            "required": ["task", "prompt_name"],
        },
    },
    {
        "name": "read_ground_truth",
        "description": "Read ground truth annotations for a specific PMCID and task to understand expected output format.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pmcid": {
                    "type": "string",
                    "description": "PMCID to read (e.g., 'PMC3548984')",
                },
                "task": {
                    "type": "string",
                    "description": "Task type (var-pheno, var-drug, var-fa, study-parameters)",
                },
            },
            "required": ["pmcid", "task"],
        },
    },
    {
        "name": "list_prompts",
        "description": "List all available prompts for a task, showing which one is currently marked as best.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Task name to list prompts for",
                },
            },
            "required": ["task"],
        },
    },
    {
        "name": "read_article",
        "description": "Read a benchmark article markdown file to understand its content and structure.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pmcid": {
                    "type": "string",
                    "description": "PMCID to read (e.g., 'PMC3548984')",
                },
            },
            "required": ["pmcid"],
        },
    },
    {
        "name": "update_best_prompt",
        "description": "Update best_prompts.json to use a new prompt as the default for a task.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Task to update",
                },
                "name": {
                    "type": "string",
                    "description": "New best prompt name",
                },
            },
            "required": ["task", "name"],
        },
    },
    {
        "name": "list_benchmark_results",
        "description": "List available benchmark result files to find the most recent one.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 10)",
                },
            },
        },
    },
]


class PromptOptimizationAgent:
    """
    Autonomous agent for optimizing pharmacogenomics extraction prompts.

    Uses Claude with tool calling to iteratively improve prompts based on
    benchmark analysis.
    """

    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.client = Anthropic()
        self.prompt_manager = PromptManager()
        self.benchmark_runner = BenchmarkRunner()

        # Ensure log directory exists
        self.config.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Conversation history for the agent
        self.messages: List[Dict] = []

        # State tracking
        self.optimization_log: List[Dict] = []
        self.current_iteration = 0

    def _log_event(self, event: str, data: Dict[str, Any]) -> None:
        """Log an event to the JSONL log file."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            **data,
        }
        self.optimization_log.append(entry)

        with open(self.config.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def _execute_tool(self, tool_name: str, tool_input: Dict) -> str:
        """Execute a tool and return the result as a string."""
        try:
            if tool_name == "analyze_benchmark":
                return self._analyze_benchmark(tool_input)
            elif tool_name == "write_analysis":
                return self._write_analysis(tool_input)
            elif tool_name == "read_prompt":
                return self._read_prompt(tool_input)
            elif tool_name == "write_prompt":
                return self._write_prompt(tool_input)
            elif tool_name == "run_benchmark":
                return self._run_benchmark(tool_input)
            elif tool_name == "read_ground_truth":
                return self._read_ground_truth(tool_input)
            elif tool_name == "list_prompts":
                return self._list_prompts(tool_input)
            elif tool_name == "read_article":
                return self._read_article(tool_input)
            elif tool_name == "update_best_prompt":
                return self._update_best_prompt(tool_input)
            elif tool_name == "list_benchmark_results":
                return self._list_benchmark_results(tool_input)
            else:
                return json.dumps({"error": f"Unknown tool: {tool_name}"})
        except Exception as e:
            return json.dumps({"error": f"Tool execution failed: {str(e)}"})

    def _analyze_benchmark(self, args: Dict) -> str:
        """Analyze benchmark results to identify patterns of failure."""
        results_file = Path(args["results_file"])
        task = args["task"]

        if not results_file.exists():
            return json.dumps({"error": f"Results file not found: {results_file}"})

        with open(results_file) as f:
            results = json.load(f)

        pmcid_results = results.get("pmcid_results", {})

        # Collect per-PMCID scores for this task
        pmcid_scores = []
        field_scores_agg: Dict[str, List[float]] = {}
        all_field_values = []
        unmatched_count = 0
        dependency_issues_count = 0

        for pmcid, task_results in pmcid_results.items():
            if task not in task_results:
                continue

            task_data = task_results[task]
            score = task_data.get("overall_score", 0)
            pmcid_scores.append({"pmcid": pmcid, "score": score})

            # Aggregate field scores
            for field_name, field_data in task_data.get("field_scores", {}).items():
                if field_name not in field_scores_agg:
                    field_scores_agg[field_name] = []
                field_scores_agg[field_name].append(field_data.get("mean_score", 0))

            # Collect field values for pattern analysis
            for detail in task_data.get("detailed_results", []):
                all_field_values.append(detail.get("field_values", {}))
                if detail.get("dependency_issues"):
                    dependency_issues_count += 1

            # Count unmatched ground truth
            unmatched_count += len(task_data.get("unmatched_ground_truth", []))

        # Sort and find worst PMCIDs
        pmcid_scores.sort(key=lambda x: x["score"])
        worst_pmcids = pmcid_scores[:5]

        # Calculate average field scores and find worst
        field_averages = {
            field: sum(scores) / len(scores)
            for field, scores in field_scores_agg.items()
            if scores
        }
        worst_fields = sorted(field_averages.items(), key=lambda x: x[1])[:5]

        # Analyze common mismatches in field values
        mismatch_patterns = self._analyze_mismatch_patterns(all_field_values)

        return json.dumps(
            {
                "task": task,
                "overall_average": results.get("summary", {})
                .get("scores", {})
                .get(task, 0),
                "worst_pmcids": worst_pmcids,
                "worst_fields": [{"field": f, "score": s} for f, s in worst_fields],
                "common_mismatches": mismatch_patterns,
                "unmatched_ground_truth_total": unmatched_count,
                "dependency_issues_total": dependency_issues_count,
                "total_pmcids_analyzed": len(pmcid_scores),
            },
            indent=2,
        )

    def _analyze_mismatch_patterns(
        self, field_values: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Identify common mismatch patterns across samples."""
        patterns: Dict[str, Dict] = {}

        for sample in field_values:
            for field_name, values in sample.items():
                if not isinstance(values, dict):
                    continue
                gt = str(values.get("ground_truth", ""))
                pred = str(values.get("prediction", ""))

                if gt != pred and gt and pred:
                    # Create a pattern key (truncated for grouping)
                    pattern_key = f"{field_name}|{gt[:50]}|{pred[:50]}"
                    if pattern_key not in patterns:
                        patterns[pattern_key] = {
                            "field": field_name,
                            "ground_truth": gt[:100],
                            "prediction": pred[:100],
                            "count": 0,
                        }
                    patterns[pattern_key]["count"] += 1

        # Return top 10 most common mismatches
        sorted_patterns = sorted(
            patterns.values(), key=lambda x: x["count"], reverse=True
        )
        return sorted_patterns[:10]

    def _write_analysis(self, args: Dict) -> str:
        """Write analysis document to markdown file."""
        task = args["task"]
        iteration = args["iteration"]
        current_score = args["current_score"]
        analysis_content = args["analysis_content"]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{task}_{timestamp}.md"
        filepath = Path("logs") / filename

        # Ensure logs directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Write the analysis document
        filepath.write_text(analysis_content)

        self._log_event(
            "analysis_documented",
            {
                "task": task,
                "iteration": iteration,
                "current_score": current_score,
                "filepath": str(filepath),
            },
        )

        return json.dumps(
            {
                "success": True,
                "filepath": str(filepath),
                "message": f"Analysis document saved to {filepath}",
            }
        )

    def _read_prompt(self, args: Dict) -> str:
        """Read prompt files from the prompts directory."""
        task = args["task"]
        name = args["name"]

        prompt_data = self.prompt_manager.get_prompt_by_task_and_name(task, name)

        if not prompt_data:
            return json.dumps({"error": f"Prompt not found: {task}/{name}"})

        return json.dumps(
            {
                "task": prompt_data["task"],
                "name": prompt_data["name"],
                "prompt": prompt_data["prompt"],
                "schema": prompt_data.get("response_format", {}),
                "model": prompt_data.get("model", "gpt-4o-mini"),
                "temperature": prompt_data.get("temperature", 0.0),
            },
            indent=2,
        )

    def _write_prompt(self, args: Dict) -> str:
        """Write a new prompt to the prompts directory with changelog."""
        task = args["task"]
        name = args["name"]
        prompt = args["prompt"]
        schema = args["schema"]
        model = args.get("model", "gpt-4o-mini")
        temperature = args.get("temperature", 0.0)
        changelog = args["changelog"]

        # Save prompt using PromptManager
        self.prompt_manager.save_prompt(
            task=task,
            name=name,
            prompt=prompt,
            response_format=schema,
            model=model,
            temperature=temperature,
        )

        # Write changelog
        safe_name = self.prompt_manager._sanitize_name(name)
        changelog_path = Path(PROMPTS_DIR) / task / safe_name / "changelog.md"

        changelog_content = f"""# Changelog for {name}

## {datetime.now().strftime("%Y-%m-%d %H:%M")}

### Changes Made
{changelog.get('changes', 'No changes specified')}

### Issues Addressed
{changelog.get('issues_addressed', 'No specific issues')}

### Expected Improvements
{changelog.get('expected_improvements', 'No specific improvements expected')}

### Previous Version
{changelog.get('previous_version', 'Unknown')}

### Benchmark Context
- Previous Score: {changelog.get('previous_score', 'N/A')}
- Target Score: {changelog.get('target_score', 'N/A')}
- Fields Targeted: {', '.join(changelog.get('fields_targeted', []))}
"""

        changelog_path.write_text(changelog_content)

        self._log_event(
            "prompt_created",
            {
                "task": task,
                "name": name,
                "changes": changelog.get("changes", ""),
                "previous_version": changelog.get("previous_version", ""),
            },
        )

        return json.dumps(
            {
                "success": True,
                "message": f"Successfully wrote prompt {task}/{name} with changelog",
                "prompt_path": str(Path(PROMPTS_DIR) / task / safe_name),
            }
        )

    def _run_benchmark(self, args: Dict) -> str:
        """Run benchmark by processing articles and evaluating against ground truth."""
        task = args["task"]
        prompt_name = args["prompt_name"]
        sample_pmcids = args.get("sample_pmcids", 5)
        model = args.get("model", self.config.quick_model)

        # Create temporary output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"outputs/optimization_test_{timestamp}")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get sample PMCIDs
        all_pmcids = self.benchmark_runner.get_pmcids()
        if sample_pmcids > 0:
            test_pmcids = all_pmcids[:sample_pmcids]
        else:
            test_pmcids = all_pmcids

        # Create a temporary best_prompts.json for this test
        current_best = self.prompt_manager.load_best_config()
        test_best = current_best.copy()
        test_best[task] = prompt_name

        temp_best_file = output_dir / "test_best_prompts.json"
        with open(temp_best_file, "w") as f:
            json.dump(test_best, f, indent=2)

        # Create temp data directory with symlinks to test articles
        temp_data_dir = output_dir / "test_articles"
        temp_data_dir.mkdir(exist_ok=True)

        for pmcid in test_pmcids:
            src = Path(f"persistent_data/benchmark_articles_md/{pmcid}.md")
            if src.exists():
                dst = temp_data_dir / f"{pmcid}.md"
                if not dst.exists():
                    dst.symlink_to(src.resolve())

        # Run batch process using subprocess
        cmd = [
            sys.executable,
            "scripts/batch_process.py",
            "--data-dir",
            str(temp_data_dir),
            "--best-prompts",
            str(temp_best_file),
            "--output-dir",
            str(output_dir),
            "--model",
            model,
            "--concurrency",
            "3",
        ]

        print(f"Running benchmark with command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            return json.dumps(
                {
                    "error": f"Batch processing failed",
                    "stderr": result.stderr[:1000],
                    "stdout": result.stdout[:1000],
                }
            )

        # Load and benchmark outputs
        benchmark_results = {}
        task_scores = []

        for pmcid in test_pmcids:
            output_file = output_dir / f"{pmcid}.json"
            if not output_file.exists():
                continue

            with open(output_file) as f:
                predictions = json.load(f)

            try:
                benchmark_result = self.benchmark_runner.benchmark_pmcid(
                    pmcid, predictions, verbose=False
                )
                if task in benchmark_result:
                    benchmark_results[pmcid] = {
                        "overall_score": benchmark_result[task].get("overall_score", 0),
                        "field_scores": {
                            k: v.get("mean_score", 0)
                            for k, v in benchmark_result[task]
                            .get("field_scores", {})
                            .items()
                        },
                    }
                    task_scores.append(benchmark_result[task].get("overall_score", 0))
            except Exception as e:
                benchmark_results[pmcid] = {"error": str(e)}

        avg_score = sum(task_scores) / len(task_scores) if task_scores else 0

        self._log_event(
            "benchmark_complete",
            {
                "task": task,
                "prompt": prompt_name,
                "score": avg_score,
                "pmcids_tested": len(test_pmcids),
                "model": model,
            },
        )

        return json.dumps(
            {
                "task": task,
                "prompt_name": prompt_name,
                "model": model,
                "pmcids_tested": len(test_pmcids),
                "average_score": avg_score,
                "per_pmcid_scores": {
                    pmcid: r.get("overall_score", 0) if isinstance(r, dict) else 0
                    for pmcid, r in benchmark_results.items()
                },
                "output_directory": str(output_dir),
            },
            indent=2,
        )

    def _read_ground_truth(self, args: Dict) -> str:
        """Read ground truth annotations for analysis."""
        pmcid = args["pmcid"]
        task = args["task"]

        # Map task to annotation key
        task_to_key = {
            "var-pheno": "var_pheno_ann",
            "var-drug": "var_drug_ann",
            "var-fa": "var_fa_ann",
            "study-parameters": "study_parameters",
        }

        ann_key = task_to_key.get(task)
        if not ann_key:
            return json.dumps({"error": f"Unknown task: {task}"})

        # Load ground truth
        gt_file = (
            GROUND_TRUTH_NORMALIZED_FILE
            if Path(GROUND_TRUTH_NORMALIZED_FILE).exists()
            else GROUND_TRUTH_FILE
        )

        with open(gt_file) as f:
            ground_truth = json.load(f)

        if pmcid not in ground_truth:
            return json.dumps({"error": f"PMCID not found: {pmcid}"})

        annotations = ground_truth[pmcid].get(ann_key, [])

        return json.dumps(
            {
                "pmcid": pmcid,
                "task": task,
                "annotation_count": len(annotations),
                "annotations": annotations[:3],  # Return sample (first 3)
                "all_fields": list(annotations[0].keys()) if annotations else [],
            },
            indent=2,
        )

    def _list_prompts(self, args: Dict) -> str:
        """List all prompts for a given task."""
        task = args["task"]

        prompts = self.prompt_manager.get_prompts_by_task(task)
        best_config = self.prompt_manager.load_best_config()
        best_name = best_config.get(task)

        prompt_list = [
            {
                "name": p["name"],
                "is_best": p["name"] == best_name,
                "model": p.get("model", "unknown"),
                "timestamp": p.get("timestamp", "unknown"),
            }
            for p in prompts
        ]

        return json.dumps(
            {
                "task": task,
                "prompt_count": len(prompt_list),
                "prompts": prompt_list,
                "current_best": best_name,
            },
            indent=2,
        )

    def _read_article(self, args: Dict) -> str:
        """Read article markdown for analysis."""
        pmcid = args["pmcid"]

        article_path = Path(f"persistent_data/benchmark_articles_md/{pmcid}.md")

        if not article_path.exists():
            return json.dumps({"error": f"Article not found: {pmcid}"})

        content = article_path.read_text()

        # Return truncated content if too long
        max_chars = 50000
        if len(content) > max_chars:
            content = content[:max_chars] + "\n\n[TRUNCATED...]"

        return content

    def _update_best_prompt(self, args: Dict) -> str:
        """Update best_prompts.json with new best prompt."""
        task = args["task"]
        name = args["name"]

        # Verify prompt exists
        prompt = self.prompt_manager.get_prompt_by_task_and_name(task, name)
        if not prompt:
            return json.dumps({"error": f"Prompt {task}/{name} does not exist"})

        # Update best prompts
        best_config = self.prompt_manager.load_best_config()
        old_best = best_config.get(task)
        best_config[task] = name

        success = self.prompt_manager.update_best_prompts(best_config)

        self._log_event(
            "best_prompt_updated",
            {"task": task, "old_best": old_best, "new_best": name},
        )

        return json.dumps(
            {
                "success": success,
                "task": task,
                "old_best": old_best,
                "new_best": name,
            },
            indent=2,
        )

    def _list_benchmark_results(self, args: Dict) -> str:
        """List available benchmark result files."""
        limit = args.get("limit", 10)

        results_dir = Path(BENCHMARK_RESULTS_DIR)
        if not results_dir.exists():
            return json.dumps({"error": "Benchmark results directory not found"})

        # Find pipeline benchmark files
        files = sorted(
            results_dir.glob("pipeline_benchmark_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )[:limit]

        file_info = []
        for f in files:
            try:
                with open(f) as fp:
                    data = json.load(fp)
                    summary = data.get("summary", {})
                    file_info.append(
                        {
                            "filename": f.name,
                            "path": str(f),
                            "timestamp": data.get("timestamp", ""),
                            "scores": summary.get("scores", {}),
                            "overall": summary.get("overall", 0),
                        }
                    )
            except Exception:
                file_info.append(
                    {"filename": f.name, "path": str(f), "error": "Could not read"}
                )

        return json.dumps({"files": file_info, "total": len(files)}, indent=2)

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the optimization agent."""
        return """You are an expert prompt engineer specializing in pharmacogenomics data extraction.

Your role is to iteratively improve prompts that extract structured annotation data
from scientific literature about genetic variants, drugs, and phenotypes.

## Domain Knowledge

You understand:
- Pharmacogenomics: drug-gene interactions, variant-phenotype associations
- HLA alleles and drug hypersensitivity (var-pheno task)
- Drug metabolism variants like CYP enzymes (var-drug task)
- Functional analysis annotations (var-fa task)
- Study parameters extraction (study-parameters task)

## Optimization Strategy

1. **Evidence-Based Changes**: Always base changes on concrete benchmark data
2. **Field-Specific Fixes**: Target specific fields that score poorly
3. **Pattern Recognition**: Look for systematic errors across multiple PMCIDs
4. **Incremental Improvement**: Make focused changes, test, iterate
5. **Regression Prevention**: Ensure fixes don't break working behavior

## Output Quality

Your prompt improvements should:
- Include clear field definitions with examples
- Specify exact value formats (case, prefixes, etc.)
- Address common extraction errors explicitly
- Use decision tables for complex logic

## Changelog Requirements

Every new prompt version must include a changelog with:
- Specific changes made
- Issues being addressed (with PMCID examples)
- Expected improvements
- Fields targeted

## Analysis Documentation

Before making changes, always document your analysis using write_analysis tool:
- Worst performing PMCIDs with specific issues
- Fields with lowest scores and why
- Hypotheses for root causes
- Recommended changes

## Process

1. Use list_benchmark_results to find the most recent benchmark
2. Use analyze_benchmark to identify issues
3. Document your analysis with write_analysis
4. Read the current prompt with read_prompt
5. Examine ground truth and articles for worst PMCIDs
6. Create improved prompt with write_prompt
7. Test with run_benchmark
8. If improved, update best_prompts.json
9. Repeat until target score reached or max iterations"""

    def _find_lowest_scoring_task(self) -> tuple[str, float]:
        """Find the task with lowest benchmark score."""
        results_dir = Path(BENCHMARK_RESULTS_DIR)
        files = sorted(
            results_dir.glob("pipeline_benchmark_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )

        if not files:
            return "var-drug", 0.0  # Default fallback

        with open(files[0]) as f:
            results = json.load(f)

        scores = results.get("summary", {}).get("scores", {})

        # Find lowest (excluding 'overall' if present)
        task_scores = {
            k: v for k, v in scores.items() if k not in ("overall", "summary")
        }
        if not task_scores:
            return "var-drug", 0.0

        lowest_task = min(task_scores, key=task_scores.get)
        return lowest_task, task_scores[lowest_task]

    def run(self) -> OptimizationResult:
        """Execute the optimization loop."""
        # Determine target task
        if self.config.target_task == "auto":
            task, initial_score = self._find_lowest_scoring_task()
            print(f"Auto-selected task: {task} (score: {initial_score:.3f})")
        else:
            task = self.config.target_task
            _, scores = self._find_lowest_scoring_task()  # Just to get current score
            results_dir = Path(BENCHMARK_RESULTS_DIR)
            files = sorted(
                results_dir.glob("pipeline_benchmark_*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True,
            )
            if files:
                with open(files[0]) as f:
                    results = json.load(f)
                initial_score = (
                    results.get("summary", {}).get("scores", {}).get(task, 0)
                )
            else:
                initial_score = 0.0

        self._log_event(
            "optimization_started",
            {
                "task": task,
                "initial_score": initial_score,
                "target_score": self.config.target_score,
                "max_iterations": self.config.max_iterations,
            },
        )

        # Build optimization prompt
        optimization_prompt = f"""I need you to optimize the {task} prompt to achieve better benchmark scores.

## Current State
- Task: {task}
- Current Score: {initial_score:.4f} ({initial_score*100:.1f}%)
- Target Score: {self.config.target_score:.4f} ({self.config.target_score*100:.1f}%)
- Max Iterations: {self.config.max_iterations}
- Quick Model (for iteration): {self.config.quick_model}
- Validation Model: {self.config.validation_model}

## Your Objective
Improve the {task} prompt to achieve at least {self.config.target_score*100:.1f}% benchmark score.

## Process
1. First, use list_benchmark_results to find the most recent benchmark file
2. Use analyze_benchmark to find worst-performing PMCIDs and fields
3. Document your analysis with write_analysis
4. Use read_prompt to get the current best prompt for {task}
5. For the worst PMCIDs, read the ground truth and article to understand issues
6. Create a new prompt version that addresses the identified issues
7. Test with run_benchmark (using {self.config.sample_pmcids} sample PMCIDs)
8. If score improved, update best_prompts.json
9. Continue iterating until target score reached or after {self.config.max_iterations} iterations

Start by finding and analyzing the most recent benchmark results."""

        # Initialize conversation
        self.messages = [{"role": "user", "content": optimization_prompt}]

        # Track results
        score_history = [initial_score]
        prompt_versions = []
        changelogs = []
        improvement_cycles = 0  # Count actual prompt write+test cycles
        api_calls = 0  # Track API calls for logging
        current_score = initial_score
        final_score = initial_score

        # Agent loop - runs until agent completes or max improvement cycles reached
        # No hard limit on API calls - the improvement cycle limit is the real control
        while improvement_cycles < self.config.max_iterations:
            api_calls += 1
            print(f"\n{'='*60}")
            print(
                f"API call {api_calls} | Improvement cycles: {improvement_cycles}/{self.config.max_iterations}"
            )
            print(f"{'='*60}")

            # Get Claude's response
            response = self.client.messages.create(
                model="claude-opus-4-5-20251101",
                max_tokens=8192,
                system=self._get_system_prompt(),
                tools=TOOLS,
                messages=self.messages,
            )

            # Process response
            assistant_content = []
            tool_results = []
            wrote_prompt_this_turn = False

            for block in response.content:
                if block.type == "text":
                    print(f"\nAgent: {block.text[:500]}...")
                    assistant_content.append(block)
                elif block.type == "tool_use":
                    print(f"\nTool call: {block.name}")
                    print(f"Input: {json.dumps(block.input, indent=2)[:500]}...")
                    assistant_content.append(block)

                    # Execute tool
                    result = self._execute_tool(block.name, block.input)
                    print(f"Result: {result[:500]}...")

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )

                    # Track prompt versions - this marks start of improvement cycle
                    if block.name == "write_prompt":
                        prompt_versions.append(block.input.get("name", "unknown"))
                        if "changelog" in block.input:
                            changelogs.append(block.input["changelog"])
                        wrote_prompt_this_turn = True
                        print(
                            f"\n>>> New prompt version created: {block.input.get('name')}"
                        )

                    # Track benchmark results - completing an improvement cycle
                    if block.name == "run_benchmark":
                        try:
                            result_data = json.loads(result)
                            if "average_score" in result_data:
                                new_score = result_data["average_score"]
                                score_history.append(new_score)
                                print(f"\n>>> Benchmark score: {new_score:.4f}")

                                if new_score > current_score:
                                    current_score = new_score
                                    final_score = new_score
                                    print(
                                        f">>> Improvement: +{new_score - score_history[-2]:.4f}"
                                    )

                                # Count this as an improvement cycle if we wrote a prompt
                                if (
                                    wrote_prompt_this_turn
                                    or len(prompt_versions) > improvement_cycles
                                ):
                                    improvement_cycles += 1
                                    print(
                                        f">>> Completed improvement cycle {improvement_cycles}"
                                    )
                        except json.JSONDecodeError:
                            pass

            # Add assistant response to history
            self.messages.append({"role": "assistant", "content": assistant_content})

            # If there were tool calls, add results and continue
            if tool_results:
                self.messages.append({"role": "user", "content": tool_results})
            else:
                # No tool calls - agent is done or waiting
                if response.stop_reason == "end_turn":
                    print("\nAgent completed optimization")
                    break

            # Check if target reached
            if current_score >= self.config.target_score:
                print(f"\nTarget score reached: {current_score:.3f}")
                break

        print(f"\nTotal API calls: {api_calls}")
        iteration = improvement_cycles  # For result compatibility

        # Compile result
        success = final_score >= self.config.target_score or final_score > initial_score

        self._log_event(
            "optimization_complete",
            {
                "task": task,
                "initial_score": initial_score,
                "final_score": final_score,
                "iterations": iteration,
                "success": success,
            },
        )

        return OptimizationResult(
            task=task,
            initial_score=initial_score,
            final_score=final_score,
            iterations=iteration,
            prompt_versions=prompt_versions,
            score_history=score_history,
            changelogs=changelogs,
            success=success,
        )
