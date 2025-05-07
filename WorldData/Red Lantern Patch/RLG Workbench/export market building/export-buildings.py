import json
import os
import re

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

def convert_building_type(building_type):
    """
    Convert the building type value to its corresponding number
    based on the provided enum mapping.
    """
    # If already an integer, return it.
    if isinstance(building_type, int):
        return building_type

    mapping = {
        "Alchemist": 0x00,
        "HouseForSale": 0x01,
        "Armorer": 0x02,
        "Bank": 0x03,
        "Town4": 0x04,
        "Bookseller": 0x05,
        "ClothingStore": 0x06,
        "FurnitureStore": 0x07,
        "GemStore": 0x08,
        "GeneralStore": 0x09,
        "Library": 0x0a,
        "Guildhall": 0x0b,
        "PawnShop": 0x0c,
        "WeaponSmith": 0x0d,
        "Temple": 0x0e,
        "Tavern": 0x0f,
        "Palace": 0x10,
        "House1": 0x11,
        "House2": 0x12,
        "House3": 0x13,
        "House4": 0x14,
        "House5": 0x15,
        "House6": 0x16,
        "Town23": 0x17,
        "Ship": 0x18,
        "Special1": 0x74,
        "Special2": 0xdf,
        "Special3": 0xf9,
        "Special4": 0xfa,
    }
    return mapping.get(building_type, 0)

def export_buildings_from_rmb(rmb_file, placeholder="__BACKSLASH__"):
    # Load the RMB JSON data
    rmb_data = load_json_file(rmb_file, placeholder)
    if not rmb_data:
        return
    
    # Validate the expected structure exists
    if "RmbBlock" not in rmb_data or "FldHeader" not in rmb_data["RmbBlock"]:
        print(f"Error: Invalid RMB JSON structure in '{rmb_file}'.")
        return
    
    fld_header = rmb_data["RmbBlock"]["FldHeader"]
    building_list = fld_header.get("BuildingDataList", [])
    sub_records = rmb_data["RmbBlock"].get("SubRecords", [])
    
    if not building_list:
        print(f"No buildings found in '{rmb_file}'.")
        return
    
    # Get the RMB index from the top-level header (e.g. 15 in your example)
    rmb_index = rmb_data.get("Index", "0")
    
    # Base file name: remove the .json extension (e.g. "MARKAA00.RMB" from "MARKAA00.RMB.json")
    base_name = os.path.splitext(rmb_file)[0]
    
    # Process each building (using the smaller length if the lists differ)
    num_buildings = min(len(building_list), len(sub_records))
    for i in range(num_buildings):
        building_data = building_list[i]
        sub_record = sub_records[i]
        
        # Build the export JSON structure with converted BuildingType
        export_data = {
            "FactionId": building_data.get("FactionId", 0),
            "BuildingType": convert_building_type(building_data.get("BuildingType", 0)),
            "Quality": building_data.get("Quality", 0),
            "NameSeed": building_data.get("NameSeed", 0),
            "RmbSubRecord": sub_record,
            "AutoMapData": None
        }
        
        # Construct the output file name
        output_filename = f"{base_name}-{rmb_index}-building{i}.json"
        save_json_file(output_filename, export_data, placeholder)

def process_directory():
    # Find all files in the current directory that end with ".RMB.json" (ignoring .meta files)
    rmb_files = [file for file in os.listdir() if file.endswith(".RMB.json") and not file.endswith(".meta")]
    
    if not rmb_files:
        print("No RMB JSON files found in the current directory.")
        return
    
    for rmb_file in rmb_files:
        print(f"Processing '{rmb_file}'...")
        export_buildings_from_rmb(rmb_file)

if __name__ == "__main__":
    process_directory()

