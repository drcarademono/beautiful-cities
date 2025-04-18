import json
import os
import re
import random
import fnmatch



def preprocess_json(raw_content, placeholder="__BACKSLASH__"):
    return raw_content.replace("\\", placeholder)


def postprocess_json(processed_content, placeholder="__BACKSLASH__"):
    return processed_content.replace(placeholder, "\\")


def load_json_file(file_path, placeholder="__BACKSLASH__"):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            raw_content = file.read()
            preprocessed_content = preprocess_json(raw_content, placeholder)
            return json.loads(preprocessed_content)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON file '{file_path}'. {e}")
    except Exception as e:
        print(f"Error: Unexpected error while reading file '{file_path}'. {e}")
    return None


def save_json_file(file_path, data, placeholder="__BACKSLASH__"):
    try:
        json_content = json.dumps(data, indent=4)
        postprocessed_content = postprocess_json(json_content, placeholder)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(postprocessed_content)
        print(f"Successfully saved file '{file_path}'.")
    except Exception as e:
        print(f"Error: Failed to save JSON file '{file_path}'. {e}")


def get_one_prefix_name(two_prefix_name):
    """
    Converts a two-prefix RMB.json name (e.g., WALLAA06.FARMAA04.RMB.json)
    to its corresponding one-prefix name (e.g., WALLAA06.RMB.json).
    """
    return two_prefix_name.split('.')[0] + ".RMB.json"


def replace_with_wall(rmb_data, subrecord_index, wall_data):
    """
    Replaces the specified subrecord in the RMB data with the wall data,
    adhering to constraints:
    - Only update FactionId if the original value is 0.
    - Do not overwrite XPos, ZPos, or YRotation in Exterior.
    """
    building_list = rmb_data["RmbBlock"]["FldHeader"].get("BuildingDataList", [])
    sub_records = rmb_data["RmbBlock"].get("SubRecords", [])

    if subrecord_index >= len(building_list) or subrecord_index >= len(sub_records):
        print(f"Error: Subrecord index {subrecord_index} is out of range.")
        return

    # Update BuildingDataList
    original_building = building_list[subrecord_index]
    building_list[subrecord_index] = {
        "FactionId": wall_data.get("FactionId", original_building.get("FactionId")),
        "BuildingType": wall_data.get("BuildingType", original_building.get("BuildingType")),
        "Quality": wall_data.get("Quality", original_building.get("Quality")),
        "NameSeed": wall_data.get("NameSeed", original_building.get("NameSeed")),
    }

    # Only update FactionId if the original value is 0
    if original_building.get("FactionId") != 0:
        building_list[subrecord_index]["FactionId"] = original_building.get("FactionId")

    # Update SubRecords
    original_subrecord = sub_records[subrecord_index]
    updated_subrecord = original_subrecord.copy()

    # Replace Exterior and Interior while preserving XPos, ZPos, and YRotation
    wall_exterior = wall_data.get("RmbSubRecord", {}).get("Exterior", {})
    wall_interior = wall_data.get("RmbSubRecord", {}).get("Interior", {})

    if "Exterior" in original_subrecord:
        updated_exterior = original_subrecord["Exterior"].copy()
        updated_exterior.update(
            {
                key: value
                for key, value in wall_exterior.items()
                if key not in {"XPos", "ZPos", "YRotation"}
            }
        )
        updated_subrecord["Exterior"] = updated_exterior

    if "Interior" in original_subrecord:
        updated_subrecord["Interior"] = wall_interior

    sub_records[subrecord_index] = updated_subrecord


import json
import os
import re
import random
import fnmatch



def preprocess_json(raw_content, placeholder="__BACKSLASH__"):
    return raw_content.replace("\\", placeholder)


def postprocess_json(processed_content, placeholder="__BACKSLASH__"):
    return processed_content.replace(placeholder, "\\")


def load_json_file(file_path, placeholder="__BACKSLASH__"):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            raw_content = file.read()
            preprocessed_content = preprocess_json(raw_content, placeholder)
            return json.loads(preprocessed_content)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON file '{file_path}'. {e}")
    except Exception as e:
        print(f"Error: Unexpected error while reading file '{file_path}'. {e}")
    return None


def save_json_file(file_path, data, placeholder="__BACKSLASH__"):
    try:
        json_content = json.dumps(data, indent=4)
        postprocessed_content = postprocess_json(json_content, placeholder)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(postprocessed_content)
        print(f"Successfully saved file '{file_path}'.")
    except Exception as e:
        print(f"Error: Failed to save JSON file '{file_path}'. {e}")


def get_one_prefix_name(two_prefix_name):
    """
    Converts a two-prefix RMB.json name (e.g., WALLAA06.FARMAA04.RMB.json)
    to its corresponding one-prefix name (e.g., WALLAA06.RMB.json).
    """
    return two_prefix_name.split('.')[0] + ".RMB.json"


def replace_with_wall(rmb_data, subrecord_index, wall_data):
    """
    Replaces the specified subrecord in the RMB data with the wall data,
    adhering to constraints:
    - Only update FactionId if the original value is 0.
    - Do not overwrite XPos, ZPos, or YRotation in Exterior.
    """
    building_list = rmb_data["RmbBlock"]["FldHeader"].get("BuildingDataList", [])
    sub_records = rmb_data["RmbBlock"].get("SubRecords", [])

    if subrecord_index >= len(building_list) or subrecord_index >= len(sub_records):
        print(f"Error: Subrecord index {subrecord_index} is out of range.")
        return

    # Update BuildingDataList
    original_building = building_list[subrecord_index]
    building_list[subrecord_index] = {
        "FactionId": wall_data.get("FactionId", original_building.get("FactionId")),
        "BuildingType": wall_data.get("BuildingType", original_building.get("BuildingType")),
        "Quality": wall_data.get("Quality", original_building.get("Quality")),
        "NameSeed": wall_data.get("NameSeed", original_building.get("NameSeed")),
    }

    # Only update FactionId if the original value is 0
    if original_building.get("FactionId") != 0:
        building_list[subrecord_index]["FactionId"] = original_building.get("FactionId")

    # Update SubRecords
    original_subrecord = sub_records[subrecord_index]
    updated_subrecord = original_subrecord.copy()

    # Replace Exterior and Interior while preserving XPos, ZPos, and YRotation
    wall_exterior = wall_data.get("RmbSubRecord", {}).get("Exterior", {})
    wall_interior = wall_data.get("RmbSubRecord", {}).get("Interior", {})

    if "Exterior" in original_subrecord:
        updated_exterior = original_subrecord["Exterior"].copy()
        updated_exterior.update(
            {
                key: value
                for key, value in wall_exterior.items()
                if key not in {"XPos", "ZPos", "YRotation"}
            }
        )
        updated_subrecord["Exterior"] = updated_exterior

    if "Interior" in original_subrecord:
        updated_subrecord["Interior"] = wall_interior

    sub_records[subrecord_index] = updated_subrecord


def process_rmb_files(buildings_dir="dcw", walls_dir="wall"):
    """
    Processes all *.RMB.json files in the current directory, checking for wall ModelIds
    and assigning random walls if needed, based on both ModelId and YRotation.
    """
    # Wall ModelIds
    WALL_MODEL_IDS = {444, 445, 446}

    # Find all wall files and group them by (ModelId, YRotation)
    wall_files = [file for file in os.listdir(walls_dir) if re.match(r"wall-(\d+)-(\d+)-\d+\.json", file) and not file.endswith(".meta")]
    walls_by_model_and_rotation = {}
    for wall_file in wall_files:
        match = re.match(r"wall-(\d+)-(\d+)-\d+\.json", wall_file)
        if match:
            model_id = int(match.group(1))
            y_rotation = int(match.group(2))
            walls_by_model_and_rotation.setdefault((model_id, y_rotation), []).append(os.path.join(walls_dir, wall_file))

    # Process all RMB.json files
    rmb_files = [file for file in os.listdir() if file.endswith(".RMB.json") and not file.endswith(".meta")]

    for rmb_file in rmb_files:
        print(f"Processing file: {rmb_file}")
        rmb_data = load_json_file(rmb_file)
        if not rmb_data:
            continue

        # Use one-prefix name for building file checks
        one_prefix_name = get_one_prefix_name(rmb_file)
        print(f"DEBUG: One-prefix equivalent for {rmb_file} is {one_prefix_name}")

        # Iterate through SubRecords
        sub_records = rmb_data["RmbBlock"].get("SubRecords", [])
        for i, sub_record in enumerate(sub_records):
            exterior = sub_record.get("Exterior", {})
            block3d_object_records = exterior.get("Block3dObjectRecords", [])
            y_rotation = sub_record.get("YRotation", 0)

            # Adjust YRotation if negative
            if y_rotation < 0:
                y_rotation = 2048 - abs(y_rotation)

            for record in block3d_object_records:
                model_id = int(record.get("ModelId", -1))
                if model_id in WALL_MODEL_IDS:
                    # Check for a corresponding building file
                    building_file_pattern = f"{one_prefix_name.replace('.json', '')}-*-building{i}.json"
                    print(f"DEBUG: Searching for building files matching pattern: {building_file_pattern}")
                    matching_building_files = [
                        file for file in os.listdir(buildings_dir)
                        if fnmatch.fnmatch(file, f"{one_prefix_name.replace('.json', '')}-*-building{i}.json")
                    ]

                    # Log found building files
                    if matching_building_files:
                        print(f"DEBUG: Found building files for subrecord {i}: {matching_building_files}")
                        print(f"Skipping replacement for subrecord {i} in {rmb_file}.")
                        continue
                    else:
                        print(f"DEBUG: No building files found for subrecord {i} in {rmb_file}.")

                    # Match on ModelId and YRotation
                    key = (model_id, y_rotation)
                    if key in walls_by_model_and_rotation:
                        chosen_wall_file = random.choice(walls_by_model_and_rotation[key])
                        print(f"Assigning random wall '{chosen_wall_file}' to subrecord {i}.")

                        wall_data = load_json_file(chosen_wall_file)
                        if wall_data:
                            replace_with_wall(rmb_data, i, wall_data)
                    else:
                        print(f"DEBUG: No wall files found for ModelId {model_id} and YRotation {y_rotation}.")

        # Save the updated RMB JSON
        save_json_file(rmb_file, rmb_data)



if __name__ == "__main__":
    process_rmb_files()
