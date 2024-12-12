import os
import json
from glob import glob


def load_json(file_path):
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for {file_path}: {e}")
    except Exception as e:
        print(f"Unexpected error loading {file_path}: {e}")
    return None


def save_json(file_path, data):
    """Save JSON data to a file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving JSON for {file_path}: {e}")


def extract_model_ids(sub_records, relevant_model_ids):
    """
    Extract a list of ModelId values from SubRecords > Exterior > Block3dObjectRecords,
    filtered by relevant ModelIds.
    """
    model_ids = []
    for record in sub_records:
        exterior = record.get("Exterior", {})
        block_3d_records = exterior.get("Block3dObjectRecords", [])
        for obj in block_3d_records:
            model_id = obj.get("ModelId")
            if model_id in relevant_model_ids:
                model_ids.append(model_id)
    return model_ids


def reorder_by_model_ids(original_file, two_prefix_file):
    """
    Reorder BuildingDataList and SubRecords in two-prefix RMB.json
    to match the order of relevant ModelIds in the original RMB.json.
    """
    original_data = load_json(original_file)
    two_prefix_data = load_json(two_prefix_file)

    if not original_data or not two_prefix_data:
        print(f"Skipping {two_prefix_file} due to errors in loading JSON files.")
        return

    # Define relevant ModelIds
    relevant_model_ids = {"444", "445", "446"}

    try:
        # Extract ModelId order from the original SubRecords
        original_sub_records = original_data.get("RmbBlock", {}).get("SubRecords", [])
        original_model_ids = extract_model_ids(original_sub_records, relevant_model_ids)
        print(f"ModelIds in {original_file}: {original_model_ids}")

        # Extract ModelId order from the two-prefix SubRecords
        two_sub_records = two_prefix_data.get("RmbBlock", {}).get("SubRecords", [])
        two_building_list = two_prefix_data.get("RmbBlock", {}).get("FldHeader", {}).get("BuildingDataList", [])
        two_model_ids = extract_model_ids(two_sub_records, relevant_model_ids)
        print(f"ModelIds in {two_prefix_file} before reordering: {two_model_ids}")

        # Create mappings of ModelId -> (index, record) for two-prefix SubRecords
        model_id_to_records = {}
        unmatched_records = []
        for i, record in enumerate(two_sub_records):
            exterior = record.get("Exterior", {})
            block_3d_records = exterior.get("Block3dObjectRecords", [])
            has_relevant_model_id = False
            for obj in block_3d_records:
                model_id = obj.get("ModelId")
                if model_id in relevant_model_ids:
                    has_relevant_model_id = True
                    if model_id not in model_id_to_records:
                        model_id_to_records[model_id] = []
                    model_id_to_records[model_id].append((i, record))
            if not has_relevant_model_id:
                unmatched_records.append((i, record))

        # Reorder based on original ModelId order
        reordered_sub_records = []
        reordered_building_list = []
        used_indices = set()

        for model_id in original_model_ids:
            if model_id in model_id_to_records and model_id_to_records[model_id]:
                # Pop the next available record with this ModelId
                index, record = model_id_to_records[model_id].pop(0)
                reordered_sub_records.append(record)
                reordered_building_list.append(two_building_list[index])
                used_indices.add(index)

        # Append remaining unmatched entries in their original order
        for i, record in enumerate(two_sub_records):
            if i not in used_indices:
                reordered_sub_records.append(record)
                reordered_building_list.append(two_building_list[i])

        # Update the two-prefix file
        two_prefix_data["RmbBlock"]["FldHeader"]["BuildingDataList"] = reordered_building_list
        two_prefix_data["RmbBlock"]["SubRecords"] = reordered_sub_records

        # Save changes
        save_json(two_prefix_file, two_prefix_data)

        # Extract and display the final ordered ModelIds
        final_model_ids = extract_model_ids(reordered_sub_records, relevant_model_ids)
        print(f"ModelIds in {two_prefix_file} after reordering: {final_model_ids}")

    except Exception as e:
        print(f"Error reordering {two_prefix_file}: {e}")


def find_original_rmb(json_file):
    """Find the corresponding original RMB.json for a given two-prefix RMB.json."""
    base_name = json_file.split('.')[0]
    prefix1 = base_name[:8]  # Extract the WALLAA## part
    original_file = f"{prefix1}.RMB.json"
    if os.path.exists(original_file):
        return original_file
    return None


def main():
    # Find all two-prefix RMB.json files
    two_prefix_files = glob("WALLAA??.*.RMB.json")

    for two_prefix_file in two_prefix_files:
        # Find the corresponding original RMB.json file
        original_file = find_original_rmb(two_prefix_file)
        if original_file:
            print(f"Processing {two_prefix_file} with original {original_file}")
            reorder_by_model_ids(original_file, two_prefix_file)
        else:
            print(f"No original file found for {two_prefix_file}")


if __name__ == "__main__":
    main()

