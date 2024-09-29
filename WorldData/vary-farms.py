import json
import os
import glob
import random

def find_and_replace_farm_blocks(file_path):
    # Read the JSON file
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)

        # Check if BlockNames exist in the current file
        if "Exterior" in data and "ExteriorData" in data["Exterior"] and "BlockNames" in data["Exterior"]["ExteriorData"]:
            block_names = data["Exterior"]["ExteriorData"]["BlockNames"]
            print(f"Processing BlockNames in file {file_path}")

            # Replace FARMAA10 with FARMAA10 to FARMAA13, and FARMBA10 with FARMBA10 to FARMBA13
            for i, block_name in enumerate(block_names):
                if "FARMAA10" in block_name:
                    new_block = block_name.replace("FARMAA10", f"FARMAA{random.randint(10, 13):02d}")
                    print(f"Changing {block_name} to {new_block}")
                    block_names[i] = new_block
                elif "FARMBA10" in block_name:
                    new_block = block_name.replace("FARMBA10", f"FARMBA{random.randint(10, 13):02d}")
                    print(f"Changing {block_name} to {new_block}")
                    block_names[i] = new_block

            # Save the modified JSON back to the file
            with open(file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)

            print(f"Finished processing {file_path}")

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON in file {file_path}: {e}")
    except IOError as e:
        print(f"Error processing file {file_path}: {e}")

def process_all_json_files():
    # Look for all location*.json files in the current directory and subdirectories
    json_files = glob.glob('**/location*.json', recursive=True)

    if not json_files:
        print(f"No JSON files found.")
        return

    for file in json_files:
        find_and_replace_farm_blocks(file)

# Run the script
process_all_json_files()

