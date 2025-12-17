#!/usr/bin/env python3
"""
CLI for running the autonomous prompt optimization agent.

Usage:
    python -m agents.run_optimizer --task var-drug --target-score 0.80
    python -m agents.run_optimizer --task auto --max-iterations 10

Examples:
    # Auto-select lowest scoring task
    python -m agents.run_optimizer

    # Target specific task with custom settings
    python -m agents.run_optimizer --task var-drug --target-score 0.80 --max-iterations 5

    # Quick iteration with mini, validate with opus
    python -m agents.run_optimizer --task var-pheno \\
        --quick-model openai/gpt-4o-mini \\
        --validation-model anthropic/claude-opus-4-5-20251101
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.prompt_optimizer import PromptOptimizationAgent, OptimizationConfig


def main():
    parser = argparse.ArgumentParser(
        description="Autonomous Prompt Optimization Agent for AutoGKB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Auto-select lowest scoring task
  %(prog)s --task var-drug                    # Optimize var-drug task
  %(prog)s --task var-pheno --target-score 0.85
  %(prog)s --task auto --max-iterations 10 --sample-pmcids 10
        """,
    )

    parser.add_argument(
        "--task",
        type=str,
        default="auto",
        choices=["var-pheno", "var-drug", "var-fa", "study-parameters", "auto"],
        help="Task to optimize (default: auto - picks lowest scoring)",
    )

    parser.add_argument(
        "--target-score",
        type=float,
        default=0.90,
        help="Target benchmark score to achieve (default: 0.90)",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum improvement cycles - each cycle = write prompt + test (default: 5)",
    )

    parser.add_argument(
        "--min-improvement",
        type=float,
        default=0.01,
        help="Minimum improvement per iteration to continue (default: 0.01)",
    )

    parser.add_argument(
        "--sample-pmcids",
        type=int,
        default=5,
        help="Number of PMCIDs for quick testing (default: 5, 0=all)",
    )

    parser.add_argument(
        "--quick-model",
        type=str,
        default="openai/gpt-5.2",
        help="Model for quick iteration benchmarks (default: openai/gpt-5.2)",
    )

    parser.add_argument(
        "--validation-model",
        type=str,
        default="openai/gpt-5.2",
        help="Model for validation benchmarks (default: openai/gpt-5.2)",
    )

    parser.add_argument(
        "--validation-threshold",
        type=float,
        default=0.03,
        help="Improvement threshold to trigger validation (default: 0.03)",
    )

    parser.add_argument(
        "--full-final",
        action="store_true",
        help="Run full benchmark on final prompt (all PMCIDs)",
    )

    parser.add_argument(
        "--log-file",
        type=str,
        default="logs/optimization_log.jsonl",
        help="Path to optimization log file (default: logs/optimization_log.jsonl)",
    )

    args = parser.parse_args()

    # Create configuration
    config = OptimizationConfig(
        target_task=args.task,
        target_score=args.target_score,
        max_iterations=args.max_iterations,
        min_improvement=args.min_improvement,
        sample_pmcids=args.sample_pmcids,
        quick_model=args.quick_model,
        validation_model=args.validation_model,
        validation_threshold=args.validation_threshold,
        full_benchmark_on_final=args.full_final,
        log_file=Path(args.log_file),
    )

    print("=" * 60)
    print("AUTONOMOUS PROMPT OPTIMIZATION AGENT")
    print("=" * 60)
    print(f"Task: {config.target_task}")
    print(f"Target Score: {config.target_score:.1%}")
    print(f"Max Improvement Cycles: {config.max_iterations}")
    print(f"  (Each cycle = analyze -> write prompt -> test)")
    print(f"Sample PMCIDs per test: {config.sample_pmcids}")
    print(f"Quick Model: {config.quick_model}")
    print(f"Validation Model: {config.validation_model}")
    print(f"Log File: {config.log_file}")
    print("=" * 60)

    # Create and run agent
    agent = PromptOptimizationAgent(config)

    try:
        result = agent.run()

        # Print summary
        print("\n" + "=" * 60)
        print("OPTIMIZATION COMPLETE")
        print("=" * 60)
        print(f"Task: {result.task}")
        print(f"Initial Score: {result.initial_score:.4f} ({result.initial_score:.1%})")
        print(f"Final Score: {result.final_score:.4f} ({result.final_score:.1%})")
        print(
            f"Improvement: {result.final_score - result.initial_score:.4f} "
            f"({(result.final_score - result.initial_score):.1%})"
        )
        print(f"Improvement Cycles Completed: {result.iterations}")
        print(f"Prompt Versions Created: {len(result.prompt_versions)}")
        if result.prompt_versions:
            for pv in result.prompt_versions:
                print(f"  - {pv}")
        print(f"Success: {'Yes' if result.success else 'No'}")
        print(f"Score History: {' -> '.join(f'{s:.3f}' for s in result.score_history)}")
        print("=" * 60)

        if result.error:
            print(f"\nError: {result.error}")
            return 1

        return 0 if result.success else 1

    except KeyboardInterrupt:
        print("\n\nOptimization interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
