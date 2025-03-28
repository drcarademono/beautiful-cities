import os
import json
import re
import random

VANILLA_DIR = "vanillaloc"
TARGET_BLOCK = "PAWNAL03.RMB"

def fix_invalid_escapes(json_string):
    """Escape invalid backslashes in the JSON string."""
    return re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', json_string)

def load_json_safe(filepath):
    """Load a JSON file with invalid escape handling."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            raw = f.read()
        fixed = fix_invalid_escapes(raw)
        return json.loads(fixed)
    except Exception as e:
        print(f"Failed to read {filepath}: {e}")
        return None

def save_json_safe(filepath, data):
    """Save JSON data with UTF-8 encoding and indenting."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Failed to write {filepath}: {e}")

def get_block_names(data):
    """Extract BlockNames list from the JSON data, if present."""
    return data.get("Exterior", {}).get("ExteriorData", {}).get("BlockNames", [])

def set_block_names(data, block_names):
    """Set BlockNames list inside the JSON data."""
    if "Exterior" in data and "ExteriorData" in data["Exterior"]:
        data["Exterior"]["ExteriorData"]["BlockNames"] = block_names

def main():
    for filename in os.listdir("."):
        if not filename.endswith(".json"):
            continue

        base_path = filename
        vanilla_path = os.path.join(VANILLA_DIR, filename)

        if not os.path.exists(vanilla_path):
            continue

        vanilla_data = load_json_safe(vanilla_path)
        base_data = load_json_safe(base_path)

        if vanilla_data is None or base_data is None:
            continue

        vanilla_blocks = get_block_names(vanilla_data)
        base_blocks = get_block_names(base_data)

        # Only proceed if vanilla has it and base does not
        if TARGET_BLOCK in vanilla_blocks and TARGET_BLOCK not in base_blocks:
            # Find all PAWNAL**.RMB blocks in base
            candidate_indices = [
                idx for idx, b in enumerate(base_blocks)
                if re.match(r"PAWNAL..\.RMB", b)
            ]

            if not candidate_indices:
                print(f"{filename}: No PAWNAL**.RMB blocks to replace.")
                continue

            chosen_idx = random.choice(candidate_indices)
            old_value = base_blocks[chosen_idx]
            base_blocks[chosen_idx] = TARGET_BLOCK
            set_block_names(base_data, base_blocks)

            save_json_safe(base_path, base_data)
            print(f"{filename}: Replaced {old_value} -> {TARGET_BLOCK}")

    print("\nDone.")

if __name__ == "__main__":
    main()

