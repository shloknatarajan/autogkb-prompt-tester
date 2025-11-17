import json
from datetime import datetime

from benchmarks.pheno_benchmark import evaluate_phenotype_annotations
from benchmarks.fa_benchmark import (
    evaluate_fa_from_articles,
    evaluate_functional_analysis,
)

from benchmarks.drug_benchmark import evaluate_drug_annotations

BENCHMARK_FILE = "persistent_data/benchmark_annotations.json"


def load_benchmark_annotations():
    with open(BENCHMARK_FILE, "r") as f:
        return json.load(f)


BENCHMARK_ANNOTATIONS = load_benchmark_annotations()


def load_generated_annotations_single(file_path) -> (dict, str):
    generated_annotations = {}
    with open(file_path, "r") as f:
        generated_annotations = json.load(f)

    pmcid = generated_annotations.get("pmcid", "")
    return generated_annotations, pmcid


def load_generated_annotations_combined(file_path) -> list[(dict, str)]:
    generated_annotations_by_pmcid = {}
    with open(file_path, "r") as f:
        generated_annotations_by_pmcid = json.load(f)

    results = []
    for pmcid, annotations in generated_annotations_by_pmcid.items():
        results.append((annotations, pmcid))

    return results


def benchmark_pmcid(pmcid, generated_annotations: dict):
    if pmcid not in BENCHMARK_ANNOTATIONS:
        print(f"No benchmark annotations found for PMCID: {pmcid}")
        return None  # No benchmark available

    benchmark = BENCHMARK_ANNOTATIONS[pmcid]
    scores = {}

    if "var_pheno_ann" in benchmark and len(benchmark["var_pheno_ann"]) > 0:
        gt_pheno_anns = benchmark["var_pheno_ann"]
        pred_pheno_anns = generated_annotations.get("var_pheno_ann", [])

        score = evaluate_phenotype_annotations([gt_pheno_anns, pred_pheno_anns])
        scores["var_pheno_ann"] = score

    if "var_drug_ann" in benchmark and len(benchmark["var_drug_ann"]) > 0:
        gt_drug_anns = benchmark["var_drug_ann"]
        pred_drug_anns = generated_annotations.get("var_drug_ann", [])

        score = evaluate_drug_annotations([gt_drug_anns, pred_drug_anns])
        scores["var_drug_ann"] = score

    if "var_fa_ann" in benchmark and len(benchmark["var_fa_ann"]) > 0:
        gt_fa_anns = benchmark["var_fa_ann"]
        pred_fa_anns = generated_annotations.get("var_fa_ann", [])

        score = evaluate_fa_from_articles(benchmark, generated_annotations)
        # score = evaluate_functional_analysis()

        scores["var_fa_ann"] = score

    return scores


if __name__ == "__main__":
    import argparse

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
        type=bool,
        default=False,
    )

    parser.add_argument(
        "--output_file",
        type=str,
        help="Path to the output file to save benchmark results.",
        default=f"benchmark_results/benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
    )

    args = parser.parse_args()

    if args.combined:
        data = load_generated_annotations_combined(args.generated_file)
        results = {}
        for generated_annotations, pmcid in data:
            print("Processing PMCID:", pmcid)
            scores = benchmark_pmcid(pmcid, generated_annotations)
            if scores is not None:
                print(f"Benchmark scores for PMCID {pmcid}: {scores}")
            else:
                print(f"No benchmark available for PMCID {pmcid}.")

            results[pmcid] = scores
            print("-----")

        # Save results to output file
        with open(args.output_file, "w") as f:
            json.dump(results, f, indent=4)

    else:
        generated_annotations, pmcid = load_generated_annotations_single(
            args.generated_file
        )
        scores = benchmark_pmcid(pmcid, generated_annotations)

    if scores is not None:
        print(f"Benchmark scores for PMCID {pmcid}: {scores}")
    else:
        print(f"No benchmark available for PMCID {pmcid}.")
