from pathlib import Path
from term_normalization.term_lookup import normalize_annotation

input_path = Path("outputs/PMC10786722.json")
output_path = Path("outputs/PMC10786722_normalized.json")

normalize_annotation(input_path, output_path)
