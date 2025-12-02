"""
Term normalization utilities for annotation outputs.

This module provides functions to normalize terms in output files using
the term_normalization package, consolidating logic from multiple scripts.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from term_normalization.term_lookup import normalize_annotation


def normalize_output_file(
    input_file: str, output_file: str, verbose: bool = True
) -> bool:
    """
    Normalize terms in a single output file.

    Args:
        input_file: Path to input JSON file
        output_file: Path to save normalized output
        verbose: Whether to print status messages

    Returns:
        True if successful, False if error occurred

    Example:
        >>> success = normalize_output_file(
        ...     "outputs/PMC123.json",
        ...     "outputs/PMC123_normalized.json"
        ... )
        >>> print(success)
        True
    """
    try:
        normalize_annotation(Path(input_file), Path(output_file))
        if verbose:
            print(f"✓ Normalized: {input_file}")
        return True
    except Exception as e:
        if verbose:
            print(f"✗ Failed to normalize {input_file}: {e}")
        return False


def normalize_outputs_in_directory(
    directory: str, in_place: bool = True, verbose: bool = True
) -> Tuple[int, int]:
    """
    Normalize all JSON output files in a directory.

    Args:
        directory: Directory containing output JSON files
        in_place: If True, overwrite original files; if False, create *_normalized.json
        verbose: Whether to print progress messages

    Returns:
        Tuple of (successful_count, failed_count)

    Example:
        >>> success, failed = normalize_outputs_in_directory(
        ...     "outputs/pipeline_run_20240115"
        ... )
        >>> print(f"Normalized {success} files, {failed} failed")
        Normalized 34 files, 1 failed
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")

    # Find all JSON files
    json_files = list(Path(directory).glob("*.json"))

    # Skip combined files
    json_files = [f for f in json_files if "combined" not in f.name]

    if verbose:
        print(f"Found {len(json_files)} files to normalize in {directory}")

    successful = 0
    failed = 0

    for input_file in json_files:
        try:
            if in_place:
                # Normalize in place using temp file
                temp_file = input_file.with_suffix(".json.tmp")
                normalize_annotation(input_file, temp_file)
                temp_file.replace(input_file)
            else:
                # Create separate normalized file
                output_file = input_file.with_stem(f"{input_file.stem}_normalized")
                normalize_annotation(input_file, output_file)

            successful += 1
            if verbose:
                print(f"  ✓ Normalized: {input_file.name}")

        except Exception as e:
            failed += 1
            if verbose:
                print(f"  ✗ Failed: {input_file.name} - {e}")

    if verbose:
        print(f"Normalization complete: {successful} successful, {failed} failed")

    return successful, failed


def normalize_output_dict(output_data: Dict) -> Dict:
    """
    Normalize terms in an output dictionary in memory.

    This is useful when you have an output dict already loaded
    and want to normalize it without file I/O.

    Args:
        output_data: Output dictionary with annotations

    Returns:
        Normalized output dictionary (new copy)

    Note:
        This function saves to a temp file, normalizes it, and loads it back.
        It's not as efficient as direct in-memory normalization but ensures
        consistency with the file-based normalization logic.
    """
    import tempfile

    # Create temp files
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as input_tmp:
        json.dump(output_data, input_tmp, indent=2)
        input_path = input_tmp.name

    output_path = input_path.replace(".json", "_normalized.json")

    try:
        # Normalize via file
        normalize_annotation(input_path, output_path)

        # Load normalized result
        with open(output_path, "r") as f:
            normalized_data = json.load(f)

        return normalized_data

    finally:
        # Clean up temp files
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)


def check_normalization_status(output_file: str) -> bool:
    """
    Check if an output file has already been normalized.

    Args:
        output_file: Path to output JSON file

    Returns:
        True if file appears to be normalized (has term_mappings), False otherwise
    """
    try:
        with open(output_file, "r") as f:
            data = json.load(f)

        # Check for normalization indicators
        has_term_mappings = "term_mappings" in data

        # Check if any annotations have _normalized fields
        has_normalized_fields = False
        for ann_type in ["var_pheno_ann", "var_drug_ann", "var_fa_ann"]:
            if ann_type in data and isinstance(data[ann_type], list):
                for ann in data[ann_type]:
                    if any(key.endswith("_normalized") for key in ann.keys()):
                        has_normalized_fields = True
                        break

        return has_term_mappings or has_normalized_fields

    except Exception:
        return False


def get_normalization_stats(output_file: str) -> Dict:
    """
    Get statistics about normalization in an output file.

    Args:
        output_file: Path to output JSON file

    Returns:
        Dictionary with normalization statistics:
        {
            "is_normalized": bool,
            "term_mappings_count": int,
            "normalized_fields": list[str],
            "annotations_with_normalized_terms": int
        }
    """
    stats = {
        "is_normalized": False,
        "term_mappings_count": 0,
        "normalized_fields": [],
        "annotations_with_normalized_terms": 0,
    }

    try:
        with open(output_file, "r") as f:
            data = json.load(f)

        # Check term_mappings
        if "term_mappings" in data:
            stats["is_normalized"] = True
            stats["term_mappings_count"] = len(data.get("term_mappings", {}))

        # Check for normalized fields
        normalized_fields = set()
        ann_count = 0

        for ann_type in ["var_pheno_ann", "var_drug_ann", "var_fa_ann"]:
            if ann_type in data and isinstance(data[ann_type], list):
                for ann in data[ann_type]:
                    has_normalized = False
                    for key in ann.keys():
                        if key.endswith("_normalized"):
                            normalized_fields.add(key)
                            has_normalized = True
                    if has_normalized:
                        ann_count += 1

        stats["normalized_fields"] = sorted(normalized_fields)
        stats["annotations_with_normalized_terms"] = ann_count

    except Exception as e:
        stats["error"] = str(e)

    return stats


def _normalize_single_file(input_file: Path, in_place: bool) -> Tuple[str, bool, Optional[str]]:
    """
    Normalize a single file (internal helper for async wrapper).

    Args:
        input_file: Path to the file
        in_place: Whether to overwrite the original file

    Returns:
        Tuple of (filename, success, error_message)
    """
    try:
        if in_place:
            temp_file = input_file.with_suffix(".json.tmp")
            normalize_annotation(input_file, temp_file)
            temp_file.replace(input_file)
        else:
            output_file = input_file.with_stem(f"{input_file.stem}_normalized")
            normalize_annotation(input_file, output_file)
        return (input_file.name, True, None)
    except Exception as e:
        return (input_file.name, False, str(e))


async def normalize_single_file_async(
    file_path: Path, in_place: bool = True
) -> Tuple[str, bool, Optional[str]]:
    """
    Normalize a single file asynchronously.

    This function is designed for use in pipelines where normalization
    should run concurrently with other tasks (e.g., LLM generation).

    Args:
        file_path: Path to the JSON file to normalize
        in_place: Whether to overwrite the original file (default True)

    Returns:
        Tuple of (filename, success, error_message)

    Note:
        PharmGKB API calls are rate-limited by the global semaphore
        in term_normalization.cache (max 2 concurrent API calls).
    """
    return await asyncio.to_thread(_normalize_single_file, file_path, in_place)


async def normalize_outputs_in_directory_async(
    directory: str,
    in_place: bool = True,
    concurrency: int = 10,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
) -> Tuple[int, int]:
    """
    Normalize all JSON output files in a directory concurrently.

    Args:
        directory: Directory containing output JSON files
        in_place: If True, overwrite original files; if False, create *_normalized.json
        concurrency: Maximum number of files to process concurrently (default 10)
        progress_callback: Optional callback called after each file with (filename, completed, total)

    Returns:
        Tuple of (successful_count, failed_count)

    Note:
        PharmGKB API calls are rate-limited separately (max 2 concurrent) via
        the global semaphore in term_normalization.cache. This concurrency
        parameter controls file-level parallelism.
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")

    # Find all JSON files (excluding combined files)
    json_files = [
        f for f in Path(directory).glob("*.json")
        if "combined" not in f.name
    ]

    if not json_files:
        return (0, 0)

    total = len(json_files)
    successful = 0
    failed = 0
    completed = 0

    # Semaphore for file-level concurrency
    semaphore = asyncio.Semaphore(concurrency)

    async def process_file(input_file: Path) -> Tuple[str, bool, Optional[str]]:
        async with semaphore:
            # Run synchronous normalization in thread pool
            return await asyncio.to_thread(_normalize_single_file, input_file, in_place)

    # Create tasks for all files
    tasks = [process_file(f) for f in json_files]

    # Process as they complete for real-time progress reporting
    for coro in asyncio.as_completed(tasks):
        filename, success, error = await coro
        completed += 1

        if success:
            successful += 1
        else:
            failed += 1

        if progress_callback:
            progress_callback(filename, completed, total)

    return (successful, failed)
