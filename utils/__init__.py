"""
Shared utilities for AutoGKB Prompt Tester.

This package contains common functionality used across both the FastAPI backend
and standalone CLI scripts, eliminating code duplication and ensuring consistency.
"""

from .config import (
    PROMPTS_FILE,
    BEST_PROMPTS_FILE,
    OUTPUT_DIR,
    BENCHMARK_RESULTS_DIR,
    GROUND_TRUTH_FILE,
    GROUND_TRUTH_NORMALIZED_FILE,
    MARKDOWN_DIR,
)
from .benchmark_runner import BenchmarkRunner
from .prompt_manager import PromptManager
from .citation_generator import CITATION_PROMPT_TEMPLATE, generate_citations
from .output_manager import save_output, load_output, combine_outputs
from .normalization import normalize_outputs_in_directory
from .cost import (
    MODEL_PRICING,
    UsageInfo,
    CostTracker,
    calculate_cost,
    extract_usage_from_response,
)

__all__ = [
    # Config
    "PROMPTS_FILE",
    "BEST_PROMPTS_FILE",
    "OUTPUT_DIR",
    "BENCHMARK_RESULTS_DIR",
    "GROUND_TRUTH_FILE",
    "GROUND_TRUTH_NORMALIZED_FILE",
    "MARKDOWN_DIR",
    # Classes
    "BenchmarkRunner",
    "PromptManager",
    # Functions
    "generate_citations",
    "save_output",
    "load_output",
    "combine_outputs",
    "normalize_outputs_in_directory",
    # Constants
    "CITATION_PROMPT_TEMPLATE",
    "MODEL_PRICING",
    # Cost tracking
    "UsageInfo",
    "CostTracker",
    "calculate_cost",
    "extract_usage_from_response",
]
