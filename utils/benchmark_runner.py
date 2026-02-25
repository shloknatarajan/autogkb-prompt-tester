"""
Unified benchmark runner for evaluating annotation quality.

This module provides a consistent interface for running benchmarks against
ground truth, eliminating duplication between main.py and scripts.
"""

import json
import os
from typing import Dict, Optional, List, Tuple

from benchmarks.pheno_benchmark import evaluate_phenotype_annotations
from benchmarks.drug_benchmark import evaluate_drug_annotations
from benchmarks.fa_benchmark import evaluate_fa_from_articles
from benchmarks.study_parameters_benchmark import evaluate_study_parameters

from .config import GROUND_TRUTH_FILE, GROUND_TRUTH_NORMALIZED_FILE


class BenchmarkRunner:
    """
    Manages benchmark execution against ground truth annotations.

    Features:
    - Automatic ground truth loading with normalized fallback
    - Support for all three annotation types (phenotype, drug, functional analysis)
    - Consistent score calculation and aggregation
    - Graceful error handling
    """

    def __init__(self, ground_truth_file: Optional[str] = None):
        """
        Initialize benchmark runner with ground truth data.

        Args:
            ground_truth_file: Path to ground truth JSON file. If None, will
                             use normalized version if available, otherwise regular.
        """
        self.ground_truth = self._load_ground_truth(ground_truth_file)
        self.ground_truth_source = ground_truth_file or self._get_default_ground_truth()

    def _get_default_ground_truth(self) -> str:
        """Determine which ground truth file to use."""
        if os.path.exists(GROUND_TRUTH_NORMALIZED_FILE):
            return GROUND_TRUTH_NORMALIZED_FILE
        return GROUND_TRUTH_FILE

    def _load_ground_truth(self, file_path: Optional[str] = None) -> Dict:
        """
        Load ground truth with normalized fallback.

        Args:
            file_path: Explicit path to ground truth file

        Returns:
            Ground truth dictionary keyed by PMCID

        Raises:
            FileNotFoundError: If no ground truth file exists
        """
        # Determine which file to use
        if file_path:
            path = file_path
        elif os.path.exists(GROUND_TRUTH_NORMALIZED_FILE):
            path = GROUND_TRUTH_NORMALIZED_FILE
        elif os.path.exists(GROUND_TRUTH_FILE):
            path = GROUND_TRUTH_FILE
        else:
            raise FileNotFoundError(
                f"Ground truth not found. Checked:\n"
                f"  - {GROUND_TRUTH_NORMALIZED_FILE}\n"
                f"  - {GROUND_TRUTH_FILE}"
            )

        # Load and clean data
        with open(path, "r") as f:
            data = json.load(f)

        # Remove metadata if present (from normalized files)
        if "_metadata" in data:
            del data["_metadata"]

        return data

    def benchmark_pmcid(
        self, pmcid: str, predictions: Dict, verbose: bool = True
    ) -> Dict:
        """
        Run all benchmarks for a single PMCID.

        Args:
            pmcid: PubMed Central ID
            predictions: Prediction dictionary with annotation arrays
            verbose: Whether to print progress messages

        Returns:
            Dictionary with benchmark results for each annotation type:
            {
                "var-pheno": {"overall_score": 0.75, "raw_score": 75, ...},
                "var-drug": {"overall_score": 0.85, "field_scores": {...}, ...},
                "var-fa": {"overall_score": 0.65, "field_scores": {...}, ...}
            }
        """
        if pmcid not in self.ground_truth:
            raise ValueError(f"No ground truth found for PMCID: {pmcid}")

        ground_truth = self.ground_truth[pmcid]
        results = {}

        # Phenotype benchmark
        if "var_pheno_ann" in ground_truth and len(ground_truth["var_pheno_ann"]) > 0:
            gt_pheno = ground_truth["var_pheno_ann"]
            pred_pheno = predictions.get("var_pheno_ann", [])

            if not pred_pheno:
                results["var-pheno"] = {
                    "error": "Empty predictions list",
                    "overall_score": 0.0,
                    "total_samples": 0,
                }
                if verbose:
                    print(f"✗ Phenotype benchmark skipped: empty predictions")
            else:
                try:
                    result = evaluate_phenotype_annotations([gt_pheno, pred_pheno])
                    results["var-pheno"] = {
                        "overall_score": result.get("overall_score", 0.0),  # Already 0-1
                        "field_scores": result.get("field_scores", {}),
                        "total_samples": result.get("total_samples", len(pred_pheno)),
                        "detailed_results": result.get("detailed_results", []),
                        "aligned_variants": result.get("aligned_variants", []),
                        "unmatched_ground_truth": result.get("unmatched_ground_truth", []),
                        "unmatched_predictions": result.get("unmatched_predictions", []),
                    }
                    if verbose:
                        print(
                            f"✓ Phenotype benchmark score: {result.get('overall_score', 0):.2f}"
                        )
                except Exception as e:
                    if verbose:
                        print(f"✗ Phenotype benchmark failed: {e}")
                    results["var-pheno"] = {
                        "error": f"Evaluation failed: {str(e)}",
                        "overall_score": 0.0,
                        "total_samples": 0,
                    }

        # Drug benchmark
        if "var_drug_ann" in ground_truth and len(ground_truth["var_drug_ann"]) > 0:
            gt_drug = ground_truth["var_drug_ann"]
            pred_drug = predictions.get("var_drug_ann", [])

            if not pred_drug:
                results["var-drug"] = {
                    "error": "Empty predictions list",
                    "overall_score": 0.0,
                    "total_samples": 0,
                }
                if verbose:
                    print(f"✗ Drug benchmark skipped: empty predictions")
            else:
                try:
                    result = evaluate_drug_annotations([gt_drug, pred_drug])
                    results["var-drug"] = {
                        "overall_score": result.get("overall_score", 0.0),
                        "field_scores": result.get("field_scores", {}),
                        "total_samples": result.get("total_samples", len(pred_drug)),
                        "detailed_results": result.get("detailed_results", []),
                        "aligned_variants": result.get("aligned_variants", []),
                        "unmatched_ground_truth": result.get("unmatched_ground_truth", []),
                        "unmatched_predictions": result.get("unmatched_predictions", []),
                    }
                    if verbose:
                        print(
                            f"✓ Drug benchmark score: {result.get('overall_score', 0):.2f}"
                        )
                except Exception as e:
                    if verbose:
                        print(f"✗ Drug benchmark failed: {e}")
                    results["var-drug"] = {
                        "error": f"Evaluation failed: {str(e)}",
                        "overall_score": 0.0,
                        "total_samples": 0,
                    }

        # Functional analysis benchmark
        if "var_fa_ann" in ground_truth and len(ground_truth["var_fa_ann"]) > 0:
            gt_fa = ground_truth["var_fa_ann"]
            pred_fa = predictions.get("var_fa_ann", [])

            if not pred_fa:
                results["var-fa"] = {
                    "error": "Empty predictions list",
                    "overall_score": 0.0,
                    "total_samples": 0,
                }
                if verbose:
                    print(f"✗ FA benchmark skipped: empty predictions")
            else:
                try:
                    # FA benchmark needs full article context
                    result = evaluate_fa_from_articles(ground_truth, predictions)
                    results["var-fa"] = {
                        "overall_score": result.get("overall_score", 0.0),
                        "field_scores": result.get("field_scores", {}),
                        "total_samples": result.get("total_samples", len(pred_fa)),
                        "detailed_results": result.get("detailed_results", []),
                        "aligned_variants": result.get("aligned_variants", []),
                        "unmatched_ground_truth": result.get("unmatched_ground_truth", []),
                        "unmatched_predictions": result.get("unmatched_predictions", []),
                    }
                    if verbose:
                        print(
                            f"✓ FA benchmark score: {result.get('overall_score', 0):.2f}"
                        )
                except Exception as e:
                    if verbose:
                        print(f"✗ FA benchmark failed: {e}")
                    results["var-fa"] = {
                        "error": f"Evaluation failed: {str(e)}",
                        "overall_score": 0.0,
                        "total_samples": 0,
                    }

        # Study parameters benchmark
        if (
            "study_parameters" in ground_truth
            and len(ground_truth["study_parameters"]) > 0
        ):
            gt_sp = ground_truth["study_parameters"]
            pred_sp = predictions.get("study_parameters", [])

            if not pred_sp:
                results["study-parameters"] = {
                    "error": "Empty predictions list",
                    "overall_score": 0.0,
                    "total_samples": 0,
                }
                if verbose:
                    print(f"✗ Study parameters benchmark skipped: empty predictions")
            else:
                try:
                    result = evaluate_study_parameters([gt_sp, pred_sp])
                    results["study-parameters"] = {
                        "overall_score": result.get("overall_score", 0.0),
                        "field_scores": result.get("field_scores", {}),
                        "total_samples": result.get("total_samples", len(pred_sp)),
                        "detailed_results": result.get("detailed_results", []),
                        "aligned_variants": result.get("aligned_variants", []),
                        "unmatched_ground_truth": result.get("unmatched_ground_truth", []),
                        "unmatched_predictions": result.get("unmatched_predictions", []),
                    }
                    if verbose:
                        print(
                            f"✓ Study parameters benchmark score: {result.get('overall_score', 0):.2f}"
                        )
                except Exception as e:
                    if verbose:
                        print(f"✗ Study parameters benchmark failed: {e}")
                    results["study-parameters"] = {
                        "error": f"Evaluation failed: {str(e)}",
                        "overall_score": 0.0,
                        "total_samples": 0,
                    }

        return results

    def benchmark_multiple(
        self, outputs: Dict[str, Dict], verbose: bool = True
    ) -> Tuple[Dict[str, Dict], Dict[str, float], float]:
        """
        Benchmark multiple PMCIDs and calculate aggregated scores.

        Args:
            outputs: Dictionary mapping PMCID to prediction dictionary
            verbose: Whether to print progress messages

        Returns:
            Tuple of:
            - Individual results: {pmcid: benchmark_results}
            - Task averages: {task: average_score}
            - Overall average score
        """
        all_results = {}

        for pmcid, predictions in outputs.items():
            if pmcid not in self.ground_truth:
                if verbose:
                    print(f"Warning: No ground truth for {pmcid}, skipping")
                all_results[pmcid] = None
                continue

            try:
                all_results[pmcid] = self.benchmark_pmcid(pmcid, predictions, verbose)
            except Exception as e:
                if verbose:
                    print(f"Error benchmarking {pmcid}: {e}")
                all_results[pmcid] = {"error": str(e)}

        # Calculate aggregated scores
        task_scores, sample_counts = self.calculate_task_averages(all_results)
        overall_score = self.calculate_overall_score(task_scores, sample_counts)

        return all_results, task_scores, overall_score

    def calculate_task_averages(
        self, results: Dict[str, Dict]
    ) -> Tuple[Dict[str, float], Dict[str, int]]:
        """
        Calculate average scores per task across all PMCIDs and track ground truth counts.

        Args:
            results: Dictionary mapping PMCID to benchmark results

        Returns:
            Tuple of:
            - task_averages: {task: average_score}
            - task_gt_counts: {task: total_ground_truth_count}
        """
        task_scores = {}
        task_gt_counts = {}

        for pmcid, scores in results.items():
            if scores is None or "error" in scores:
                continue

            for task, result in scores.items():
                if task not in task_scores:
                    task_scores[task] = []
                    task_gt_counts[task] = 0

                # Extract overall_score, handle errors gracefully
                if isinstance(result, dict) and "overall_score" in result:
                    if "error" not in result:
                        task_scores[task].append(result["overall_score"])
                        # Track TOTAL ground truth count (matched + unmatched)
                        matched_count = result.get("total_samples", 0)
                        unmatched_gt = result.get("unmatched_ground_truth", [])
                        total_gt_count = matched_count + len(unmatched_gt)
                        task_gt_counts[task] += total_gt_count

        # Calculate averages
        average_scores = {
            task: sum(scores) / len(scores) if scores else 0.0
            for task, scores in task_scores.items()
        }

        return average_scores, task_gt_counts

    def calculate_overall_score(
        self,
        task_averages: Dict[str, float],
        task_gt_counts: Dict[str, int]
    ) -> float:
        """
        Calculate GT-weighted overall score from task averages.

        Tasks are weighted by their total ground truth count (matched + unmatched).
        This ensures tasks with more GT annotations contribute proportionally more,
        and missing predictions count against the overall score.
        Missing tasks (with 0 GT annotations) are automatically excluded.

        Args:
            task_averages: {task: average_score}
            task_gt_counts: {task: total_ground_truth_count}

        Returns:
            Weighted average score
        """
        if not task_averages or not task_gt_counts:
            return 0.0

        # Calculate weighted sum and total weight
        weighted_sum = 0.0
        total_gt = 0

        for task, avg_score in task_averages.items():
            gt_count = task_gt_counts.get(task, 0)
            if gt_count > 0:  # Only include tasks with data
                weighted_sum += avg_score * gt_count
                total_gt += gt_count

        if total_gt == 0:
            return 0.0

        return weighted_sum / total_gt

    def has_ground_truth(self, pmcid: str) -> bool:
        """Check if ground truth exists for a PMCID."""
        return pmcid in self.ground_truth

    def get_pmcids(self) -> List[str]:
        """Get list of all PMCIDs in ground truth."""
        return list(self.ground_truth.keys())
