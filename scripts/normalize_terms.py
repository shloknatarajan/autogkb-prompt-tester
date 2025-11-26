"""
Script to normalize terms in annotation output files.

This is a thin CLI wrapper around the normalization utility.
"""

import argparse

from utils.normalization import normalize_outputs_in_directory, normalize_output_file


def main():
    parser = argparse.ArgumentParser(
        description="Normalize terms in annotation JSON files."
    )
    parser.add_argument(
        "--directory",
        type=str,
        help="Path to directory containing JSON files to normalize",
        default=None,
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to single JSON file to normalize",
        default=None,
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite original files instead of creating *_normalized.json",
        default=True,
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (only for single file mode)",
        default=None,
    )

    args = parser.parse_args()

    if args.directory:
        # Normalize entire directory
        print(f"Normalizing directory: {args.directory}")
        print(f"In-place: {args.in_place}")

        success, failed = normalize_outputs_in_directory(
            args.directory, in_place=args.in_place, verbose=True
        )

        print(f"\n=== Summary ===")
        print(f"Successful: {success}")
        print(f"Failed: {failed}")

        return 0 if failed == 0 else 1

    elif args.file:
        # Normalize single file
        print(f"Normalizing file: {args.file}")

        # Determine output file
        if args.output:
            output_file = args.output
        elif args.in_place:
            output_file = args.file
        else:
            # Create _normalized version
            if args.file.endswith(".json"):
                output_file = args.file.replace(".json", "_normalized.json")
            else:
                output_file = f"{args.file}_normalized"

        success = normalize_output_file(args.file, output_file, verbose=True)

        if success:
            print(f"Output saved to: {output_file}")
            return 0
        else:
            print("Normalization failed")
            return 1

    else:
        print("Error: Must specify either --directory or --file")
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit(main())
