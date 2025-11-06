# combine outputs from individual json files into a single json file
import json
import os
import argparse


def combine_json_files(input_folder, output_file):
    combined_data = {}

    # Iterate through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(input_folder, filename)
            with open(file_path, "r") as f:
                data = json.load(f)

                # check if pmcid is part of the data
                pmcid = ""
                if data.get("pmcid"):
                    pmcid = data["pmcid"]
                else:
                    pmcid = filename.replace(".json", "")

                combined_data[pmcid] = data

    # Write the combined data to the output file
    with open(output_file, "w") as f:
        json.dump(combined_data, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Combine JSON files from a folder into a single JSON file."
    )
    parser.add_argument(
        "--input_folder",
        type=str,
        help="Path to the folder containing JSON files.",
        default="./outputs",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        help="Path to the output combined JSON file.",
        default="/outputs/combined_output.json",
    )

    args = parser.parse_args()

    combine_json_files(args.input_folder, args.output_file)
