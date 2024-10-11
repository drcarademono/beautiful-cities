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

# Modify the BlockNames array based on diagonal roads
def modify_block_names_with_diagonal_roads(block_names, road_paths):
    # Step 1: Check if there are diagonal roads but no cardinal roads
    cardinal_roads = road_paths['N'] or road_paths['E'] or road_paths['S'] or road_paths['W']
    diagonal_roads = road_paths['NE'] or road_paths['SE'] or road_paths['SW'] or road_paths['NW']

    if diagonal_roads and not cardinal_roads:
        # Step 2: Handle diagonal roads by choosing one component cardinal direction
        for diagonal in ['NE', 'SE', 'SW', 'NW']:
            if road_paths[diagonal]:
                # Randomly choose one of the component cardinal directions of the diagonal
                if diagonal == 'NE':
                    chosen_direction = random.choice(['N', 'E'])
                elif diagonal == 'SE':
                    chosen_direction = random.choice(['S', 'E'])
                elif diagonal == 'SW':
                    chosen_direction = random.choice(['S', 'W'])
                elif diagonal == 'NW':
                    chosen_direction = random.choice(['N', 'W'])

                # Replace the corresponding FARM block for the chosen direction
                block_key = chosen_direction  # 'N', 'E', 'S', or 'W'
                for i, block_name in enumerate(block_names):
                    # Only replace blocks with the correct prefixes: WALLAA08, WALLAA09, WALLAA10, WALLAA11
                    if block_name.startswith(("WALLAA08", "WALLAA09", "WALLAA10", "WALLAA11")):
                        if 'FARMAA' in block_name or 'FARMBA' in block_name:
                            # Extract the number and A/B part from the block name
                            block_prefix, block_suffix = block_name.split('FARM')
                            farm_type = block_suffix[0:2]  # AA or BA
                            block_number = block_suffix[2:4]  # Number part, e.g., 00

                            # Generate the replacement based on the type and number
                            if farm_type == 'AA':
                                block_names[i] = f"{block_prefix}TVRNAS{block_number}.RMB"
                            elif farm_type == 'BA':
                                block_names[i] = f"{block_prefix}TVRNBS{block_number}.RMB"
                            break  # Only change the first matching block

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
                    modified_block_names = modify_block_names_with_diagonal_roads(block_names, road_paths)
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

