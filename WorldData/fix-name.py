import os
import json
from glob import glob


def preprocess_json(file_path, placeholder="_BACKSLASH_"):
    """Replace backslashes with a placeholder in the file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        content = content.replace("\\", placeholder)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        print(f"Error preprocessing {file_path}: {e}")


def restore_backslashes(file_path, placeholder="_BACKSLASH_"):
    """Restore backslashes from the placeholder in the file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        content = content.replace(placeholder, "\\")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        print(f"Error restoring backslashes in {file_path}: {e}")


def load_json(file_path):
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for {file_path}: {e}")
    except Exception as e:
        print(f"Unexpected error loading {file_path}: {e}")
    return None


def save_json(file_path, data):
    """Save JSON data to a file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving JSON for {file_path}: {e}")


def update_name(file_path):
    """Update the Name field in the JSON to match the filename without the .json extension."""
    placeholder = "_BACKSLASH_"
    preprocess_json(file_path, placeholder)

    # Load the JSON file
    data = load_json(file_path)
    if data is None:
        print(f"Skipping {file_path} due to loading errors.")
        restore_backslashes(file_path, placeholder)
        return

    # Update the Name field
    filename = os.path.basename(file_path).replace(".json", "")
    if "Name" in data:
        old_name = data["Name"]
        data["Name"] = filename
        print(f"Updated Name from {old_name} to {filename} in {file_path}")

    # Save the updated JSON file
    save_json(file_path, data)

    # Restore original backslashes
    restore_backslashes(file_path, placeholder)


def main():
    # Find all RMB.json files in the current directory
    rmb_files = glob("*.RMB.json")

    for file_path in rmb_files:
        print(f"Processing {file_path}...")
        update_name(file_path)


if __name__ == "__main__":
    main()

