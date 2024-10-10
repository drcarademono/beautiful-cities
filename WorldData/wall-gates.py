import json
import os
import glob
import random

# Function to calculate original coordinates from MapId
def calculate_original_coordinates(transformed_value):
    y = transformed_value // 1000
    x = transformed_value % 1000
    return x, y

# Function to read bytes from a file
def read_bytes_file(filename):
    with open(filename, 'rb') as file:
        return file.read()

# Function to get a byte at a specific (x, y) position in the data array
def get_byte_at_position(data, x, y, width):
    index = x + (y * width)
    return data[index]

# Function to interpret a byte and return road paths
def interpret_byte(byte_value):
    paths = {'N': False, 'NE': False, 'E': False, 'SE': False, 
             'S': False, 'SW': False, 'W': False, 'NW': False}

    if byte_value & 0b10000000:  # N
        paths['N'] = True
    if byte_value & 0b01000000:  # NE
        paths['NE'] = True
    if byte_value & 0b00100000:  # E
        paths['E'] = True
    if byte_value & 0b00010000:  # SE
        paths['SE'] = True
    if byte_value & 0b00001000:  # S
        paths['S'] = True
    if byte_value & 0b00000100:  # SW
        paths['SW'] = True
    if byte_value & 0b00000010:  # W
        paths['W'] = True
    if byte_value & 0b00000001:  # NW
        paths['NW'] = True

    return paths

# Modify the BlockNames array based on the presence of roads
def modify_block_names_with_roads(block_names, road_paths):
    # Define road replacement rules based on direction
    replacement_options = {
        'N': {
            'road': ['WALLAA08.TVRNAS00.RMB', 'WALLAA08.TVRNAS01.RMB', 'WALLAA08.TVRNAS02.RMB'],
            'no_road': ['WALLAA08.FARMAA00.RMB', 'WALLAA08.FARMAA01.RMB', 'WALLAA08.FARMAA02.RMB']
        },
        'E': {
            'road': ['WALLAA09.TVRNAS00.RMB', 'WALLAA09.TVRNAS01.RMB', 'WALLAA09.TVRNAS02.RMB'],
            'no_road': ['WALLAA09.FARMAA00.RMB', 'WALLAA09.FARMAA01.RMB', 'WALLAA09.FARMAA02.RMB']
        },
        'S': {
            'road': ['WALLAA10.TVRNAS00.RMB', 'WALLAA10.TVRNAS01.RMB', 'WALLAA10.TVRNAS02.RMB'],
            'no_road': ['WALLAA10.FARMAA00.RMB', 'WALLAA10.FARMAA01.RMB', 'WALLAA10.FARMAA02.RMB']
        },
        'W': {
            'road': ['WALLAA11.TVRNAS00.RMB', 'WALLAA11.TVRNAS01.RMB', 'WALLAA11.TVRNAS02.RMB'],
            'no_road': ['WALLAA11.FARMAA00.RMB', 'WALLAA11.FARMAA01.RMB', 'WALLAA11.FARMAA02.RMB']
        }
    }

    # Determine replacement direction for each WALLAA block
    for i, block_name in enumerate(block_names):
        if "WALLAA08.ROAD.RMB" in block_name:
            # Replace WALLAA08 based on the presence of a northern road
            if road_paths['N']:
                block_names[i] = random.choice(replacement_options['N']['road'])
            else:
                block_names[i] = random.choice(replacement_options['N']['no_road'])
        elif "WALLAA09.ROAD.RMB" in block_name:
            # Replace WALLAA09 based on the presence of an eastern road
            if road_paths['E']:
                block_names[i] = random.choice(replacement_options['E']['road'])
            else:
                block_names[i] = random.choice(replacement_options['E']['no_road'])
        elif "WALLAA10.ROAD.RMB" in block_name:
            # Replace WALLAA10 based on the presence of a southern road
            if road_paths['S']:
                block_names[i] = random.choice(replacement_options['S']['road'])
            else:
                block_names[i] = random.choice(replacement_options['S']['no_road'])
        elif "WALLAA11.ROAD.RMB" in block_name:
            # Replace WALLAA11 based on the presence of a western road
            if road_paths['W']:
                block_names[i] = random.choice(replacement_options['W']['road'])
            else:
                block_names[i] = random.choice(replacement_options['W']['no_road'])

    return block_names

# Extract road data from roadData.bytes file and determine paths for each location
def extract_and_modify_locations(source_directory, road_data_file):
    # Read the road data file into memory
    road_data = read_bytes_file(road_data_file)
    width = 1000  # Set the width of the Daggerfall map

    # Look for all location*.json files in the source directory
    json_files = glob.glob(os.path.join(source_directory, 'location*.json'))

    for file in json_files:
        try:
            with open(file, 'r') as json_file:
                data = json.load(json_file)

            # Check if MapId exists in the current file
            map_id = data.get("Exterior", {}).get("ExteriorData", {}).get("MapId")
            if map_id is not None:
                # Calculate the original coordinates
                x, y = calculate_original_coordinates(map_id)
                location_name = data.get("Name", os.path.basename(file))  # Use 'Name' or filename as the location name

                # Get the road paths for the calculated coordinates
                road_byte = get_byte_at_position(road_data, x, y, width)
                road_paths = interpret_byte(road_byte)

                # Check and modify BlockNames if applicable
                if "Exterior" in data and "ExteriorData" in data["Exterior"] and "BlockNames" in data["Exterior"]["ExteriorData"]:
                    block_names = data["Exterior"]["ExteriorData"]["BlockNames"]
                    modified_block_names = modify_block_names_with_roads(block_names, road_paths)
                    data["Exterior"]["ExteriorData"]["BlockNames"] = modified_block_names

                    # Save the modified JSON back to the file if changes were made
                    with open(file, 'w') as json_file:
                        json.dump(data, json_file, indent=4)
                    print(f"Modified and saved file: {file}")

            else:
                print(f"Skipping {file}: No MapId found.")

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON in file {file}: {e}")
        except IOError as e:
            print(f"Error processing file {file}: {e}")

# Usage
current_directory = '.'  # Set to current directory
road_data_file = 'roadData.bytes'  # Path to the roadData.bytes file
extract_and_modify_locations(current_directory, road_data_file)

