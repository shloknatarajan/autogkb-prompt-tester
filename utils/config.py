"""
Shared configuration constants for AutoGKB Prompt Tester.

This module provides a single source of truth for file paths and directories
used across the application, preventing inconsistencies and hardcoded paths.
"""

import os

# File paths
PROMPTS_FILE = "stored_prompts.json"  # Legacy file (for fallback)
PROMPTS_BACKUP_FILE = "stored_prompts.json.backup"  # Migration backup
BEST_PROMPTS_FILE = "best_prompts.json"

# Directories
PROMPTS_DIR = "prompts"  # Prompts folder structure
OUTPUT_DIR = "outputs"
BENCHMARK_RESULTS_DIR = "benchmark_results"
MARKDOWN_DIR = "persistent_data/benchmark_articles_md"
PERSISTENT_DATA_DIR = "persistent_data"
LOGS_DIR = "logs"

# Ground truth files
GROUND_TRUTH_FILE = os.path.join(PERSISTENT_DATA_DIR, "benchmark_annotations.json")
GROUND_TRUTH_NORMALIZED_FILE = os.path.join(
    PERSISTENT_DATA_DIR, "benchmark_annotations_normalized.json"
)
BENCHMARK_PMCIDS_FILE = os.path.join(PERSISTENT_DATA_DIR, "benchmark_pmcids.txt")

# Normalization data
TERM_LOOKUP_DIR = "data/term_lookup_info"
VARIANTS_TSV = os.path.join(TERM_LOOKUP_DIR, "variants.tsv")
DRUGS_TSV = os.path.join(TERM_LOOKUP_DIR, "drugs.tsv")
