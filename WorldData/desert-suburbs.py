import json
import os
import glob

# Function to replace all FARMAA with FARMBA and TVRNAS with TVRNBS in a given JSON data structure
def replace_blocks_in_desert(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                # Recursively call the function on nested dictionaries or lists
                data[key] = replace_blocks_in_desert(value)
            elif isinstance(value, str):
                # Replace FARMAA with FARMBA and TVRNAS with TVRNBS in string values
                if "FARMAA" in value:
                    data[key] = value.replace("FARMAA", "FARMBA")
                if "TVRNAS" in value:
                    data[key] = value.replace("TVRNAS", "TVRNBS")
    elif isinstance(data, list):
        # Iterate over each item in the list and replace as needed
        for index, item in enumerate(data):
            data[index] = replace_blocks_in_desert(item)
    elif isinstance(data, str):
        # Replace FARMAA with FARMBA and TVRNAS with TVRNBS in string values directly
        if "FARMAA" in data:
            data = data.replace("FARMAA", "FARMBA")
        if "TVRNAS" in data:
            data = data.replace("TVRNAS", "TVRNBS")
    return data

# Function to process JSON files and replace blocks if the climate is Desert
def process_json_files_for_desert_climate(source_directory):
    # List all location*.json files in the source directory
    json_files = glob.glob(os.path.join(source_directory, 'location*.json'))

    for file in json_files:
        try:
            with open(file, 'r') as json_file:
                data = json.load(json_file)

            # Check if the ClimateType is Desert
            climate_type = data.get("Climate", {}).get("ClimateType")
            if climate_type == "Desert":
                print(f"Processing Desert location: {file}")
                
                # Replace blocks in the JSON data
                modified_data = replace_blocks_in_desert(data)

                # Save the modified JSON back to the file
                with open(file, 'w') as json_file:
                    json.dump(modified_data, json_file, indent=4)
                print(f"Modified and saved file: {file}")

            else:
                print(f"Skipping {file}: Not a Desert climate.")

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON in file {file}: {e}")
        except IOError as e:
            print(f"Error processing file {file}: {e}")

# Usage
current_directory = '.'  # Set to current directory
process_json_files_for_desert_climate(current_directory)

