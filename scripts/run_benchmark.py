"""
Script to benchmark generated annotations against ground truth.

This is a thin CLI wrapper around the BenchmarkRunner utility.
"""

import json
import argparse
from datetime import datetime

from utils.benchmark_runner import BenchmarkRunner
from utils.output_manager import load_output_by_path


def load_generated_annotations_combined(file_path) -> dict:
    """Load combined file with multiple PMCIDs."""
    with open(file_path, "r") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark generated annotations against ground truth."
    )
    parser.add_argument(
        "--generated_file",
        type=str,
        required=True,
        help="Path to the JSON file with generated annotations.",
    )

    parser.add_argument(
        "--combined",
        help="Indicates if the generated annotations file is a combined file with multiple PMCIDs.",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--output_file",
        type=str,
        help="Path to the output file to save benchmark results.",
        default=f"benchmark_results/benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
    )

    args = parser.parse_args()

    # Initialize benchmark runner
    try:
        runner = BenchmarkRunner()
        print(f"Loaded ground truth from: {runner.ground_truth_source}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    if args.combined:
        # Load combined file
        print(f"Loading combined file: {args.generated_file}")
        combined_data = load_generated_annotations_combined(args.generated_file)

        # Benchmark all PMCIDs
        print(f"\nBenchmarking {len(combined_data)} PMCIDs...")
        all_results, task_averages, overall_score = runner.benchmark_multiple(
            combined_data, verbose=True
        )

        # Save detailed results
        output = {
            "timestamp": datetime.now().isoformat(),
            "source_file": args.generated_file,
            "summary": {
                "total_pmcids": len(combined_data),
                "benchmarked_pmcids": sum(1 for r in all_results.values() if r is not None),
                "task_averages": task_averages,
                "overall_score": overall_score,
            },
            "pmcid_results": all_results,
        }

        with open(args.output_file, "w") as f:
            json.dump(output, f, indent=4)

        print(f"\n=== Summary ===")
        print(f"Total PMCIDs: {len(combined_data)}")
        print(f"Overall Score: {overall_score:.2%}")
        print(f"Task Averages:")
        for task, score in task_averages.items():
            print(f"  {task}: {score:.2%}")
        print(f"\nResults saved to: {args.output_file}")

    else:
        # Load single file
        print(f"Loading file: {args.generated_file}")
        generated_annotations = load_output_by_path(args.generated_file)

        # Extract PMCID
        pmcid = generated_annotations.get("pmcid")
        if not pmcid:
            print("Error: No PMCID found in output file")
            return 1

        print(f"PMCID: {pmcid}")

        # Check if ground truth exists
        if not runner.has_ground_truth(pmcid):
            print(f"Error: No benchmark annotations found for PMCID: {pmcid}")
            return 1

        # Run benchmark
        print(f"\nRunning benchmark...")
        scores = runner.benchmark_pmcid(pmcid, generated_annotations, verbose=True)

        # Calculate overall score
        task_scores, sample_counts = runner.calculate_task_averages({pmcid: scores})
        overall_score = runner.calculate_overall_score(task_scores, sample_counts)

        # Save results
        output = {
            "timestamp": datetime.now().isoformat(),
            "pmcid": pmcid,
            "source_file": args.generated_file,
            "results": scores,
            "overall_score": overall_score,
        }

        with open(args.output_file, "w") as f:
            json.dump(output, f, indent=4)

        print(f"\n=== Summary ===")
        print(f"Overall Score: {overall_score:.2%}")
        print(f"Results saved to: {args.output_file}")

    return 0


if __name__ == "__main__":
    exit(main())
