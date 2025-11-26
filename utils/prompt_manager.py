"""
Prompt management utilities for loading and selecting prompts.

This module consolidates prompt selection logic used across scripts
and the FastAPI backend.
"""

import json
import os
from typing import Dict, List, Optional

from .config import PROMPTS_FILE, BEST_PROMPTS_FILE


class PromptManager:
    """
    Manages prompt loading and selection.

    Features:
    - Load all stored prompts from JSON
    - Load best prompts configuration
    - Match tasks to their best prompts
    - Validate prompt existence
    """

    def __init__(
        self, prompts_file: str = PROMPTS_FILE, best_prompts_file: str = BEST_PROMPTS_FILE
    ):
        """
        Initialize prompt manager.

        Args:
            prompts_file: Path to stored prompts JSON file
            best_prompts_file: Path to best prompts configuration JSON
        """
        self.prompts_file = prompts_file
        self.best_prompts_file = best_prompts_file
        self._all_prompts: Optional[List[Dict]] = None
        self._best_config: Optional[Dict[str, str]] = None

    def load_prompts(self, force_reload: bool = False) -> List[Dict]:
        """
        Load all stored prompts from JSON file.

        Args:
            force_reload: If True, reload from file even if cached

        Returns:
            List of prompt dictionaries with structure:
            [{
                "task": str,
                "name": str,
                "prompt": str,
                "model": str,
                "response_format": dict,
                "output": any,
                "timestamp": str
            }, ...]

        Raises:
            FileNotFoundError: If prompts file doesn't exist
        """
        if self._all_prompts is not None and not force_reload:
            return self._all_prompts

        if not os.path.exists(self.prompts_file):
            raise FileNotFoundError(f"Prompts file not found: {self.prompts_file}")

        with open(self.prompts_file, "r") as f:
            self._all_prompts = json.load(f)

        return self._all_prompts

    def load_best_config(self, force_reload: bool = False) -> Dict[str, str]:
        """
        Load best prompts configuration.

        Args:
            force_reload: If True, reload from file even if cached

        Returns:
            Dictionary mapping task name to best prompt name:
            {
                "var-pheno": "structured",
                "var-drug": "from docs",
                "var-fa": "from readme",
                ...
            }

        Raises:
            FileNotFoundError: If best prompts file doesn't exist
        """
        if self._best_config is not None and not force_reload:
            return self._best_config

        if not os.path.exists(self.best_prompts_file):
            raise FileNotFoundError(
                f"Best prompts file not found: {self.best_prompts_file}"
            )

        with open(self.best_prompts_file, "r") as f:
            self._best_config = json.load(f)

        return self._best_config

    def get_best_prompts(self) -> Dict[str, Dict]:
        """
        Get detailed information for all best prompts.

        Returns:
            Dictionary mapping task to prompt details:
            {
                "var-pheno": {
                    "task": "var-pheno",
                    "name": "structured",
                    "prompt": "...",
                    "model": "gpt-4o-mini",
                    "response_format": {...},
                    ...
                },
                ...
            }

        Raises:
            FileNotFoundError: If required files don't exist
            ValueError: If a configured best prompt is not found
        """
        all_prompts = self.load_prompts()
        best_config = self.load_best_config()

        prompt_details_map = {}

        for task, prompt_name in best_config.items():
            # Find matching prompt
            matching_prompts = [
                p
                for p in all_prompts
                if p.get("task") == task and p.get("name") == prompt_name
            ]

            if not matching_prompts:
                raise ValueError(
                    f"Best prompt not found: task='{task}', name='{prompt_name}'"
                )

            # Use the first match (should only be one)
            prompt_details_map[task] = matching_prompts[0]

        return prompt_details_map

    def get_prompt_by_task_and_name(self, task: str, name: str) -> Optional[Dict]:
        """
        Get a specific prompt by task and name.

        Args:
            task: Task identifier (e.g., "var-pheno")
            name: Prompt name (e.g., "structured")

        Returns:
            Prompt dictionary or None if not found
        """
        all_prompts = self.load_prompts()

        for prompt in all_prompts:
            if prompt.get("task") == task and prompt.get("name") == name:
                return prompt

        return None

    def get_prompts_by_task(self, task: str) -> List[Dict]:
        """
        Get all prompts for a specific task.

        Args:
            task: Task identifier (e.g., "var-pheno")

        Returns:
            List of prompt dictionaries for the task
        """
        all_prompts = self.load_prompts()
        return [p for p in all_prompts if p.get("task") == task]

    def get_tasks(self) -> List[str]:
        """
        Get list of all unique tasks in stored prompts.

        Returns:
            List of task identifiers
        """
        all_prompts = self.load_prompts()
        tasks = set(p.get("task") for p in all_prompts if p.get("task"))
        return sorted(tasks)

    def validate_best_prompts(self) -> Dict[str, bool]:
        """
        Validate that all configured best prompts exist.

        Returns:
            Dictionary mapping task to validation status (True if found)
        """
        all_prompts = self.load_prompts()
        best_config = self.load_best_config()

        validation = {}

        for task, prompt_name in best_config.items():
            matching = [
                p
                for p in all_prompts
                if p.get("task") == task and p.get("name") == prompt_name
            ]
            validation[task] = len(matching) > 0

        return validation
