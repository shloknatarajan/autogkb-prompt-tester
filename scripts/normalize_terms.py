from pathlib import Path
from term_normalization.term_lookup import normalize_annotation

input_path = Path("outputs/PMC2859392.json")
output_path = Path("outputs/PMC2859392_normalized.json")

normalize_annotation(input_path, output_path)

# normalize directory
# def normalize_directory(input_dir: Path, output_dir: Path):
#     """
#     Normalize all JSON files in the input directory and save them to the output directory.
#
#     Args:
#         input_dir (Path): Path to the input directory
#         output_dir (Path): Path to the output directory
#     """
#     output_dir.mkdir(parents=True, exist_ok=True)
#
#     for input_file in input_dir.glob("*.json"):
#         output_file = output_dir / input_file.name
#         normalize_annotation(input_file, output_file)
#
#
# if __name__ == "__main__":
#     Parser = argparse.ArgumentParser(
#         description="Normalize all JSON annotation files in a directory."
#     )
#     Parser.add_argument(
#         "--input_directory",
#         type=str,
#         help="Path to the input directory containing JSON files.",
#         default="outputs",
#     )
#     Parser.add_argument(
#         "--output_directory",
#         type=str,
#         help="Path to the output directory to save normalized JSON files.",
#         default="outputs_normalized",
#     )
#     args = Parser.parse_args()
#     input_directory = Path(args.input_directory)
#     output_directory = Path(args.output_directory)
#
#     normalize_directory(input_directory, output_directory)
