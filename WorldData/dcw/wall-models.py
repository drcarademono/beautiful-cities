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


def get_wall_model_id(data):
    """
    Checks if a building JSON contains any wall ModelId in RmbSubRecord > Exterior > Block3dObjectRecords.
    :param data: Parsed JSON data.
    :return: The first matching wall ModelId, or None if no match is found.
    """
    try:
        block3d_object_records = (
            data.get("RmbSubRecord", {})
                .get("Exterior", {})
                .get("Block3dObjectRecords", [])
        )
        for record in block3d_object_records:
            model_id = int(record.get("ModelId", -1))
            if model_id in WALL_MODEL_IDS:
                return model_id
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
    wall_counts = {model_id: 0 for model_id in WALL_MODEL_IDS}

    for file in building_files:
        file_path = os.path.join(directory, file)
        print(f"Processing file: {file_path}")

        # Load the JSON file
        data = load_json_file(file_path)
        if not data:
            continue

        # Check if the file contains a wall ModelId
        wall_model_id = get_wall_model_id(data)
        if wall_model_id is not None:
            # Increment the counter for this ModelId
            count = wall_counts[wall_model_id]
            wall_counts[wall_model_id] += 1

            # Build the new filename
            new_filename = f"wall-{wall_model_id:03d}-{count:02d}.json"
            new_file_path = os.path.join(output_directory, new_filename)

            # Move the file
            shutil.move(file_path, new_file_path)
            print(f"Moved file to: {new_file_path}")


if __name__ == "__main__":
    process_building_files()

