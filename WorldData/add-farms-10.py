import json
import os
import random
import glob

def update_block_names(directory, block_name, used_prefixes, available_prefixes):
    """ Helper function to select a block name with preferences and restrictions """
    if block_name.startswith('EMTYAA00'):
        pattern = f"{directory}/FARMAA*.RMB.json"
    else:
        index = block_name[6:8]
        pattern = f"{directory}/WALLAA{index}.FARMAA*.RMB.json"
    matching_files = glob.glob(pattern)
    print(f"Searching for files with pattern: {pattern} -> Found: {len(matching_files)} files")

    farm_aa10_files = [file for file in matching_files if 'FARMAA10' in file]
    non_farm_aa10_files = [file for file in matching_files if 'FARMAA10' not in file]

    if matching_files:
        if random.random() < 0.67 and farm_aa10_files:
            chosen_file = random.choice(farm_aa10_files)
        else:
            # Filter files that have not been used yet
            unused_files = [f for f in non_farm_aa10_files if f not in used_prefixes]
            if not unused_files:  # Reset if all options have been used
                unused_files = non_farm_aa10_files
                used_prefixes.clear()  # Clear used prefixes for this JSON

            chosen_file = random.choice(unused_files)
            # Add the chosen prefix to the used list
            used_prefixes.add(chosen_file)

        new_name = os.path.basename(chosen_file)[:-5]  # Remove '.json'
        print(f"Replacing {block_name} with {new_name}")
        return new_name, used_prefixes
    print(f"No matching files found for {block_name}, keeping original.")
    return block_name, used_prefixes


def main(directory):
    json_files = glob.glob(os.path.join(directory, 'location*.json'))
    print(f"Found {len(json_files)} location*.json files in directory.")

    for json_file in json_files:
        used_prefixes = set()  # Set to track used prefixes
        print(f"Processing file: {json_file}")
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        updated = False
        block_names = data['Exterior']['ExteriorData']['BlockNames']
        for i, block_name in enumerate(block_names):
            original_name = block_name
            if block_name == 'EMTYAA00.RMB':
                new_block_name, used_prefixes = update_block_names(directory, 'EMTYAA00.RMB', used_prefixes, block_names)
            elif block_name.startswith('WALLAA') and block_name.endswith('RMB'):
                index = block_name[6:8]
                if index.isdigit():
                    new_block_name, used_prefixes = update_block_names(directory, f'WALLAA{index}.RMB', used_prefixes, block_names)
                else:
                    continue
            else:
                continue

            if new_block_name != block_name:
                block_names[i] = new_block_name
                updated = True
                print(f"Updated {original_name} to {new_block_name}")

        if updated:
            with open(json_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
            print(f"Changes saved for {json_file}")
        else:
            print("No changes needed for this file.")

if __name__ == '__main__':
    # Use the current directory
    main(os.getcwd())

