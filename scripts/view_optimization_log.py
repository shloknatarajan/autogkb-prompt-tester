#!/usr/bin/env python3
"""
View optimization logs in a human-readable format.

Usage:
    pixi run python scripts/view_optimization_log.py logs/optimization/var-pheno_20251216_123456.jsonl
    pixi run python scripts/view_optimization_log.py --latest var-pheno
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent


def format_iteration(entry: dict) -> str:
    """Format a single iteration entry for display."""
    lines = []

    iteration = entry.get("iteration", "?")
    lines.append(f"\n{'='*60}")
    lines.append(f"ITERATION {iteration}")
    lines.append(f"{'='*60}")

    if "timestamp" in entry:
        lines.append(f"Time: {entry['timestamp']}")

    # Version change
    before = entry.get("prompt_version_before", "?")
    after = entry.get("prompt_version_after", "?")
    lines.append(f"Prompt: {before} -> {after}")

    # Scores
    score_before = entry.get("score_before", "?")
    score_after = entry.get("score_after", "?")
    if score_after and score_after != "?" and score_before != "?":
        diff = score_after - score_before
        symbol = "+" if diff >= 0 else ""
        lines.append(f"Score: {score_before} -> {score_after} ({symbol}{diff:.1f})")
    else:
        lines.append(f"Score before: {score_before}")

    # Analyzed PMCIDs
    pmcids = entry.get("worst_pmcids_analyzed", [])
    if pmcids:
        lines.append(f"\nAnalyzed PMCIDs: {', '.join(pmcids)}")

    # Error patterns
    patterns = entry.get("error_patterns_found", [])
    if patterns:
        lines.append(f"\nError Patterns Found ({len(patterns)}):")
        for i, p in enumerate(patterns, 1):
            lines.append(f"  {i}. {p.get('pattern', 'Unknown')}")
            if p.get("frequency"):
                lines.append(f"     Frequency: {p['frequency']}")
            if p.get("example_pmcid"):
                lines.append(f"     Example: {p['example_pmcid']}")

    # Changes made
    changes = entry.get("changes_made", [])
    if changes:
        lines.append(f"\nChanges Made ({len(changes)}):")
        for i, c in enumerate(changes, 1):
            change_type = c.get("change_type", "modified")
            section = c.get("section", "unknown")
            lines.append(f"  {i}. [{change_type.upper()}] {section}")
            if c.get("description"):
                lines.append(f"     {c['description']}")
            if c.get("rationale"):
                lines.append(f"     Rationale: {c['rationale']}")

    # Hypothesis
    hypothesis = entry.get("hypothesis")
    if hypothesis:
        lines.append(f"\nHypothesis: {hypothesis}")

    return "\n".join(lines)


def format_summary(entry: dict) -> str:
    """Format the final summary entry."""
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append("OPTIMIZATION COMPLETE")
    lines.append(f"{'='*60}")

    lines.append(f"Total iterations: {entry.get('total_iterations', '?')}")
    lines.append(f"Initial score: {entry.get('initial_score', '?')}")
    lines.append(f"Final score: {entry.get('final_score', '?')}")

    improvement = entry.get("improvement")
    if improvement is not None:
        symbol = "+" if improvement >= 0 else ""
        lines.append(f"Improvement: {symbol}{improvement}")

    lines.append(f"Best prompt version: {entry.get('best_prompt_version', '?')}")

    insights = entry.get("key_insights", [])
    if insights:
        lines.append(f"\nKey Insights:")
        for insight in insights:
            lines.append(f"  - {insight}")

    return "\n".join(lines)


def find_latest_log(task: str) -> Path:
    """Find the most recent log file for a task."""
    logs_dir = PROJECT_ROOT / "logs" / "optimization"
    if not logs_dir.exists():
        raise FileNotFoundError(f"No logs directory found at {logs_dir}")

    pattern = f"{task}_*.jsonl"
    logs = sorted(logs_dir.glob(pattern), reverse=True)

    if not logs:
        raise FileNotFoundError(f"No logs found for task '{task}'")

    return logs[0]


def main():
    parser = argparse.ArgumentParser(description="View optimization logs")
    parser.add_argument("log_file", nargs="?", help="Path to log file")
    parser.add_argument("--latest", metavar="TASK", help="Show latest log for task")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.latest:
        log_path = find_latest_log(args.latest)
        print(f"Viewing: {log_path}\n")
    elif args.log_file:
        log_path = Path(args.log_file)
    else:
        parser.print_help()
        sys.exit(1)

    if not log_path.exists():
        print(f"Error: Log file not found: {log_path}")
        sys.exit(1)

    # Read and parse log file
    entries = []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    if args.json:
        print(json.dumps(entries, indent=2))
        return

    # Display formatted output
    for entry in entries:
        if "run_started" in entry:
            # Config entry
            print(f"Optimization Run: {entry.get('task', '?')}")
            print(f"Started: {entry.get('run_started', '?')}")
            print(f"Target: {entry.get('target_score', '?')}%")
            print(f"Max iterations: {entry.get('max_iterations', '?')}")
        elif entry.get("optimization_complete"):
            print(format_summary(entry))
        elif "iteration" in entry:
            print(format_iteration(entry))
        else:
            # Unknown entry type, just dump it
            print(f"\nUnknown entry: {json.dumps(entry, indent=2)}")

    print()


if __name__ == "__main__":
    main()
