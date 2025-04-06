import os
import re
import json
import random


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


def merge_exteriors(original, new):
    merged = original.copy()

    existing_model_ids = set()
    for obj in original.get("Block3dObjectRecords", []):
        model_id = obj.get("ModelId")
        if model_id is not None:
            existing_model_ids.add(model_id)

    merged_objects = original.get("Block3dObjectRecords", [])[:]
    for obj in new.get("Block3dObjectRecords", []):
        model_id = obj.get("ModelId")
        if model_id is None or model_id not in existing_model_ids:
            merged_objects.append(obj)

    merged["Block3dObjectRecords"] = merged_objects
    return merged


def replace_with_house(rmb_data, subrecord_index, house_data):
    building_list = rmb_data["RmbBlock"]["FldHeader"].get("BuildingDataList", [])
    sub_records = rmb_data["RmbBlock"].get("SubRecords", [])

    if subrecord_index >= len(building_list) or subrecord_index >= len(sub_records):
        print(f"Error: Subrecord index {subrecord_index} is out of range.")
        return

    # Update BuildingDataList
    original_building = building_list[subrecord_index]
    building_list[subrecord_index] = {
        "FactionId": house_data.get("FactionId", original_building.get("FactionId")),
        "BuildingType": house_data.get("BuildingType", original_building.get("BuildingType")),
        "Quality": house_data.get("Quality", original_building.get("Quality")),
        "NameSeed": house_data.get("NameSeed", original_building.get("NameSeed")),
    }

    if original_building.get("FactionId") != 0:
        building_list[subrecord_index]["FactionId"] = original_building.get("FactionId")

    # Update SubRecords
    original_subrecord = sub_records[subrecord_index]
    updated_subrecord = original_subrecord.copy()

    house_exterior = house_data.get("RmbSubRecord", {}).get("Exterior", {})
    house_interior = house_data.get("RmbSubRecord", {}).get("Interior", {})

    if "Exterior" in original_subrecord:
        updated_subrecord["Exterior"] = merge_exteriors(original_subrecord["Exterior"], house_exterior)

    if "Interior" in original_subrecord:
        updated_subrecord["Interior"] = house_interior

    sub_records[subrecord_index] = updated_subrecord


def process_rmb_files(buildings_dir="buildings", diep_dir="diep"):
    # House ModelIds from DIEP
    HOUSE_MODEL_IDS = {
        116, 117, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136,
        137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151,
        152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 200, 201, 202,
        203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 320, 321,
        324, 326, 327, 328, 330, 332, 334, 335, 336, 337, 338, 339, 340, 421, 535,
        538, 539, 541, 544, 546, 547, 548, 549, 552, 562, 602, 605, 606, 608, 610,
        614, 658, 659, 663, 702, 704, 705, 707, 708, 709
    }

    # Group DIEP files by ModelId
    diep_files = [file for file in os.listdir(diep_dir) if re.match(r"diep-(\d+)-\d+\.json", file)]
    diep_by_model_id = {}
    for f in diep_files:
        match = re.match(r"diep-(\d+)-\d+\.json", f)
        if match:
            model_id = int(match.group(1))
            diep_by_model_id.setdefault(model_id, []).append(os.path.join(diep_dir, f))

    rmb_files = [file for file in os.listdir() if file.endswith(".RMB.json") and not file.endswith(".meta")]

    for rmb_file in rmb_files:
        print(f"Processing file: {rmb_file}")
        rmb_data = load_json_file(rmb_file)
        if not rmb_data:
            continue

        sub_records = rmb_data["RmbBlock"].get("SubRecords", [])
        for i, sub_record in enumerate(sub_records):
            exterior = sub_record.get("Exterior", {})
            block3d = exterior.get("Block3dObjectRecords", [])

            for record in block3d:
                model_id = int(record.get("ModelId", -1))
                if model_id in HOUSE_MODEL_IDS:
                    building_file_pattern = f"{rmb_file.replace('.json', '')}-*-building{i}.json"
                    matching = [
                        f for f in os.listdir(buildings_dir)
                        if re.fullmatch(building_file_pattern, f) and not f.endswith(".meta")
                    ]
                    if matching:
                        print(f"Found specific building file for subrecord {i}, skipping.")
                        continue

                    if model_id in diep_by_model_id:
                        chosen = random.choice(diep_by_model_id[model_id])
                        print(f"Assigning DIEP house '{chosen}' to subrecord {i}")
                        diep_data = load_json_file(chosen)
                        if diep_data:
                            replace_with_house(rmb_data, i, diep_data)

        save_json_file(rmb_file, rmb_data)


if __name__ == "__main__":
    process_rmb_files()

