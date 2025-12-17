#!/usr/bin/env python3
"""
Batch Processing Script for AutoGKB Prompt Tester

This script processes multiple article files using the best prompts for each task,
generates citations, and saves outputs to the outputs directory.

Usage:
    python batch_process.py --data-dir ./data --concurrency 3
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import argparse

# Add parent directory to path to import from main.py
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import generate_citations_for_annotation
from llm import generate_response, normalize_model
from utils.cost import CostTracker, UsageInfo

# Citation prompt template
CITATION_PROMPT = """You are analyzing a genetic variant annotation. Your task is to find direct quotes from the article text that support this specific annotation.

Annotation Details:
- Variant/Haplotype: {variant}
- Gene: {gene}
- Drug(s): {drug}
- Finding: {sentence}
- Notes: {notes}

Article Text:
{full_text}

Please identify 1-3 direct quotes from the article that provide evidence for this annotation. Focus on quotes that mention:
1. The specific variant or haplotype
2. The phenotype, outcome, or drug response
3. Statistical significance or effect size
4. Study population or methodology

Return your response as a JSON object with a "citations" array containing the exact quoted text:
{{
  "citations": [
    "Direct quote from article supporting this finding",
    "Another relevant quote if available"
  ]
}}

Important:
- Only include quotes that directly support THIS specific annotation
- Use exact quotes from the article text
- Do not fabricate or modify quotes
- Return empty array if no supporting quotes found"""


class BatchProcessor:
    """Handles batch processing of article files with prompts and citations."""

    def __init__(self, args):
        self.data_dir = Path(args.data_dir)
        self.prompts_file = Path(args.prompts)
        self.best_prompts_file = Path(args.best_prompts)
        self.output_dir = Path(args.output_dir)
        self.concurrency = args.concurrency
        self.skip_existing = args.skip_existing
        # Normalize model to provider-prefixed format (e.g., "openai/gpt-4o")
        self.model = normalize_model(args.model)

        # Create necessary directories
        self.output_dir.mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)

        # Setup logging
        self.setup_logging()

        # Statistics
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "start_time": datetime.now(),
            "total_cost_usd": 0.0,
        }

    def setup_logging(self):
        """Configure logging to both file and console."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"logs/batch_{timestamp}.log"

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # Configure root logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.logger.info(f"Logging to {log_file}")

    def load_prompts(self) -> List[Dict]:
        """Load prompts via PromptManager."""
        from utils.prompt_manager import PromptManager

        self.logger.info("Loading prompts via PromptManager")
        manager = PromptManager()
        prompts = manager.load_prompts()
        self.logger.info(f"Loaded {len(prompts)} prompts")
        return prompts

    def load_best_prompts_config(self) -> Dict[str, str]:
        """Load best prompts configuration via PromptManager."""
        from utils.prompt_manager import PromptManager

        self.logger.info(f"Loading best prompts config from: {self.best_prompts_file}")
        manager = PromptManager(best_prompts_file=str(self.best_prompts_file))
        try:
            config = manager.load_best_config()
            self.logger.info(f"Best prompts config: {config}")
            return config
        except FileNotFoundError:
            self.logger.warning("Best prompts config not found")
            return {}

    def select_best_prompts(
        self, prompts: List[Dict], config: Dict[str, str]
    ) -> List[Dict]:
        """
        Select the best prompt for each task based on config.

        Args:
            prompts: All available prompts
            config: Mapping of task -> prompt name

        Returns:
            List of selected prompts (one per task)
        """
        selected = []
        tasks_seen = set()

        for prompt in prompts:
            task = prompt["task"]

            # Skip if we already selected a prompt for this task
            if task in tasks_seen:
                continue

            # Check if this prompt matches the config
            if task in config and prompt["name"] == config[task]:
                selected.append(prompt)
                tasks_seen.add(task)
                self.logger.info(f"Selected prompt for task '{task}': {prompt['name']}")

        # Log any tasks in config that weren't found
        for task, name in config.items():
            if task not in tasks_seen:
                self.logger.warning(f"Could not find prompt '{name}' for task '{task}'")

        self.logger.info(f"Selected {len(selected)} prompts for processing")
        return selected

    def get_article_files(self) -> List[Path]:
        """Get all .md files from data directory."""
        if not self.data_dir.exists():
            self.logger.error(f"Data directory not found: {self.data_dir}")
            return []

        files = sorted(self.data_dir.glob("*.md"))
        self.logger.info(f"Found {len(files)} article files in {self.data_dir}")
        return files

    async def run_single_task(self, prompt: Dict, text: str, model: str) -> tuple:
        """
        Run a single task prompt and return results.

        Returns:
            (task_name, prompt_name, output, error)
        """
        try:
            # Parse response format
            response_format = prompt.get("response_format")
            if isinstance(response_format, str):
                response_format = json.loads(response_format)

            # Format prompt with article text or append article text if no placeholder
            if "{article_text}" not in prompt["prompt"]:
                formatted_prompt = f"{prompt['prompt']}\n\n{text}"
            else:
                formatted_prompt = prompt["prompt"].replace("{article_text}", text)

            # Generate response with usage tracking
            self.logger.debug(
                f"Running task: {prompt['task']} with prompt: {prompt['name']}"
            )
            result = await generate_response(
                prompt=formatted_prompt,
                text="",
                model=model,
                response_format=response_format,
                temperature=prompt.get("temperature", 0.0),
                return_usage=True,
            )
            output, usage_info = result

            # Parse output
            parsed_output = json.loads(output)
            self.logger.debug(f"Task {prompt['task']} completed successfully")

            return (prompt["task"], prompt["name"], parsed_output, None, usage_info)

        except Exception as e:
            self.logger.error(f"Error running task {prompt['task']}: {str(e)}")
            return (prompt["task"], prompt["name"], None, str(e), None)

    async def generate_single_citation(
        self, ann_type: str, index: int, annotation: Dict, text: str, model: str
    ) -> tuple:
        """
        Generate citation for one annotation.

        Returns:
            (ann_type, index, citations, error, usage_info)
        """
        try:
            result = await generate_citations_for_annotation(
                annotation=annotation,
                full_text=text,
                citation_prompt_template=CITATION_PROMPT,
                model=model,
                return_usage=True,
            )
            citations, usage_info = result
            return (ann_type, index, citations, None, usage_info)
        except Exception as e:
            self.logger.error(
                f"Error generating citation for {ann_type}[{index}]: {str(e)}"
            )
            return (ann_type, index, [], str(e), None)

    async def process_single_file(
        self, file_path: Path, prompts: List[Dict], semaphore: asyncio.Semaphore
    ) -> Dict[str, Any]:
        """
        Process a single article file with all selected prompts.

        Args:
            file_path: Path to article .md file
            prompts: List of prompts to run
            semaphore: Concurrency control semaphore

        Returns:
            Dictionary with processing results
        """
        async with semaphore:
            start_time = datetime.now()
            self.logger.info(f"Processing: {file_path.name}")

            try:
                # Read article text
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

                # Run all tasks in parallel
                self.logger.info(
                    f"Running {len(prompts)} tasks in parallel for {file_path.name}"
                )
                task_coroutines = [
                    self.run_single_task(prompt, text, model=self.model)
                    for prompt in prompts
                ]
                task_results_list = await asyncio.gather(*task_coroutines)

                # Combine task results and track costs
                task_results = {}
                prompts_used = {}
                cost_tracker = CostTracker()

                for task_name, prompt_name, output, error, usage_info in task_results_list:
                    if error:
                        task_results[task_name] = {"error": error}
                        self.logger.error(f"Task {task_name} failed: {error}")
                    else:
                        task_results.update(output)
                    prompts_used[task_name] = prompt_name
                    if usage_info:
                        cost_tracker.add_usage(task_name, usage_info)

                # Generate citations in parallel
                citation_tasks = []

                # Collect citation tasks for all annotation types
                for ann_type in ["var_pheno_ann", "var_drug_ann", "var_fa_ann"]:
                    if ann_type in task_results and isinstance(
                        task_results[ann_type], list
                    ):
                        for i, annotation in enumerate(task_results[ann_type]):
                            citation_tasks.append(
                                self.generate_single_citation(
                                    ann_type, i, annotation, text, self.model
                                )
                            )

                # Run all citations in parallel
                if citation_tasks:
                    self.logger.info(
                        f"Generating {len(citation_tasks)} citations in parallel for {file_path.name}"
                    )
                    citation_results = await asyncio.gather(*citation_tasks)

                    # Add citations to annotations and track costs
                    for ann_type, index, citations, error, usage_info in citation_results:
                        if error:
                            self.logger.warning(
                                f"Citation generation failed for {ann_type}[{index}]: {error}"
                            )
                        task_results[ann_type][index]["Citations"] = citations
                        if usage_info:
                            cost_tracker.add_usage("citations", usage_info)

                # Extract PMCID from results or use filename
                pmcid = task_results.get("pmcid", file_path.stem)

                # Add metadata and usage
                task_results["input_text"] = text
                task_results["timestamp"] = datetime.now().isoformat()
                task_results["prompts_used"] = prompts_used
                task_results["usage"] = cost_tracker.get_summary()

                # Save output file
                output_file = self.output_dir / f"{pmcid}.json"

                # Check if we should skip existing
                if self.skip_existing and output_file.exists():
                    self.logger.info(
                        f"Skipping {file_path.name} - output already exists: {output_file}"
                    )
                    self.stats["skipped"] += 1
                    return {
                        "file": file_path.name,
                        "status": "skipped",
                        "output_file": str(output_file),
                        "duration": (datetime.now() - start_time).total_seconds(),
                    }

                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(task_results, f, indent=2, ensure_ascii=False)

                duration = (datetime.now() - start_time).total_seconds()
                file_cost = cost_tracker.total_cost_usd
                self.logger.info(
                    f"✓ Completed {file_path.name} in {duration:.1f}s (${file_cost:.4f}) -> {output_file}"
                )

                self.stats["success"] += 1
                self.stats["total_cost_usd"] += file_cost

                return {
                    "file": file_path.name,
                    "status": "success",
                    "output_file": str(output_file),
                    "pmcid": pmcid,
                    "tasks_completed": len(prompts_used),
                    "citations_generated": len(citation_tasks),
                    "duration": duration,
                    "cost_usd": file_cost,
                }

            except Exception as e:
                self.logger.error(f"✗ Failed to process {file_path.name}: {str(e)}")
                self.stats["failed"] += 1
                return {
                    "file": file_path.name,
                    "status": "failed",
                    "error": str(e),
                    "duration": (datetime.now() - start_time).total_seconds(),
                }

    async def process_all_files(self):
        """Main processing loop for all files."""
        # Load prompts and configuration
        all_prompts = self.load_prompts()
        best_prompts_config = self.load_best_prompts_config()
        selected_prompts = self.select_best_prompts(all_prompts, best_prompts_config)

        if not selected_prompts:
            self.logger.error("No prompts selected. Check your configuration.")
            return

        # Get article files
        article_files = self.get_article_files()
        if not article_files:
            self.logger.error("No article files found.")
            return

        self.stats["total"] = len(article_files)

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.concurrency)

        self.logger.info(f"\nStarting batch processing of {len(article_files)} files")
        self.logger.info(f"Concurrency limit: {self.concurrency}")
        self.logger.info(f"Skip existing: {self.skip_existing}\n")

        # Process all files
        tasks = [
            self.process_single_file(file_path, selected_prompts, semaphore)
            for file_path in article_files
        ]

        results = await asyncio.gather(*tasks)

        # Print summary
        self.print_summary(results)

    def print_summary(self, results: List[Dict]):
        """Print processing summary."""
        duration = (datetime.now() - self.stats["start_time"]).total_seconds()

        self.logger.info("\n" + "=" * 60)
        self.logger.info("BATCH PROCESSING SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total files: {self.stats['total']}")
        self.logger.info(f"Successful: {self.stats['success']}")
        self.logger.info(f"Failed: {self.stats['failed']}")
        self.logger.info(f"Skipped: {self.stats['skipped']}")
        self.logger.info(f"Total duration: {duration:.1f}s")
        self.logger.info(f"Total API cost: ${self.stats['total_cost_usd']:.4f}")

        if self.stats["success"] > 0:
            avg_duration = (
                sum(r["duration"] for r in results if r["status"] == "success")
                / self.stats["success"]
            )
            avg_cost = self.stats["total_cost_usd"] / self.stats["success"]
            self.logger.info(f"Average per file: {avg_duration:.1f}s, ${avg_cost:.4f}")

        # List failed files
        failed = [r for r in results if r["status"] == "failed"]
        if failed:
            self.logger.info("\nFailed files:")
            for result in failed:
                self.logger.info(
                    f"  - {result['file']}: {result.get('error', 'Unknown error')}"
                )

        self.logger.info("=" * 60 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch process article files with AutoGKB prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--data-dir",
        type=str,
        default="./persistent_data/benchmark_articles_md",
        help="Directory containing input .md files (default: ./persistent_data/benchmark_articles_md)",
    )

    parser.add_argument(
        "--prompts",
        type=str,
        default="stored_prompts.json",
        help="Path to prompts file (default: stored_prompts.json)",
    )

    parser.add_argument(
        "--best-prompts",
        type=str,
        default="best_prompts.json",
        help="Path to best prompts configuration (default: best_prompts.json)",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="./outputs",
        help="Directory for output files (default: ./outputs)",
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Number of files to process in parallel (default: 3)",
    )

    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="LLM model to use for processing (default: gpt-5-mini)",
    )

    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip files that already have output files",
    )

    args = parser.parse_args()

    # Create and run processor
    processor = BatchProcessor(args)

    try:
        asyncio.run(processor.process_all_files())
    except KeyboardInterrupt:
        processor.logger.info("\nProcessing interrupted by user")
        sys.exit(1)
    except Exception as e:
        processor.logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
