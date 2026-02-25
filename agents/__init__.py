"""
Autonomous Prompt Optimization Agent for AutoGKB.

This module provides an autonomous agent using Claude that iteratively
improves prompts based on benchmark analysis.
"""

from .prompt_optimizer import PromptOptimizationAgent, OptimizationConfig, OptimizationResult

__all__ = ["PromptOptimizationAgent", "OptimizationConfig", "OptimizationResult"]
