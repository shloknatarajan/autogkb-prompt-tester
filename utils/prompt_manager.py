"""
Prompt management utilities for loading and selecting prompts.

This module consolidates prompt selection logic used across scripts
and the FastAPI backend.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .config import PROMPTS_FILE, BEST_PROMPTS_FILE

logger = logging.getLogger(__name__)


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
            prompts_file: Path to legacy stored prompts JSON file (for fallback)
            best_prompts_file: Path to best prompts configuration JSON
        """
        self.prompts_file = prompts_file
        self.best_prompts_file = best_prompts_file
        self.prompts_dir = Path("prompts")
        self._all_prompts: Optional[List[Dict]] = None
        self._best_config: Optional[Dict[str, str]] = None

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """
        Sanitize prompt name for filesystem use.

        Replaces spaces and slashes with hyphens.

        Args:
            name: Original prompt name

        Returns:
            Sanitized name safe for filesystem

        Examples:
            "from docs" -> "from-docs"
            "llm generated" -> "llm-generated"
        """
        return name.replace(" ", "-").replace("/", "-")

    def _scan_prompt_directories(self) -> List[Dict]:
        """
        Scan prompts/ folder and load all prompts from folder structure.

        Returns:
            List of prompt dictionaries with same structure as legacy JSON

        Note:
            - Prompts stored in: prompts/{task}/{sanitized-name}/
            - Each prompt folder contains: prompt.md, schema.json, config.json
            - Original names (with spaces) are preserved in returned dict
        """
        prompts = []

        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory not found: {self.prompts_dir}")
            return []

        # Iterate through task directories
        for task_dir in self.prompts_dir.iterdir():
            if not task_dir.is_dir():
                continue

            task = task_dir.name

            # Iterate through prompt directories within task
            for prompt_dir in task_dir.iterdir():
                if not prompt_dir.is_dir():
                    continue

                sanitized_name = prompt_dir.name

                # Check for required files
                prompt_file = prompt_dir / "prompt.md"
                schema_file = prompt_dir / "schema.json"
                config_file = prompt_dir / "config.json"

                if not all([prompt_file.exists(), schema_file.exists(), config_file.exists()]):
                    missing = []
                    if not prompt_file.exists():
                        missing.append("prompt.md")
                    if not schema_file.exists():
                        missing.append("schema.json")
                    if not config_file.exists():
                        missing.append("config.json")
                    logger.warning(
                        f"Incomplete prompt: {task}/{sanitized_name} (missing: {', '.join(missing)})"
                    )
                    continue

                try:
                    # Read prompt text
                    prompt_text = prompt_file.read_text(encoding="utf-8")

                    # Read schema
                    with open(schema_file, "r", encoding="utf-8") as f:
                        schema = json.load(f)

                    # Read config
                    with open(config_file, "r", encoding="utf-8") as f:
                        config = json.load(f)

                    # Get original name from config.json, fallback to sanitized name
                    original_name = config.get("name", sanitized_name)

                    # Build prompt object matching legacy format
                    prompts.append({
                        "task": task,
                        "name": original_name,
                        "prompt": prompt_text,
                        "response_format": schema,
                        "model": config.get("model", "gpt-4o-mini"),
                        "temperature": config.get("temperature", 0.0),
                        "timestamp": config.get("timestamp", "")
                    })

                except Exception as e:
                    logger.error(f"Error loading prompt {task}/{sanitized_name}: {e}")
                    continue

        return prompts

    def load_prompts(self, force_reload: bool = False) -> List[Dict]:
        """
        Load all stored prompts from folder structure.

        Attempts to load from prompts/ folder structure first.
        Falls back to legacy stored_prompts.json if folder doesn't exist.

        Args:
            force_reload: If True, reload from disk even if cached

        Returns:
            List of prompt dictionaries with structure:
            [{
                "task": str,
                "name": str,
                "prompt": str,
                "model": str,
                "response_format": dict,
                "temperature": float,
                "timestamp": str
            }, ...]

        Raises:
            FileNotFoundError: If neither prompts folder nor legacy file exists
        """
        if self._all_prompts is not None and not force_reload:
            return self._all_prompts

        # Try to load from folder structure first
        if self.prompts_dir.exists():
            logger.info(f"Loading prompts from folder structure: {self.prompts_dir}")
            self._all_prompts = self._scan_prompt_directories()
            return self._all_prompts

        # Fallback to legacy JSON file
        logger.warning(
            f"Prompts folder not found ({self.prompts_dir}), "
            f"falling back to legacy file: {self.prompts_file}"
        )

        if not os.path.exists(self.prompts_file):
            raise FileNotFoundError(
                f"Neither prompts folder ({self.prompts_dir}) "
                f"nor legacy file ({self.prompts_file}) found"
            )

        with open(self.prompts_file, "r", encoding="utf-8") as f:
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

    def save_prompt(
        self,
        task: str,
        name: str,
        prompt: str,
        response_format: Dict,
        model: str = "gpt-4o-mini",
        temperature: float = 0.0
    ) -> None:
        """
        Save a prompt to the folder structure.

        Creates or updates a prompt by writing to:
        - prompts/{task}/{sanitized-name}/prompt.md
        - prompts/{task}/{sanitized-name}/schema.json
        - prompts/{task}/{sanitized-name}/config.json

        Args:
            task: Task identifier (e.g., "var-pheno")
            name: Prompt name (e.g., "structured", "from docs")
            prompt: Prompt text content
            response_format: JSON schema for response format
            model: Model name (default: "gpt-4o-mini")
            temperature: Temperature setting (default: 0.0)

        Note:
            - Name sanitization is automatic (spaces → hyphens)
            - Creates directories if they don't exist
            - Overwrites existing prompts with same task/name
            - Clears cache after saving
        """
        # Sanitize name for filesystem
        safe_name = self._sanitize_name(name)

        # Create directory
        prompt_dir = self.prompts_dir / task / safe_name
        prompt_dir.mkdir(parents=True, exist_ok=True)

        # Write prompt.md
        prompt_file = prompt_dir / "prompt.md"
        prompt_file.write_text(prompt, encoding="utf-8")

        # Write schema.json
        schema_file = prompt_dir / "schema.json"
        schema_file.write_text(
            json.dumps(response_format, indent=2), encoding="utf-8"
        )

        # Write config.json (include original name to preserve spaces)
        config_file = prompt_dir / "config.json"
        config_data = {
            "name": name,  # Store original name with spaces
            "model": model,
            "temperature": temperature,
            "timestamp": datetime.now().isoformat()
        }
        config_file.write_text(
            json.dumps(config_data, indent=2), encoding="utf-8"
        )

        # Clear cache to force reload
        self._all_prompts = None

        logger.info(f"Saved prompt: {task}/{name} (folder: {safe_name})")

    def delete_prompt(self, task: str, name: str) -> bool:
        """
        Delete a prompt from the folder structure.

        Args:
            task: Task identifier (e.g., "var-pheno")
            name: Prompt name (e.g., "structured", "from docs")

        Returns:
            True if deleted successfully, False if not found

        Note:
            - Deletes the entire prompt folder and all contents
            - Name sanitization is automatic
            - Clears cache after deletion
        """
        import shutil

        # Sanitize name for filesystem
        safe_name = self._sanitize_name(name)

        # Find prompt directory
        prompt_dir = self.prompts_dir / task / safe_name

        if not prompt_dir.exists():
            logger.warning(f"Prompt not found for deletion: {task}/{name}")
            return False

        try:
            # Delete the entire folder
            shutil.rmtree(prompt_dir)

            # Clear cache to force reload
            self._all_prompts = None

            logger.info(f"Deleted prompt: {task}/{name} (folder: {safe_name})")
            return True

        except Exception as e:
            logger.error(f"Error deleting prompt {task}/{name}: {e}")
            return False

    def rename_prompt(self, task: str, old_name: str, new_name: str) -> bool:
        """
        Rename a prompt in the folder structure.

        Args:
            task: Task identifier (e.g., "var-pheno")
            old_name: Current prompt name
            new_name: New prompt name

        Returns:
            True if renamed successfully, False if not found or new name exists

        Note:
            - Renames the folder (with sanitized names)
            - Updates config.json to store new original name
            - Clears cache after renaming
        """
        # Sanitize both names for filesystem
        old_safe_name = self._sanitize_name(old_name)
        new_safe_name = self._sanitize_name(new_name)

        # Find old prompt directory
        old_prompt_dir = self.prompts_dir / task / old_safe_name
        new_prompt_dir = self.prompts_dir / task / new_safe_name

        if not old_prompt_dir.exists():
            logger.warning(f"Prompt not found for renaming: {task}/{old_name}")
            return False

        if new_prompt_dir.exists():
            logger.warning(
                f"Cannot rename to {task}/{new_name}: destination already exists"
            )
            return False

        try:
            # Rename the folder
            old_prompt_dir.rename(new_prompt_dir)

            # Update config.json with new original name
            config_file = new_prompt_dir / "config.json"
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)

                config["name"] = new_name
                config["timestamp"] = datetime.now().isoformat()

                with open(config_file, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2)

            # Clear cache to force reload
            self._all_prompts = None

            logger.info(
                f"Renamed prompt: {task}/{old_name} -> {task}/{new_name} "
                f"(folder: {old_safe_name} -> {new_safe_name})"
            )
            return True

        except Exception as e:
            logger.error(f"Error renaming prompt {task}/{old_name} to {new_name}: {e}")
            return False

    def update_best_prompts(self, best_prompts: Dict[str, str]) -> bool:
        """
        Update the best prompts configuration file.

        Args:
            best_prompts: Dictionary mapping task -> prompt name
                         Example: {"var-pheno": "structured", "var-drug": "improved_v1"}

        Returns:
            True if updated successfully, False otherwise

        Note:
            - Validates that all referenced prompts exist
            - Writes to best_prompts.json
            - Clears cache after update
        """
        try:
            # Validate that all referenced prompts exist
            all_prompts = self.load_prompts()
            prompt_set = {(p["task"], p["name"]) for p in all_prompts}

            for task, name in best_prompts.items():
                if (task, name) not in prompt_set:
                    logger.warning(
                        f"Best prompt validation failed: {task}/{name} does not exist"
                    )
                    return False

            # Write to file
            with open(self.best_prompts_file, "w", encoding="utf-8") as f:
                json.dump(best_prompts, f, indent=2)

            # Clear cache
            self._best_config = None

            logger.info(f"Updated best prompts configuration: {best_prompts}")
            return True

        except Exception as e:
            logger.error(f"Error updating best prompts: {e}")
            return False
