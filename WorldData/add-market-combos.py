import os
import json
import glob
import random

# Allowed candidate numbers:
# For even (MARKAA00) we allow even numbers 0, 2, 4, …, 254.
allowed_even = list(range(0, 255, 2))
# For odd (MARKAA01) we allow odd numbers 1, 3, 5, …, 127.
allowed_odd = list(range(1, 128, 2))

# Global usage dictionaries – candidate values used so far (lower usage => more likely)
usage_even = {num: 0 for num in allowed_even}
usage_odd = {num: 0 for num in allowed_odd}

def load_json_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def save_json_file(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Saved {filepath}")
    except Exception as e:
        print(f"Error saving {filepath}: {e}")

def linear_target(count, min_count=35, max_count=64, min_val=0, max_val=254):
    """
    For even (MARKAA00): when count is max_count, target is min_val;
    when count is min_count, target is max_val.
    """
    count = max(min_count, min(max_count, count))
    frac = (count - min_count) / (max_count - min_count)
    return round(max_val - frac * (max_val - min_val))

def linear_target_odd(count, min_count=35, max_count=64, min_val=1, max_val=127):
    """
    For odd (MARKAA01): when count is max_count, target is min_val;
    when count is min_count, target is max_val.
    """
    count = max(min_count, min(max_count, count))
    frac = (count - min_count) / (max_count - min_count)
    return round(max_val - frac * (max_val - min_val))

def adjust_parity(candidate, desired_parity):
    # Ensure candidate has the desired parity: 0 for even, 1 for odd.
    if candidate % 2 != desired_parity:
        candidate += 1
    return candidate

def choose_candidate(target, allowed, usage_dict, delta_low, delta_high):
    """
    Build a candidate pool from allowed numbers in the range
    [target - delta_low, target + delta_high] and choose one
    weighted inversely by its usage.
    """
    lower_bound = target - delta_low
    upper_bound = target + delta_high
    pool = [num for num in allowed if lower_bound <= num <= upper_bound]
    if not pool:
        d_low, d_high = delta_low, delta_high
        while not pool and (d_low < max(allowed) or d_high < max(allowed)):
            d_low += 5
            d_high += 5
            lower_bound = target - d_low
            upper_bound = target + d_high
            pool = [num for num in allowed if lower_bound <= num <= upper_bound]
    weights = [1 / (1 + usage_dict[num]) for num in pool]
    chosen = random.choices(pool, weights=weights, k=1)[0]
    usage_dict[chosen] += 1
    return chosen

def format_candidate(candidate):
    """
    If candidate is a single digit, pad with a leading 0.
    Otherwise, return the candidate as a string.
    """
    if candidate < 10:
        return f"0{candidate}"
    return f"{candidate}"

def process_location_file(filepath):
    data = load_json_file(filepath)
    if not data:
        return False

    exterior = data.get("Exterior", {})
    ext_data = exterior.get("ExteriorData", {})
    blocknames = ext_data.get("BlockNames")
    if not isinstance(blocknames, list):
        return False

    total_blocks = len(blocknames)
    # Rule 1: if there are exactly 64 BlockNames, leave MARKAA00 and MARKAA01 unchanged.
    if total_blocks == 64:
        return False

    changed = False

    # Determine adjustments common to the location.
    port_val = ext_data.get("PortTownAndUnknown", 0)
    is_capital = (data.get("Name") and data.get("RegionName") and data["Name"] == data["RegionName"])

    # Process each block name.
    for i, name in enumerate(blocknames):
        if name == "MARKAA00.RMB":
            base = linear_target(total_blocks, min_val=0, max_val=254)
            target = adjust_parity(base, 0)
            # For even, use a random range of ±10.
            candidate = choose_candidate(target, allowed_even, usage_even, delta_low=10, delta_high=10)
            # Adjustment: subtract 20 for port and an additional 20 for capital.
            adjustment = 0
            if isinstance(port_val, (int, float)) and port_val > 0:
                adjustment += 20
            if is_capital:
                adjustment += 20
            candidate_adjusted = candidate - adjustment
            # Clamp to minimum allowed (0 for even)
            if candidate_adjusted < allowed_even[0]:
                candidate_adjusted = allowed_even[0]
            new_name = f"MARKAA{format_candidate(candidate_adjusted)}.RMB"
            blocknames[i] = new_name
            changed = True
        elif name == "MARKAA01.RMB":
            base = linear_target_odd(total_blocks, min_val=1, max_val=127)
            target = adjust_parity(base, 1)
            # For odd, use a random range of ±6.
            candidate = choose_candidate(target, allowed_odd, usage_odd, delta_low=6, delta_high=6)
            adjustment = 0
            if isinstance(port_val, (int, float)) and port_val > 0:
                adjustment += 10
            if is_capital:
                adjustment += 10
            candidate_adjusted = candidate - adjustment
            # Clamp to minimum allowed (1 for odd)
            if candidate_adjusted < allowed_odd[0]:
                candidate_adjusted = allowed_odd[0]
            new_name = f"MARKAA{format_candidate(candidate_adjusted)}.RMB"
            blocknames[i] = new_name
            changed = True

    if changed:
        save_json_file(filepath, data)
    return changed

def process_all_locations():
    files = glob.glob("location*.json")
    if not files:
        print("No location*.json files found.")
        return

    processed = 0
    for filepath in files:
        if process_location_file(filepath):
            processed += 1
    print(f"\nProcessed {processed} files out of {len(files)}.")

if __name__ == "__main__":
    process_all_locations()

