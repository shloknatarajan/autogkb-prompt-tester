"""
Script to combine individual PMCID output files into a single JSON file.

This is a thin CLI wrapper around the combine_outputs utility.
"""

import argparse

from utils.output_manager import combine_outputs


def main():
    parser = argparse.ArgumentParser(
        description="Combine JSON files from a folder into a single JSON file."
    )
    parser.add_argument(
        "--input_folder",
        type=str,
        help="Path to the folder containing JSON files.",
        default="outputs",  # Fixed: was absolute path /outputs
    )
    parser.add_argument(
        "--output_file",
        type=str,
        help="Path to the output combined JSON file.",
        default="outputs/combined_output.json",  # Fixed: was absolute path
    )

    args = parser.parse_args()

    print(f"Combining outputs from: {args.input_folder}")
    print(f"Output file: {args.output_file}")

    # Use utility function
    combined = combine_outputs(args.input_folder, args.output_file)

    print(f"Successfully combined {len(combined)} output files")

    return 0


if __name__ == "__main__":
    exit(main())
