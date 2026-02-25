"""
Output file management utilities.

This module provides consistent functions for saving, loading, and combining
annotation output files across the application.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List

from .config import OUTPUT_DIR


def save_output(
    pmcid: str,
    data: Dict,
    output_dir: str = OUTPUT_DIR,
    include_timestamp: bool = True,
) -> str:
    """
    Save annotation output for a single PMCID.

    Args:
        pmcid: PubMed Central ID
        data: Output dictionary containing annotations
        output_dir: Directory to save output (default: OUTPUT_DIR)
        include_timestamp: Whether to add timestamp to data

    Returns:
        Path to saved file

    Example:
        >>> output = {
        ...     "var_pheno_ann": [...],
        ...     "var_drug_ann": [...],
        ...     "prompts_used": {...}
        ... }
        >>> filepath = save_output("PMC123456", output)
        >>> print(filepath)
        "outputs/PMC123456.json"
    """
    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)

    # Add timestamp if requested
    if include_timestamp and "timestamp" not in data:
        data["timestamp"] = datetime.now().isoformat()

    # Ensure PMCID is in the data
    if "pmcid" not in data:
        data["pmcid"] = pmcid

    # Construct filepath
    filepath = os.path.join(output_dir, f"{pmcid}.json")

    # Save to file
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    return filepath


def load_output(pmcid: str, output_dir: str = OUTPUT_DIR) -> Dict:
    """
    Load annotation output for a single PMCID.

    Args:
        pmcid: PubMed Central ID
        output_dir: Directory containing outputs

    Returns:
        Output dictionary

    Raises:
        FileNotFoundError: If output file doesn't exist
    """
    filepath = os.path.join(output_dir, f"{pmcid}.json")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Output file not found: {filepath}")

    with open(filepath, "r") as f:
        return json.load(f)


def load_output_by_path(filepath: str) -> Dict:
    """
    Load annotation output from an explicit file path.

    Args:
        filepath: Path to output JSON file

    Returns:
        Output dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Output file not found: {filepath}")

    with open(filepath, "r") as f:
        return json.load(f)


def combine_outputs(
    input_dir: str,
    output_file: Optional[str] = None,
    pmcids: Optional[List[str]] = None,
) -> Dict[str, Dict]:
    """
    Combine individual PMCID output files into a single JSON file.

    Args:
        input_dir: Directory containing individual PMCID JSON files
        output_file: Path to save combined output (if None, returns dict only)
        pmcids: Optional list of specific PMCIDs to combine (default: all .json files)

    Returns:
        Dictionary mapping PMCID to output data:
        {
            "PMC123": {entire_output},
            "PMC456": {entire_output},
            ...
        }

    Example:
        >>> combined = combine_outputs(
        ...     "outputs/pipeline_run_20240115",
        ...     "outputs/combined.json"
        ... )
        >>> print(len(combined))
        35
    """
    combined = {}

    # Get list of files to combine
    if pmcids:
        files = [f"{pmcid}.json" for pmcid in pmcids]
    else:
        # Find all JSON files in directory
        files = [f for f in os.listdir(input_dir) if f.endswith(".json")]

    # Load each file
    for filename in files:
        filepath = os.path.join(input_dir, filename)

        if not os.path.exists(filepath):
            print(f"Warning: File not found, skipping: {filepath}")
            continue

        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            # Extract PMCID from data or filename
            pmcid = data.get("pmcid")
            if not pmcid:
                # Fall back to filename (remove .json extension)
                pmcid = os.path.splitext(filename)[0]

            combined[pmcid] = data

        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in {filepath}: {e}")
            continue
        except Exception as e:
            print(f"Warning: Error loading {filepath}: {e}")
            continue

    # Save to file if output path provided
    if output_file:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(combined, f, indent=2)

        print(f"Combined {len(combined)} outputs to {output_file}")

    return combined


def list_outputs(output_dir: str = OUTPUT_DIR) -> List[Dict]:
    """
    List all output files in a directory with metadata.

    Args:
        output_dir: Directory to scan for outputs

    Returns:
        List of dictionaries with file metadata:
        [{
            "filename": "PMC123.json",
            "pmcid": "PMC123",
            "created": "2024-01-15T10:30:00",
            "modified": "2024-01-15T10:30:00",
            "size": 12345
        }, ...]
    """
    if not os.path.exists(output_dir):
        return []

    outputs = []

    for filename in os.listdir(output_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(output_dir, filename)
            stat = os.stat(filepath)

            # Try to extract PMCID
            pmcid = os.path.splitext(filename)[0]

            outputs.append(
                {
                    "filename": filename,
                    "pmcid": pmcid,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "size": stat.st_size,
                }
            )

    # Sort by modification time, newest first
    outputs.sort(key=lambda x: x["modified"], reverse=True)

    return outputs


def validate_output_structure(data: Dict) -> List[str]:
    """
    Validate that an output dictionary has expected structure.

    Args:
        data: Output dictionary to validate

    Returns:
        List of validation warnings (empty if valid)
    """
    warnings = []

    # Check for expected top-level keys
    expected_keys = ["pmcid", "timestamp", "prompts_used"]
    for key in expected_keys:
        if key not in data:
            warnings.append(f"Missing expected key: {key}")

    # Check for at least one annotation type
    annotation_keys = ["var_pheno_ann", "var_drug_ann", "var_fa_ann"]
    has_annotations = any(key in data for key in annotation_keys)
    if not has_annotations:
        warnings.append("No annotation arrays found (var_pheno_ann, var_drug_ann, var_fa_ann)")

    # Check that annotation values are lists
    for key in annotation_keys:
        if key in data and not isinstance(data[key], list):
            warnings.append(f"{key} should be a list, got {type(data[key])}")

    return warnings
