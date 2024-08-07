import json
import os
import random
import glob

def update_block_names(directory, block_name):
    """ Helper function to get a random file name matching the pattern based on block_name """
    if block_name.startswith('EMTYAA00'):
        pattern = f"{directory}/FARMAA*.RMB.json"  # Pattern for matching FARMAA**.RMB.json files
    else:  # For WALLAAxx patterns
        index = block_name[6:8]  # Extract the number like '01' from 'WALLAA01.RMB'
        pattern = f"{directory}/WALLAA{index}.FARMAA*.RMB.json"  # Correct pattern for WALLAAxx
    matching_files = glob.glob(pattern)
    print(f"Searching for files with pattern: {pattern} -> Found: {len(matching_files)} files")
    if matching_files:
        # Choose a random file and remove the '.json' part before returning
        chosen_file = random.choice(matching_files)
        new_name = os.path.basename(chosen_file)[:-5]  # Remove the last 5 chars (.json)
        print(f"Replacing {block_name} with {new_name}")
        return new_name
    print(f"No matching files found for {block_name}, keeping original.")
    return block_name  # Return the original name if no match found

def main(directory):
    # Path to the directory containing the JSON files
    json_files = glob.glob(os.path.join(directory, 'location*.json'))
    print(f"Found {len(json_files)} location*.json files in directory.")

    for json_file in json_files:
        print(f"Processing file: {json_file}")
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Check and update block names if they match certain patterns
        updated = False
        block_names = data['Exterior']['ExteriorData']['BlockNames']
        for i, block_name in enumerate(block_names):
            original_name = block_name
            if block_name == 'EMTYAA00.RMB':
                new_block_name = update_block_names(directory, 'EMTYAA00.RMB')
            elif block_name.startswith('WALLAA') and block_name.endswith('RMB'):
                index = block_name[6:8]  # Extract the number from something like 'WALLAA01.RMB'
                if index.isdigit():
                    new_block_name = update_block_names(directory, f'WALLAA{index}.RMB')
                else:
                    continue
            else:
                continue

            if new_block_name != block_name:
                block_names[i] = new_block_name
                updated = True
                print(f"Updated {original_name} to {new_block_name}")

        # Save the file back if updates were made
        if updated:
            with open(json_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
            print(f"Changes saved for {json_file}")
        else:
            print("No changes needed for this file.")

if __name__ == '__main__':
    # Use the current directory
    main(os.getcwd())

