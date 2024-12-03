#!/usr/bin/env python3

import argparse
import os

def main(avp_folder: str):
    """
    Calculate the Mean Average Precision (MAP) from AVP values stored in a folder.

    Arguments:
        avp_folder -- Path to the folder that contains all the avp values of each query executed.
    """
    if not os.path.exists(avp_folder):
        print(f"Error: The folder '{avp_folder}' does not exist.")
        return

    avp_values = []

    # Iterate through all files in the folder
    for filename in os.listdir(avp_folder):
        file_path = os.path.join(avp_folder, filename)
        
        # Only process files (skip directories)
        if os.path.isfile(file_path):
            try:
                with open(file_path, "r") as f:
                    value = float(f.read().strip())
                    avp_values.append(value)
            except ValueError:
                print(f"Warning: Could not read a valid number from file '{filename}'. Skipping.")

    # Calculate the MAP
    if avp_values:
        map_score = sum(avp_values) / len(avp_values)
        print(f"MAP (Mean Average Precision) of {avp_folder}: {map_score:.4f}")
        output_file = os.path.join("evaluation", f"map.txt")
        with open(output_file, "a") as f:
            f.write(f"The system {avp_folder} has a MAP value of: {map_score:.4f}\n")
    else:
        print(f"Error: No valid AVP values found in the folder {avp_folder}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate the MAP for an information retrieval system"
    )
    parser.add_argument("--avp_folder", type=str, required=True, help="Path to the folder that contains a system's AVP query files")
    args = parser.parse_args()

    main(args.avp_folder)
