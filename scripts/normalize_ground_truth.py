#!/usr/bin/env python3
"""
Normalize Ground Truth Data

Normalizes variant and drug terms in the benchmark ground truth data
using PharmGKB lookups. Creates a new normalized file while preserving
the original.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from term_normalization.variant_search import VariantLookup
from term_normalization.drug_search import DrugLookup


def normalize_variant_field(variant_str: str, variant_lookup: VariantLookup) -> dict:
    """
    Normalize a variant/haplotype string.

    Returns dict with:
        - normalized: Normalized variant name (or original if not found)
        - variant_id: PharmGKB Variant ID (if found)
        - confidence: Similarity score (if available)
    """
    if not variant_str or not variant_str.strip():
        return {"normalized": variant_str, "variant_id": None, "confidence": 0.0}

    try:
        results = variant_lookup.search(variant_str.strip())
        if results and len(results) > 0:
            result = results[0]  # Get first result
            if result.id:
                return {
                    "normalized": result.normalized_term or variant_str,
                    "variant_id": result.id,
                    "confidence": result.score or 1.0,
                }
    except Exception as e:
        print(f"  Warning: Failed to normalize variant '{variant_str}': {e}")

    return {"normalized": variant_str, "variant_id": None, "confidence": 0.0}


def normalize_drug_field(drug_str: str, drug_lookup: DrugLookup) -> dict:
    """
    Normalize a drug name string.

    Returns dict with:
        - normalized: Normalized drug name (or original if not found)
        - drug_id: PharmGKB Accession ID (if found)
        - confidence: Similarity score (if available)
    """
    if not drug_str or not drug_str.strip():
        return {"normalized": drug_str, "drug_id": None, "confidence": 0.0}

    try:
        results = drug_lookup.search(drug_str.strip())
        if results and len(results) > 0:
            result = results[0]  # Get first result
            if result.id:
                return {
                    "normalized": result.normalized_term or drug_str,
                    "drug_id": result.id,
                    "confidence": result.score or 1.0,
                }
    except Exception as e:
        print(f"  Warning: Failed to normalize drug '{drug_str}': {e}")

    return {"normalized": drug_str, "drug_id": None, "confidence": 0.0}


def normalize_annotation(
    annotation: dict, variant_lookup: VariantLookup, drug_lookup: DrugLookup
) -> dict:
    """
    Add normalized fields to a single annotation.

    Adds:
        - Variant/Haplotypes_normalized: Normalized variant data
        - Drug(s)_normalized: Normalized drug data
    """
    normalized_ann = annotation.copy()

    # Normalize variant field
    if "Variant/Haplotypes" in annotation:
        variant_data = normalize_variant_field(
            annotation["Variant/Haplotypes"], variant_lookup
        )
        normalized_ann["Variant/Haplotypes_normalized"] = variant_data

    # Normalize drug field
    if "Drug(s)" in annotation:
        drug_data = normalize_drug_field(annotation["Drug(s)"], drug_lookup)
        normalized_ann["Drug(s)_normalized"] = drug_data

    return normalized_ann


def main():
    input_file = Path("persistent_data/benchmark_annotations.json")
    output_file = Path("persistent_data/benchmark_annotations_normalized.json")

    print("=" * 60)
    print("Ground Truth Normalization")
    print("=" * 60)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print()

    # Load ground truth
    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)

    with open(input_file, "r") as f:
        ground_truth = json.load(f)

    print(f"Loaded {len(ground_truth)} PMCIDs")
    print()

    # Initialize lookup services
    print("Initializing PharmGKB lookup services...")
    variant_lookup = VariantLookup()
    drug_lookup = DrugLookup()
    print("✓ Lookup services ready")
    print()

    # Normalize each PMCID
    normalized_data = {}
    total_annotations = 0
    variant_normalizations = 0
    drug_normalizations = 0

    for pmcid, pmcid_data in ground_truth.items():
        print(f"Processing {pmcid}...")
        normalized_pmcid = {}

        # Copy metadata fields (pmid, title, etc.)
        for key in ["pmid", "title"]:
            if key in pmcid_data:
                normalized_pmcid[key] = pmcid_data[key]

        # Process annotation types
        for ann_type in ["var_pheno_ann", "var_drug_ann", "var_fa_ann", "study_parameters"]:
            if ann_type not in pmcid_data:
                continue

            annotations = pmcid_data[ann_type]
            if not isinstance(annotations, list):
                normalized_pmcid[ann_type] = annotations
                continue

            normalized_annotations = []
            for ann in annotations:
                total_annotations += 1
                normalized_ann = normalize_annotation(ann, variant_lookup, drug_lookup)

                # Track successful normalizations
                if "Variant/Haplotypes_normalized" in normalized_ann:
                    if normalized_ann["Variant/Haplotypes_normalized"].get(
                        "variant_id"
                    ):
                        variant_normalizations += 1

                if "Drug(s)_normalized" in normalized_ann:
                    if normalized_ann["Drug(s)_normalized"].get("drug_id"):
                        drug_normalizations += 1

                normalized_annotations.append(normalized_ann)

            normalized_pmcid[ann_type] = normalized_annotations

        normalized_data[pmcid] = normalized_pmcid

    print()
    print("=" * 60)
    print("Normalization Summary")
    print("=" * 60)
    print(f"Total PMCIDs:             {len(ground_truth)}")
    print(f"Total annotations:        {total_annotations}")
    print(f"Variants normalized:      {variant_normalizations}")
    print(f"Drugs normalized:         {drug_normalizations}")
    print()

    # Save normalized data
    with open(output_file, "w") as f:
        json.dump(normalized_data, f, indent=2)

    print(f"✓ Saved normalized data to {output_file}")
    print()
    print("Normalization complete!")


if __name__ == "__main__":
    main()
