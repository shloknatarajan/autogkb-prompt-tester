#!/usr/bin/env python3
"""
Full Benchmark Pipeline

Runs the complete benchmarking workflow:
1. Process all PMCIDs in benchmark set using best prompts
2. Combine individual outputs into single file
3. Benchmark against ground truth
4. Save and report results
"""

import subprocess
import sys
import json
import os
import argparse
from datetime import datetime
from pathlib import Path
from term_normalization.term_lookup import normalize_annotation


def log(message: str):
    """Log a message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def run_command(cmd: list, description: str) -> int:
    """Run a shell command and return exit code."""
    log(f"Running: {description}")
    log(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd)

    if result.returncode != 0:
        log(f"ERROR: {description} failed with exit code {result.returncode}")
    else:
        log(f"SUCCESS: {description} completed")

    return result.returncode


def step1_batch_process(
    data_dir: str,
    output_dir: str,
    prompts_file: str,
    best_prompts_file: str,
    model: str,
    concurrency: int,
    skip_existing: bool,
) -> bool:
    """Step 1: Process all PMCIDs using batch_process.py"""
    log("=" * 60)
    log("STEP 1: Batch Processing PMCIDs")
    log("=" * 60)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        sys.executable,
        "scripts/batch_process.py",
        "--data-dir",
        data_dir,
        "--prompts",
        prompts_file,
        "--best-prompts",
        best_prompts_file,
        "--output-dir",
        output_dir,
        "--model",
        model,
        "--concurrency",
        str(concurrency),
    ]

    if skip_existing:
        cmd.append("--skip-existing")

    return run_command(cmd, "Batch processing") == 0


def step1_5_normalize_terms(output_dir: str) -> bool:
    """Step 1.5: Normalize terms in all output files."""
    log("=" * 60)
    log("STEP 1.5: Normalizing Terms")
    log("=" * 60)

    # Find all JSON output files
    output_files = list(Path(output_dir).glob("*.json"))

    if not output_files:
        log("No output files found to normalize")
        return True

    log(f"Found {len(output_files)} files to normalize")

    successful = 0
    failed = 0

    for output_file in output_files:
        try:
            # Normalize in place (overwrite the original file)
            temp_file = output_file.with_suffix(".json.tmp")
            normalize_annotation(output_file, temp_file)

            # Replace original with normalized version
            temp_file.replace(output_file)
            successful += 1
            log(f"✓ Normalized {output_file.name}")
        except Exception as e:
            failed += 1
            log(f"✗ Failed to normalize {output_file.name}: {e}")

    log(f"Normalization complete: {successful} successful, {failed} failed")

    if failed > 0:
        log(f"WARNING: {failed} files failed to normalize")

    return failed == 0


def step2_combine_outputs(output_dir: str, combined_file: str) -> bool:
    """Step 2: Combine individual outputs into single file."""
    log("=" * 60)
    log("STEP 2: Combining Outputs")
    log("=" * 60)

    cmd = [
        sys.executable,
        "scripts/combine_outputs.py",
        "--input_folder",
        output_dir,
        "--output_file",
        combined_file,
    ]

    return run_command(cmd, "Combining outputs") == 0


def step3_run_benchmark(combined_file: str, results_dir: str) -> tuple[bool, str]:
    """Step 3: Run benchmark on combined outputs."""
    log("=" * 60)
    log("STEP 3: Running Benchmark")
    log("=" * 60)

    # Generate results filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(results_dir, f"pipeline_benchmark_{timestamp}.json")

    os.makedirs(results_dir, exist_ok=True)

    cmd = [
        sys.executable,
        "-m" "scripts.run_benchmark",
        "--generated_file",
        combined_file,
        "--combined=True",
        "--output_file",
        results_file,
    ]

    success = run_command(cmd, "Running benchmark") == 0
    return success, results_file


def step4_report_results(results_file: str):
    """Step 4: Load and report benchmark results."""
    log("=" * 60)
    log("STEP 4: Benchmark Results Summary")
    log("=" * 60)

    if not os.path.exists(results_file):
        log(f"ERROR: Results file not found: {results_file}")
        return

    with open(results_file, "r") as f:
        results = json.load(f)

    # Print summary
    print("\n" + "=" * 60)
    print("                   BENCHMARK RESULTS")
    print("=" * 60)

    if "summary" in results:
        summary = results["summary"]
        print(f"\nTotal PMCIDs processed: {summary.get('total_pmcids', 'N/A')}")
        print(f"Timestamp: {summary.get('timestamp', 'N/A')}")

        if "scores" in summary:
            print("\nScores by Annotation Type:")
            print("-" * 40)
            for task, score in summary["scores"].items():
                if isinstance(score, (int, float)):
                    print(f"  {task:20s}: {score:.4f} ({score*100:.1f}%)")
                else:
                    print(f"  {task:20s}: {score}")

            if "overall" in summary["scores"]:
                overall = summary["scores"]["overall"]
                print("-" * 40)
                print(f"  {'OVERALL':20s}: {overall:.4f} ({overall*100:.1f}%)")

    # Per-PMCID details if available
    if "pmcid_results" in results:
        print("\nPer-PMCID Results:")
        print("-" * 60)

        pmcid_results = results["pmcid_results"]
        for pmcid, scores in pmcid_results.items():
            if isinstance(scores, dict):
                avg_score = sum(
                    s for s in scores.values() if isinstance(s, (int, float))
                ) / max(len(scores), 1)
                print(f"  {pmcid}: {avg_score:.4f}")

    print("\n" + "=" * 60)
    print(f"Full results saved to: {results_file}")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Full Benchmark Pipeline - Process, Combine, Benchmark, Report"
    )

    parser.add_argument(
        "--data-dir",
        default="persistent_data/benchmark_articles_md",
        help="Directory containing markdown files to process (default: persistent_data/benchmark_articles_md)",
    )

    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for individual outputs (default: outputs/pipeline_run_TIMESTAMP)",
    )

    parser.add_argument(
        "--prompts",
        default="stored_prompts.json",
        help="Path to stored prompts file (default: stored_prompts.json)",
    )

    parser.add_argument(
        "--best-prompts",
        default="best_prompts.json",
        help="Path to best prompts configuration (default: best_prompts.json)",
    )

    parser.add_argument(
        "--model", default="gpt-4o-mini", help="LLM model to use (default: gpt-4o-mini)"
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=3,
        help="Number of concurrent processes (default: 3)",
    )

    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip PMCIDs that already have output files",
    )

    parser.add_argument(
        "--skip-processing",
        action="store_true",
        help="Skip batch processing, use existing outputs",
    )

    parser.add_argument(
        "--combined-file",
        default=None,
        help="Path to combined output file (if skipping processing)",
    )

    parser.add_argument(
        "--results-dir",
        default="benchmark_results",
        help="Directory for benchmark results (default: benchmark_results)",
    )

    args = parser.parse_args()

    # Generate timestamp for this run
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Set default output directory if not provided
    if args.output_dir is None:
        args.output_dir = f"outputs/pipeline_run_{run_timestamp}"

    # Set combined file path
    if args.combined_file is None:
        args.combined_file = os.path.join(
            args.output_dir, f"combined_{run_timestamp}.json"
        )

    # Print configuration
    log("=" * 60)
    log("FULL BENCHMARK PIPELINE")
    log("=" * 60)
    log(f"Data directory: {args.data_dir}")
    log(f"Output directory: {args.output_dir}")
    log(f"Prompts file: {args.prompts}")
    log(f"Best prompts: {args.best_prompts}")
    log(f"Model: {args.model}")
    log(f"Concurrency: {args.concurrency}")
    log(f"Skip existing: {args.skip_existing}")
    log(f"Skip processing: {args.skip_processing}")
    log(f"Combined file: {args.combined_file}")
    log(f"Results directory: {args.results_dir}")
    log("=" * 60 + "\n")

    # Step 1: Batch Process
    if not args.skip_processing:
        success = step1_batch_process(
            data_dir=args.data_dir,
            output_dir=args.output_dir,
            prompts_file=args.prompts,
            best_prompts_file=args.best_prompts,
            model=args.model,
            concurrency=args.concurrency,
            skip_existing=args.skip_existing,
        )

        if not success:
            log("Pipeline aborted due to batch processing failure")
            sys.exit(1)
    else:
        log("Skipping batch processing (using existing outputs)")

    # Step 1.5: Normalize Terms
    success = step1_5_normalize_terms(args.output_dir)

    if not success:
        log("WARNING: Term normalization had failures, but continuing pipeline")

    # Step 2: Combine Outputs
    success = step2_combine_outputs(args.output_dir, args.combined_file)

    if not success:
        log("Pipeline aborted due to combine outputs failure")
        sys.exit(1)

    # Step 3: Run Benchmark
    success, results_file = step3_run_benchmark(args.combined_file, args.results_dir)

    if not success:
        log("Pipeline aborted due to benchmark failure")
        sys.exit(1)

    # Step 4: Report Results
    step4_report_results(results_file)

    log("Pipeline completed successfully!")


if __name__ == "__main__":
    main()
