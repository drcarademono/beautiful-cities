import os
import json
import glob
import statistics

def load_json_file(file_path, placeholder="__BACKSLASH__"):
    """Loads a JSON file from file_path and returns the parsed JSON object."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            raw_content = file.read()
            # (Optional) Pre/post processing for backslashes could be added here if needed.
            return json.loads(raw_content)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
    return None

def count_location_blocks(data):
    """
    Given a location JSON object, counts blocks from:
      - Exterior.Buildings (if a list)
      - Exterior.ExteriorData.BlockNames (if a list)
      - Dungeon.Blocks (if a list)
    Returns a tuple (buildings_count, blocknames_count, dungeon_count, total_count)
    """
    exterior = data.get("Exterior", {})
    buildings = exterior.get("Buildings", [])
    buildings_count = len(buildings) if isinstance(buildings, list) else 0

    exterior_data = exterior.get("ExteriorData", {})
    blocknames = exterior_data.get("BlockNames", [])
    blocknames_count = len(blocknames) if isinstance(blocknames, list) else 0

    dungeon = data.get("Dungeon", {})
    dungeon_blocks = dungeon.get("Blocks")
    dungeon_count = len(dungeon_blocks) if isinstance(dungeon_blocks, list) else 0

    total_count = buildings_count + blocknames_count + dungeon_count
    return buildings_count, blocknames_count, dungeon_count, total_count

def process_locations():
    # Use glob to get all files that start with "location" and end with ".json"
    # (Adjust pattern as needed, e.g. "Location*.json")
    location_files = glob.glob("location*.json")
    if not location_files:
        print("No location*.json files found in the current directory.")
        return

    # Lists to accumulate counts
    buildings_counts = []
    blocknames_counts = []
    dungeon_counts = []
    total_counts = []
    processed_files = []

    # Process each file
    for filepath in location_files:
        data = load_json_file(filepath)
        if not data:
            continue

        # Check if the file has an ExteriorData.BlockNames array
        exterior_data = data.get("Exterior", {}).get("ExteriorData", {})
        blocknames = exterior_data.get("BlockNames", [])
        if not isinstance(blocknames, list):
            continue

        # Check if any block name equals "MARKAA00.RMB" or "MARKAA01.RMB"
        if not any(b == "MARKAA00.RMB" or b == "MARKAA01.RMB" for b in blocknames):
            continue

        # If the location qualifies, count its blocks.
        b_count, bn_count, d_count, total = count_location_blocks(data)
        buildings_counts.append(b_count)
        blocknames_counts.append(bn_count)
        dungeon_counts.append(d_count)
        total_counts.append(total)
        processed_files.append(filepath)
        print(f"Processed {filepath}: Buildings={b_count}, BlockNames={bn_count}, Dungeon={d_count}, Total={total}")

    if not processed_files:
        print("No location files contained a MARKAA00.RMB or MARKAA01.RMB block.")
        return

    print("\nSummary Statistics for location files containing a MARKAA00.RMB or MARKAA01.RMB block:")
    print(f"Number of files: {len(processed_files)}")
    
    def summarize(name, counts):
        return (min(counts), max(counts), statistics.mean(counts), statistics.median(counts))
    
    b_min, b_max, b_mean, b_median = summarize("Buildings", buildings_counts)
    bn_min, bn_max, bn_mean, bn_median = summarize("BlockNames", blocknames_counts)
    d_min, d_max, d_mean, d_median = summarize("Dungeon Blocks", dungeon_counts)
    t_min, t_max, t_mean, t_median = summarize("Total Blocks", total_counts)
    
    print(f"Buildings: min={b_min}, max={b_max}, mean={b_mean:.2f}, median={b_median}")
    print(f"BlockNames: min={bn_min}, max={bn_max}, mean={bn_mean:.2f}, median={bn_median}")
    print(f"Dungeon Blocks: min={d_min}, max={d_max}, mean={d_mean:.2f}, median={d_median}")
    print(f"Combined Total: min={t_min}, max={t_max}, mean={t_mean:.2f}, median={t_median}")

if __name__ == "__main__":
    process_locations()

