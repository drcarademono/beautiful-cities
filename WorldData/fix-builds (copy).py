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

def update_buildings():
    # Get a list of all location*.json files in the current directory
    location_files = glob.glob('location*.json')

    for location_file in location_files:
        print(f"Processing {location_file}")
        
        location_data = load_json_file(location_file)
        if location_data is None:
            continue

        new_buildings = []
        building_sector = 3

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

            # Update the fields for each building
            for building in buildings_to_add:
                building['NameSeed'] = random.randint(1, 30000)
                building['Sector'] = building_sector
                building_sector += 3
                building['LocationId'] = location_id

            new_buildings.extend(buildings_to_add)
            print(f"    Adding {len(buildings_to_add)} building(s) from {block_name} to Buildings array")

            # Running count of total buildings added
            print(f"    Total buildings added so far: {len(new_buildings)}")

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

if __name__ == '__main__':
    update_buildings()

