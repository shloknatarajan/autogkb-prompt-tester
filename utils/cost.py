"""
Cost tracking utilities for LLM API usage.

This module provides functionality for tracking token usage and calculating
costs across different LLM providers and models.
"""

from dataclasses import dataclass, field
from typing import Dict, Any
import litellm


# Model pricing per 1M tokens (input, output) in USD
# Source: Provider pricing pages as of Dec 2025
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    # OpenAI models
    "openai/gpt-4o": {"input": 2.50, "output": 10.00},
    "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "openai/gpt-5-mini": {"input": 0.25, "output": 2.00},
    "openai/gpt-5.1": {"input": 1.25, "output": 10.00},
    "openai/gpt-5.2": {"input": 1.75, "output": 14.00},
    # Anthropic models
    "anthropic/claude-opus-4-5-20251101": {"input": 15.00, "output": 75.00},
    "anthropic/claude-sonnet-4-5-20250929": {"input": 3.00, "output": 15.00},
    "anthropic/claude-3-5-sonnet-20240620": {"input": 3.00, "output": 15.00},
    "anthropic/claude-haiku-4-5-20251001": {"input": 1.00, "output": 5.00},
    "anthropic/claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    # Google models
    "gemini/gemini-2.0-flash": {"input": 0.075, "output": 0.30},
    "gemini/gemini-1.5-pro": {"input": 1.25, "output": 5.00},
}


@dataclass
class UsageInfo:
    """Token usage information from a single LLM call."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    model: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": round(self.cost_usd, 6),
            "model": self.model,
        }


@dataclass
class CostTracker:
    """
    Accumulates costs across multiple LLM calls for a single document.

    Usage:
        tracker = CostTracker()
        # After each LLM call:
        tracker.add_usage("var-pheno", usage_info)
        tracker.add_usage("citations", usage_info)
        # Get summary:
        summary = tracker.get_summary()
    """

    by_task: Dict[str, UsageInfo] = field(default_factory=dict)
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_cost_usd: float = 0.0

    def add_usage(self, task_name: str, usage: UsageInfo) -> None:
        """Add usage from a single LLM call to the tracker."""
        if task_name not in self.by_task:
            self.by_task[task_name] = UsageInfo()

        task_usage = self.by_task[task_name]
        task_usage.prompt_tokens += usage.prompt_tokens
        task_usage.completion_tokens += usage.completion_tokens
        task_usage.total_tokens += usage.total_tokens
        task_usage.cost_usd += usage.cost_usd
        task_usage.model = usage.model

        self.total_prompt_tokens += usage.prompt_tokens
        self.total_completion_tokens += usage.completion_tokens
        self.total_cost_usd += usage.cost_usd

    def get_summary(self) -> Dict[str, Any]:
        """Return a dictionary summary suitable for JSON serialization."""
        return {
            "total_cost_usd": round(self.total_cost_usd, 6),
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "by_task": {task: usage.to_dict() for task, usage in self.by_task.items()},
        }


def calculate_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> float:
    """
    Calculate cost in USD for given token counts.

    Uses LiteLLM's completion_cost if available, falls back to local pricing table.

    Args:
        model: Model identifier (e.g., "openai/gpt-4o")
        prompt_tokens: Number of input tokens
        completion_tokens: Number of output tokens

    Returns:
        Cost in USD
    """
    # Try LiteLLM's built-in cost calculation first
    try:
        cost = litellm.completion_cost(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
        if cost is not None and cost > 0:
            return cost
    except Exception:
        pass

    # Fall back to local pricing table
    if model in MODEL_PRICING:
        pricing = MODEL_PRICING[model]
        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    # Unknown model - return 0
    return 0.0


def extract_usage_from_response(response: Any, model: str) -> UsageInfo:
    """
    Extract usage information from a LiteLLM response object.

    Args:
        response: LiteLLM completion response
        model: Model identifier for cost calculation

    Returns:
        UsageInfo object with token counts and cost
    """
    usage = getattr(response, "usage", None)
    if usage is None:
        return UsageInfo(model=model)

    prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
    completion_tokens = getattr(usage, "completion_tokens", 0) or 0
    total_tokens = getattr(usage, "total_tokens", 0) or (
        prompt_tokens + completion_tokens
    )

    cost = calculate_cost(model, prompt_tokens, completion_tokens)

    return UsageInfo(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        cost_usd=cost,
        model=model,
    )
