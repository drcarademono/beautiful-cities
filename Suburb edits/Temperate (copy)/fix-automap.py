import json
import os
import re

def fix_invalid_json_escape_sequences(json_string):
    invalid_escapes = re.compile(r'\\(?!["\\/bfnrtu])')
    fixed_string = invalid_escapes.sub(r'\\\\', json_string)
    return fixed_string

def load_json_safely(filename):
    """
    Loads a JSON file and handles invalid escape sequences by pre-processing the content.
    """
    try:
        with open(filename, 'r', errors='replace') as file:  # Use errors='replace' to handle invalid escape sequences
            content = file.read()
            
            # Check if file is empty
            if not content.strip():
                print(f"Skipping empty file: {filename}")
                return None
            
            # Fix invalid escape sequences before loading JSON
            content = fix_invalid_json_escape_sequences(content)
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
        print(f"Error loading {filename}: {e}")
        return None

def copy_last_768_values(source_array, target_array):
    if len(source_array) < 768:
        print("Source array does not have 768 values to copy.")
        return target_array
    target_array[-768:] = source_array[-768:]
    return target_array

def copy_first_768_values(source_array, target_array):
    if len(source_array) < 768:
        print("Source array does not have 768 values to copy.")
        return target_array
    target_array[:768] = source_array[:768]
    return target_array

def copy_first_12_of_64_chunks(source_array, target_array):
    num_chunks = min(len(source_array), len(target_array)) // 64
    for chunk_index in range(num_chunks):
        start = chunk_index * 64
        target_array[start:start + 12] = source_array[start:start + 12]
    return target_array

def copy_last_12_of_64_chunks(source_array, target_array):
    num_chunks = min(len(source_array), len(target_array)) // 64
    for chunk_index in range(num_chunks):
        start = chunk_index * 64
        target_array[start + 52:start + 64] = source_array[start + 52:start + 64]
    return target_array

def process_road_file(road_filename, target_prefix, copy_method):
    road_data = load_json_safely(road_filename)
    if not road_data:
        print(f"Skipping {road_filename} due to loading error.")
        return
    
    # Extract AutoMapData array
    try:
        road_automap_data = road_data['RmbBlock']['FldHeader']['AutoMapData']
    except KeyError:
        print(f"AutoMapData not found in {road_filename}. Skipping file.")
        return
    
    # Iterate through all possible matching target files in the directory
    for target_filename in os.listdir('.'):
        # Match only the target files with the specified prefix and correct suffix
        if target_filename.startswith(target_prefix) and target_filename.endswith('.RMB.json') and target_filename != road_filename:
            target_data = load_json_safely(target_filename)
            if not target_data:
                print(f"Skipping {target_filename} due to loading error.")
                continue
            
            # Get AutoMapData array from target file
            try:
                target_automap_data = target_data['RmbBlock']['FldHeader']['AutoMapData']
            except KeyError:
                print(f"AutoMapData not found in {target_filename}. Skipping file.")
                continue

            # Apply the copying method based on the file type
            if copy_method == 'last_768':
                target_automap_data = copy_last_768_values(road_automap_data, target_automap_data)
            elif copy_method == 'first_768':
                target_automap_data = copy_first_768_values(road_automap_data, target_automap_data)
            elif copy_method == 'first':
                target_automap_data = copy_first_12_of_64_chunks(road_automap_data, target_automap_data)
            elif copy_method == 'last':
                target_automap_data = copy_last_12_of_64_chunks(road_automap_data, target_automap_data)

            # Save changes back to the target file
            with open(target_filename, 'w') as target_file:
                json.dump(target_data, target_file, indent=4)
            
            print(f"Copied values from {road_filename} to {target_filename} successfully using {copy_method} method.")

# Find all relevant files in the current directory and process them
for road_filename in os.listdir('.'):
    # Handle WALLAA08 (copy last 768 values)
    if road_filename.startswith('WALLAA08.RMB.json'):
        process_road_file(road_filename, 'WALLAA08.', copy_method='last_768')
    
    # Handle WALLAA09 (copy first 12 values of 64-value chunks)
    elif road_filename.startswith('WALLAA09.RMB.json'):
        process_road_file(road_filename, 'WALLAA09.', copy_method='first')
    
    # Handle WALLAA10 (copy first 768 values)
    elif road_filename.startswith('WALLAA10.RMB.json'):
        process_road_file(road_filename, 'WALLAA10.', copy_method='first_768')
    
    # Handle WALLAA11 (copy last 12 values of 64-value chunks)
    elif road_filename.startswith('WALLAA11.RMB.json'):
        process_road_file(road_filename, 'WALLAA11.', copy_method='last')

