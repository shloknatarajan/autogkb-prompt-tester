#!/usr/bin/env python3
"""
Autonomous Prompt Optimization using Claude Code.

This script launches Claude Code to iteratively improve prompts based on
benchmark performance. It tracks all changes made and the reasoning behind them.

Usage:
    pixi run python scripts/optimize_prompts.py --task var-pheno --iterations 5
    pixi run python scripts/optimize_prompts.py --task var-drug --iterations 3 --target-score 75

The script will:
1. Run the current best prompt through benchmarks
2. Analyze the worst-performing PMCIDs
3. Identify systematic error patterns
4. Create improved prompt versions
5. Track all changes with rationale
6. Repeat until target score or max iterations
"""

import argparse
import subprocess
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def create_instructions_file(task: str, iterations: int, target_score: float, log_file: Path) -> Path:
    """Write detailed instructions to a file that Claude can read."""

    instructions_file = PROJECT_ROOT / "logs" / "optimization" / f"instructions_{task}.md"

    content = f"""# Prompt Optimization Instructions

## Mission
Optimize the **{task}** prompt to improve benchmark scores.

## Configuration
- Task: {task}
- Max iterations: {iterations}
- Target score: {target_score}%
- Change log: {log_file}

## Optimization Loop

For each iteration:

### Step 1: Measure Performance
```bash
pixi run python scripts/batch_process.py --tasks {task} --pmcids persistent_data/benchmark_pmcids.txt --output-dir outputs/optimization_run
pixi run python scripts/combine_outputs.py outputs/optimization_run --output outputs/optimization_run/combined.json
pixi run python scripts/run_benchmark.py outputs/optimization_run/combined.json --output benchmark_results/optimization_latest.json
```

### Step 2: Find Worst Performers
From benchmark results, find 3 PMCIDs with lowest {task} scores.

### Step 3: Deep Analysis
For each worst PMCID, compare:
- Article: `data/markdown/{{pmcid}}.md`
- Prediction: `outputs/optimization_run/{{pmcid}}.json`
- Ground truth: Search in `persistent_data/benchmark_annotations.json`

### Step 4: Identify Patterns
What systematic errors appear across PMCIDs?

### Step 5: Create New Prompt
1. Copy: `cp -r prompts/{task}/{{old}} prompts/{task}/{{new}}`
2. Edit the prompt.md to fix patterns
3. Update config.json and best_prompts.json

### Step 6: Validate
Re-run benchmarks, compare scores.

### Step 7: Log Changes
Append to {log_file}:
```json
{{
  "iteration": 1,
  "prompt_version_before": "...",
  "prompt_version_after": "...",
  "score_before": 0,
  "score_after": 0,
  "error_patterns_found": ["..."],
  "changes_made": ["..."],
  "hypothesis": "..."
}}
```

## Stop When
- Score >= {target_score}%
- {iterations} iterations done
- No improvement for 2 iterations
"""

    instructions_file.write_text(content)
    return instructions_file


def create_optimization_prompt(task: str, iterations: int, target_score: float, log_file: Path) -> str:
    """Generate a SHORT prompt for Claude Code."""

    instructions_file = create_instructions_file(task, iterations, target_score, log_file)

    return f"""Read the optimization instructions at {instructions_file} and follow them.

Your goal: Improve the {task} prompt to score {target_score}%+ on benchmarks.

Key steps:
1. Run benchmarks to get current score
2. Analyze 3 worst PMCIDs (compare prediction vs ground truth vs article)
3. Find systematic error patterns
4. Create improved prompt version
5. Log changes to {log_file}
6. Repeat up to {iterations} times

Start now with Step 1."""


def main():
    parser = argparse.ArgumentParser(
        description="Autonomous prompt optimization using Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--task",
        required=True,
        choices=["var-pheno", "var-drug", "var-fa", "study-parameters", "summary"],
        help="Which task's prompt to optimize"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="Maximum number of optimization iterations (default: 5)"
    )
    parser.add_argument(
        "--target-score",
        type=float,
        default=80.0,
        help="Target benchmark score to achieve (default: 80.0)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the prompt without running Claude"
    )
    args = parser.parse_args()

    # Create logs directory
    logs_dir = PROJECT_ROOT / "logs" / "optimization"
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Create log file for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"{args.task}_{timestamp}.jsonl"

    # Initialize log file with run config
    config = {
        "run_started": datetime.now().isoformat(),
        "task": args.task,
        "max_iterations": args.iterations,
        "target_score": args.target_score,
        "log_file": str(log_file),
    }

    with open(log_file, "w") as f:
        f.write(json.dumps(config) + "\n")

    print(f"Prompt Optimization Starting")
    print(f"=" * 50)
    print(f"Task: {args.task}")
    print(f"Max iterations: {args.iterations}")
    print(f"Target score: {args.target_score}%")
    print(f"Log file: {log_file}")
    print(f"=" * 50)

    # Generate the optimization prompt
    prompt = create_optimization_prompt(
        task=args.task,
        iterations=args.iterations,
        target_score=args.target_score,
        log_file=log_file
    )

    if args.dry_run:
        print("\n[DRY RUN] Prompt that would be sent to Claude:\n")
        print(prompt)
        return

    # Run Claude Code with the optimization prompt
    print(f"\nLaunching Claude Code for autonomous optimization...")
    print(f"This may take a while.")
    print(f"  - Iteration logs: {log_file}")
    print(f"  - Full transcript: {logs_dir}/{args.task}_{timestamp}_transcript.txt\n")

    # Also save Claude's output to a transcript file
    transcript_file = logs_dir / f"{args.task}_{timestamp}_transcript.txt"

    try:
        # Run Claude with stream-json output format for real-time streaming
        with open(transcript_file, "w") as transcript:
            process = subprocess.Popen(
                ["claude", "-p", prompt, "--output-format", "stream-json"],
                cwd=PROJECT_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )

            # Stream output to both console and file
            for line in process.stdout:
                transcript.write(line)
                transcript.flush()

                # Parse JSON and display relevant parts
                try:
                    data = json.loads(line)
                    msg_type = data.get("type", "")

                    if msg_type == "assistant" and "content" in data:
                        for block in data.get("content", []):
                            if block.get("type") == "text":
                                print(block.get("text", ""), end="", flush=True)
                            elif block.get("type") == "tool_use":
                                tool = block.get("name", "unknown")
                                print(f"\n[Using tool: {tool}]", flush=True)
                    elif msg_type == "result":
                        print(f"\n\n=== Done ===", flush=True)
                except json.JSONDecodeError:
                    print(line, end="")  # Print raw if not JSON

            process.wait()
            if process.returncode != 0:
                stderr = process.stderr.read()
                print(f"Claude Code exited with error: {process.returncode}")
                if stderr:
                    print(f"Error: {stderr}")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\nOptimization interrupted by user")
        process.terminate()
        sys.exit(130)

    # Print summary
    print(f"\nOptimization complete. See full log at: {log_file}")

    # Try to read and display final results
    try:
        with open(log_file) as f:
            lines = f.readlines()
            if len(lines) > 1:
                last_entry = json.loads(lines[-1])
                if last_entry.get("optimization_complete"):
                    print(f"\nResults:")
                    print(f"  Initial score: {last_entry.get('initial_score', 'N/A')}")
                    print(f"  Final score: {last_entry.get('final_score', 'N/A')}")
                    print(f"  Improvement: {last_entry.get('improvement', 'N/A')}")
                    print(f"  Best version: {last_entry.get('best_prompt_version', 'N/A')}")
    except Exception:
        pass  # Log parsing failed, user can check file manually


if __name__ == "__main__":
    main()
