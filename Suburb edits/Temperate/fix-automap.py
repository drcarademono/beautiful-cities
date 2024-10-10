import json
import os
import re

def fix_invalid_json_escape_sequences(json_string):
    # Replace all invalid escape sequences with double-backslash \\
    # This captures any backslashes not followed by a valid escape character
    invalid_escapes = re.compile(r'\\(?!["\\/bfnrtu])')
    fixed_string = invalid_escapes.sub(r'\\\\', json_string)
    return fixed_string

def load_json_safely(filename):
    """
    Loads a JSON file and handles invalid escape sequences by pre-processing the content.
    """
    with open(filename, 'r', errors='replace') as file:  # Use errors='replace' to handle invalid escape sequences
        content = file.read()
        # Fix invalid escape sequences before loading JSON
        content = fix_invalid_json_escape_sequences(content)
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # Output debugging information if decoding fails
            print(f"JSONDecodeError: {e} in file: {filename}")
            print(f"Attempting to fix additional issues in JSON content...")
            # Try a more aggressive replacement approach if basic fix fails
            content = re.sub(r'\\x[0-9A-Fa-f]{2}', '', content)  # Remove any \x sequences
            content = re.sub(r'\\[^"]', '', content)  # Remove any other single backslashes
            return json.loads(content)

def copy_first_12_of_64_chunks(source_array, target_array):
    """
    Copies the first 12 values of every 64-value chunk from the source array
    to the target array.
    """
    num_chunks = min(len(source_array), len(target_array)) // 64
    for chunk_index in range(num_chunks):
        start = chunk_index * 64
        target_array[start:start + 12] = source_array[start:start + 12]
    return target_array

def copy_last_12_of_64_chunks(source_array, target_array):
    """
    Copies the last 12 values of every 64-value chunk from the source array
    to the target array.
    """
    num_chunks = min(len(source_array), len(target_array)) // 64
    for chunk_index in range(num_chunks):
        start = chunk_index * 64
        target_array[start + 52:start + 64] = source_array[start + 52:start + 64]
    return target_array

def process_road_file(road_filename, target_prefix, copy_method):
    # Load the road file safely
    road_data = load_json_safely(road_filename)
    
    # Extract AutoMapData array
    road_automap_data = road_data['RmbBlock']['FldHeader']['AutoMapData']
    
    # Iterate through all possible matching target files
    for target_filename in os.listdir('.'):
        # Match only the target files with the specified prefix and correct suffix
        if target_filename.startswith(target_prefix) and target_filename.endswith('.RMB.json') and target_filename != road_filename:
            # Load the target file safely
            target_data = load_json_safely(target_filename)
            
            # Get AutoMapData array from target file
            target_automap_data = target_data['RmbBlock']['FldHeader']['AutoMapData']
            
            # Copy the first or last 12 elements of every 64-value chunk depending on the copy_method
            if copy_method == 'first':
                target_automap_data = copy_first_12_of_64_chunks(road_automap_data, target_automap_data)
            elif copy_method == 'last':
                target_automap_data = copy_last_12_of_64_chunks(road_automap_data, target_automap_data)
            
            # Save changes back to the target file
            with open(target_filename, 'w') as target_file:
                json.dump(target_data, target_file, indent=4)
            
            print(f"Copied values from {road_filename} to {target_filename} successfully using {copy_method} 12 values.")

# Find all relevant files in the current directory and process them
for road_filename in os.listdir('.'):
    # Handle WALLAA08, WALLAA09, and WALLAA10 (copy first 12 values)
    if road_filename.startswith('WALLAA08.RMB.json') or road_filename.startswith('WALLAA09.RMB.json') or road_filename.startswith('WALLAA10.RMB.json'):
        target_prefix = 'WALLAA08.' if 'WALLAA08' in road_filename else 'WALLAA09.' if 'WALLAA09' in road_filename else 'WALLAA10.'
        process_road_file(road_filename, target_prefix, copy_method='first')
    
    # Handle WALLAA11 (copy last 12 values)
    elif road_filename.startswith('WALLAA11.RMB.json'):
        target_prefix = 'WALLAA11.'
        process_road_file(road_filename, target_prefix, copy_method='last')

