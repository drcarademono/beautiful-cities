import os
import json
import re

# Function to fix invalid escape sequences in the JSON content
def fix_invalid_escapes(json_content):
    # Escape invalid escape sequences in JSON (e.g., \x, \b, \u with incorrect values)
    json_content = re.sub(r'\\(?!["/bfnrtu])', r'\\\\', json_content)  # Handle other escape characters
    return json_content

# Get the current directory
current_dir = os.getcwd()

# List all the files in the directory
files = os.listdir(current_dir)

# Process each *-travel.json file
for travel_file in files:
    if travel_file.endswith('-travel.json') and 'meta' not in travel_file:
        # Extract the prefix (everything before '-travel.json')
        prefix = travel_file.replace('-travel.json', '')

        # Find all corresponding files (without '-travel.json' and not containing 'meta')
        corresponding_files = [file for file in files if file.startswith(prefix) and not file.endswith('-travel.json') and 'meta' not in file]
        
        if corresponding_files:
            # Open the *-travel.json file and load the data
            with open(os.path.join(current_dir, travel_file), 'r') as travel_json:
                travel_data = json.load(travel_json)

            # Process each corresponding file
            for corresponding_file in corresponding_files:
                # Open the corresponding file, handle possible invalid escapes
                with open(os.path.join(current_dir, corresponding_file), 'r') as corresponding_json:
                    try:
                        corresponding_data = json.load(corresponding_json)
                    except json.JSONDecodeError:
                        # If we encounter a JSON decode error, fix invalid escapes and try again
                        corresponding_json.seek(0)  # Reset file pointer
                        raw_json_content = corresponding_json.read()
                        fixed_json_content = fix_invalid_escapes(raw_json_content)
                        corresponding_data = json.loads(fixed_json_content)

                # Ensure 'RmbBlock' exists and append the Misc3dObjectRecords and MiscFlatObjectRecords from the travel file into it
                if 'RmbBlock' not in corresponding_data:
                    corresponding_data['RmbBlock'] = {}

                # Ensure Misc3dObjectRecords and MiscFlatObjectRecords exist and append them
                if 'Misc3dObjectRecords' not in corresponding_data['RmbBlock']:
                    corresponding_data['RmbBlock']['Misc3dObjectRecords'] = []

                if 'MiscFlatObjectRecords' not in corresponding_data['RmbBlock']:
                    corresponding_data['RmbBlock']['MiscFlatObjectRecords'] = []

                # Append the Misc3dObjectRecords from the travel file into the corresponding file
                corresponding_data['RmbBlock']['Misc3dObjectRecords'].extend(travel_data.get('Misc3dObjectRecords', []))

                # Append the MiscFlatObjectRecords from the travel file into the corresponding file
                corresponding_data['RmbBlock']['MiscFlatObjectRecords'].extend(travel_data.get('MiscFlatObjectRecords', []))

                # Save the updated corresponding file
                with open(os.path.join(current_dir, corresponding_file), 'w') as corresponding_json:
                    json.dump(corresponding_data, corresponding_json, indent=4)

                print(f"Appended Misc3dObjectRecords and MiscFlatObjectRecords from {travel_file} to {corresponding_file}")
        else:
            print(f"No corresponding file found for {travel_file}")

