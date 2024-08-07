import json
import os
import random
import glob

def get_number_from_second_prefix(filename):
    """ Extract the number part from the second prefix in the block filename """
    parts = os.path.basename(filename).split('.')
    for part in parts:
        if 'FARMAA' in part or 'FARMBA' in part:
            return part[-2:]
    return ''

def update_block_names(directory, block_name, used_numbers, climate_type):
    """ Helper function to select a block name with preferences and restrictions """
    if block_name.startswith('EMTYAA00'):
        if climate_type == 'Desert':
            pattern_farm = f"{directory}/FARMBA*.RMB.json"
        else:
            pattern_farm = f"{directory}/FARMAA*.RMB.json"
        pattern_road = f"{directory}/ROAD*.RMB.json"
    else:
        index = block_name[6:8]
        if climate_type == 'Desert':
            pattern_farm = f"{directory}/WALLAA{index}.FARMBA*.RMB.json"
        else:
            pattern_farm = f"{directory}/WALLAA{index}.FARMAA*.RMB.json"
        pattern_road = f"{directory}/WALLAA{index}.ROAD*.RMB.json"

    matching_files_farm = glob.glob(pattern_farm)
    matching_files_road = glob.glob(pattern_road)

    matching_files = matching_files_farm + matching_files_road

    if climate_type == 'Desert':
        farm_special_files = [file for file in matching_files if 'FARMBA10' in file]
    else:
        farm_special_files = [file for file in matching_files if 'FARMAA10' in file]
    non_special_files = [file for file in matching_files if file not in farm_special_files]

    if matching_files:
        if random.random() < 0.67 and farm_special_files:  # 2/3 chance to pick special files if available
            candidate_files = farm_special_files
        else:
            candidate_files = non_special_files

        unused_files = [f for f in candidate_files if get_number_from_second_prefix(f) not in used_numbers]
        if not unused_files:  # Reset if all options have been used
            unused_files = candidate_files
            used_numbers.clear()  # Clear used numbers for this JSON
            print("All candidate files have been used, resetting used numbers.")

        print(f"Choosing from unused files: {[os.path.basename(f) for f in unused_files]}")
        chosen_file = random.choice(unused_files)
        used_number = get_number_from_second_prefix(chosen_file)
        print(f"Selected file: {os.path.basename(chosen_file)} with number: {used_number}")
        used_numbers.add(used_number)  # Add the chosen number to the used list
        print(f"Adding number {used_number} to the used numbers list")

        new_name = os.path.basename(chosen_file)[:-5]  # Remove '.json'
        print(f"Replacing {block_name} with {new_name}")
        return new_name, used_numbers
    return block_name, used_numbers

def main(directory):
    json_files = glob.glob(os.path.join(directory, 'location*.json'))

    for json_file in json_files:
        used_numbers = set()  # Set to track used numbers
        print(f"Processing file: {os.path.basename(json_file)}")
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        updated = False
        width = data['Exterior']['ExteriorData']['Width']
        height = data['Exterior']['ExteriorData']['Height']
        climate_type = data['Climate']['ClimateType']
        block_names = data['Exterior']['ExteriorData']['BlockNames']
        
        for i, block_name in enumerate(block_names):
            row = i // width
            col = i % width
            original_name = block_name

            # Check if the block is on the left, right, top, or bottom edges only if width or height is 8
            if (width == 8 and (col == 0 or col == width - 1)) or (height == 8 and (row == 0 or row == height - 1)):
                continue  # Skip updating for edge blocks

            if block_name.startswith('EMTYAA00'):
                new_block_name, used_numbers = update_block_names(directory, block_name, used_numbers, climate_type)
            elif block_name.startswith('WALLAA') and block_name.endswith('RMB'):
                index = block_name[6:8]
                if index.isdigit():
                    new_block_name, used_numbers = update_block_names(directory, block_name, used_numbers, climate_type)
                else:
                    continue
            else:
                continue

            if new_block_name != block_name:
                block_names[i] = new_block_name
                updated = True

        if updated:
            with open(json_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)

if __name__ == '__main__':
    # Use the current directory
    main(os.getcwd())

