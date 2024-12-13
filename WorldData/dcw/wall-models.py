import json
import os
import shutil

# Tavern ModelIds
WALL_MODEL_IDS = {444, 445, 446}

def load_json_file(file_path):
    """
    Loads a JSON file.
    :param file_path: Path to the JSON file.
    :return: Parsed JSON data or None if the file couldn't be parsed.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON file '{file_path}'. {e}")
    except Exception as e:
        print(f"Error: Unexpected error while reading file '{file_path}'. {e}")
    return None

def get_wall_info(data):
    """
    Checks if a building JSON contains any wall ModelId in RmbSubRecord > Exterior > Block3dObjectRecords.
    Extracts the ModelId, YRotation, and VariantNumber if available.
    :param data: Parsed JSON data.
    :return: A tuple (ModelId, YRotation, VariantNumber) or None if no wall ModelId is found.
    """
    try:
        rmb_sub_record = data.get("RmbSubRecord", {})
        y_rotation = rmb_sub_record.get("YRotation", 0)
        block3d_object_records = rmb_sub_record.get("Exterior", {}).get("Block3dObjectRecords", [])

        for record in block3d_object_records:
            model_id = int(record.get("ModelId", -1))
            if model_id in WALL_MODEL_IDS:
                variant_number = record.get("VariantNumber", 0)
                return model_id, y_rotation, variant_number
    except Exception as e:
        print(f"Error processing data structure: {e}")
    return None

def process_building_files(directory=".", output_directory="wall"):
    """
    Processes all *building*.json files in the specified directory and moves wall JSONs to a new directory.
    :param directory: Directory containing the building JSON files.
    :param output_directory: Directory to move identified wall JSON files.
    """
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    building_files = [file for file in os.listdir(directory) if "building" in file and file.endswith(".json")]
    wall_counts = {}

    for file in building_files:
        file_path = os.path.join(directory, file)
        print(f"Processing file: {file_path}")

        # Load the JSON file
        data = load_json_file(file_path)
        if not data:
            continue

        # Get wall info
        wall_info = get_wall_info(data)
        if wall_info is not None:
            model_id, y_rotation, variant_number = wall_info

            # Maintain a count for each (ModelId, YRotation)
            key = (model_id, y_rotation)
            if key not in wall_counts:
                wall_counts[key] = 0
            count = wall_counts[key]
            wall_counts[key] += 1

            # Build the new filename
            new_filename = f"wall-{model_id:03d}-{y_rotation:03d}-{count:02d}.json"
            new_file_path = os.path.join(output_directory, new_filename)

            # Move the file
            shutil.move(file_path, new_file_path)
            print(f"Moved file to: {new_file_path}")

if __name__ == "__main__":
    process_building_files()

