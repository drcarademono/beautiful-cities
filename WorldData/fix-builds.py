import json
import os
import glob
import re
import random

def load_json_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        # Replace invalid escape sequences
        content = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', content)
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in file {filepath}: {e}")
            return None

def count_interiors(rmb_data):
    sub_records = rmb_data.get('RmbBlock', {}).get('SubRecords', [])
    num_interiors = sum(1 for record in sub_records if 'Interior' in record)
    return num_interiors

def get_existing_building_data(buildings):
    name_seed_list = {}
    quality_list = {}
    sector_list = {}
    for building in buildings:
        building_type = building.get('BuildingType')
        name_seed = building.get('NameSeed')
        quality = building.get('Quality')
        sector = building.get('Sector')
        if building_type is not None:
            if building_type not in name_seed_list:
                name_seed_list[building_type] = []
                quality_list[building_type] = []
                sector_list[building_type] = []
            if name_seed is not None:
                name_seed_list[building_type].append(name_seed)
            if quality is not None:
                quality_list[building_type].append(quality)
            if sector is not None:
                sector_list[building_type].append(sector)
    return name_seed_list, quality_list, sector_list

def load_vanilla_building_data(location_name):
    """Load BuildingDataList from the vanilla location JSON file."""
    vanilla_file = os.path.join('vanillaloc', location_name)
    if not os.path.exists(vanilla_file):
        print(f"  Vanilla file {vanilla_file} does not exist.")
        return None

    vanilla_data = load_json_file(vanilla_file)
    if vanilla_data is None:
        return None

    return vanilla_data.get('Exterior', {}).get('BuildingDataList', [])

def get_vanilla_building_data(vanilla_buildings):
    """Extract NameSeed, Quality, and Sector from vanilla buildings."""
    name_seed_list = {}
    quality_list = {}
    sector_list = {}
    for building in vanilla_buildings:
        building_type = building.get('BuildingType')
        name_seed = building.get('NameSeed')
        quality = building.get('Quality')
        sector = building.get('Sector')
        if building_type is not None:
            if building_type not in name_seed_list:
                name_seed_list[building_type] = []
                quality_list[building_type] = []
                sector_list[building_type] = []
            if name_seed is not None:
                name_seed_list[building_type].append(name_seed)
            if quality is not None:
                quality_list[building_type].append(quality)
            if sector is not None:
                sector_list[building_type].append(sector)
    return name_seed_list, quality_list, sector_list

# Map BuildingType names to enum values
BUILDING_TYPE_ENUM = {
    "None": -1,
    "Alchemist": 0,
    "HouseForSale": 1,
    "Armorer": 2,
    "Bank": 3,
    "Town4": 4,
    "Bookseller": 5,
    "ClothingStore": 6,
    "FurnitureStore": 7,
    "GemStore": 8,
    "GeneralStore": 9,
    "Library": 10,
    "GuildHall": 11,
    "PawnShop": 12,
    "WeaponSmith": 13,
    "Temple": 14,
    "Tavern": 15,
    "Palace": 16,
    "House1": 17,
    "House2": 18,
    "House3": 19,
    "House4": 20,
    "House5": 21,
    "House6": 22,
    "Town23": 23,
    "Ship": 24,
    "Special1": 0x74,
    "Special2": 0xdf,
    "Special3": 0xf9,
    "Special4": 0xfa,
    "AnyShop": 0xfffd,
    "AnyHouse": 0xfffe,
    "AllValid": 0xffff,
}

def normalize_building_type(building_type):
    """Convert BuildingType to its numeric equivalent if it's a string."""
    if isinstance(building_type, str):
        return BUILDING_TYPE_ENUM.get(building_type, -1)  # Default to -1 if not found
    return building_type

def update_buildings():
    # Get a list of all location*.json files in the current directory
    location_files = glob.glob('location*.json')

    for location_file in location_files:
        print(f"Processing {location_file}")
        
        location_data = load_json_file(location_file)
        if location_data is None:
            continue

        # Get the corresponding vanilla location JSON filename
        location_name = os.path.basename(location_file)
        vanilla_buildings = load_vanilla_building_data(location_name)
        if vanilla_buildings is None:
            print(f"  Skipping {location_file} due to missing vanilla data.")
            continue

        # Extract building data from the vanilla file
        name_seed_list, quality_list, sector_list = get_vanilla_building_data(vanilla_buildings)

        new_buildings = []

        # Get the LocationId
        location_id = location_data.get('Exterior', {}).get('RecordElement', {}).get('Header', {}).get('LocationId', 0)
        print(f"  LocationId: {location_id}")

        # Get the BlockNames array from Exterior > ExteriorData
        block_names = location_data.get('Exterior', {}).get('ExteriorData', {}).get('BlockNames', [])
        for block_name in block_names:
            rmb_file = block_name + '.json'
            print(f"  Working on BlockName: {block_name}")

            if not os.path.exists(rmb_file):
                print(f"    File {rmb_file} does not exist.")
                continue

            rmb_data = load_json_file(rmb_file)
            if rmb_data is None:
                continue

            # Count the number of Interior subrecords
            num_interiors = count_interiors(rmb_data)
            print(f"    Found {num_interiors} interior(s) in {rmb_file}")

            # Get the BuildingDataList
            building_data_list = rmb_data.get('RmbBlock', {}).get('FldHeader', {}).get('BuildingDataList', [])

            # Take the first x items from the BuildingDataList
            buildings_to_add = building_data_list[:num_interiors]

            # Update the fields for each building using vanilla data
            for building in buildings_to_add:
                building_type = normalize_building_type(building.get('BuildingType'))
                if building_type in name_seed_list and name_seed_list[building_type]:
                    building['NameSeed'] = name_seed_list[building_type].pop(0)
                else:
                    building['NameSeed'] = random.randint(0, 30000)

                if building_type in quality_list and quality_list[building_type]:
                    building['Quality'] = quality_list[building_type].pop(0)

                if building_type in sector_list and sector_list[building_type]:
                    building['Sector'] = sector_list[building_type].pop(0)
                else:
                    building['Sector'] = new_buildings[-1]['Sector'] + 3 if new_buildings else 3

                building['LocationId'] = location_id

            new_buildings.extend(buildings_to_add)
            print(f"    Adding {len(buildings_to_add)} building(s) from {block_name} to Buildings array")

        # Update the Buildings array and BuildingCount in the location*.json file
        if 'Exterior' in location_data:
            location_data['Exterior']['Buildings'] = new_buildings
            location_data['Exterior']['BuildingCount'] = len(new_buildings)
        else:
            print(f"    No existing Buildings array found in {location_file}. Skipping update.")

        # Write the updated data back to the file
        with open(location_file, 'w') as f:
            json.dump(location_data, f, indent=4)

        print(f"Updated {location_file} with {len(new_buildings)} buildings.")

