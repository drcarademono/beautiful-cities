import os
import json
import glob
import random

# Allowed candidate numbers:
# For MARKAA00 (even) we allow even numbers 0, 2, 4, …, 254.
allowed_even = list(range(0, 255, 2))
# For MARKAA01 (odd) we allow odd numbers 1, 3, 5, …, 127.
allowed_odd = list(range(1, 128, 2))

# Global usage dictionaries – candidate values used so far (lower count = more likely)
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
    Given the total count of blocks, linearly interpolate a target value.
    For even (MARKAA00): when count is max_count, target should be min_val;
    when count is min_count, target should be max_val.
    """
    # Clamp count to [min_count, max_count]
    count = max(min_count, min(max_count, count))
    # Linear interpolation: higher count -> lower candidate value.
    # Compute fraction = (count - min_count) / (max_count - min_count)
    frac = (count - min_count) / (max_count - min_count)
    # Then target = max_val - frac*(max_val - min_val)
    return round(max_val - frac * (max_val - min_val))

def linear_target_odd(count, min_count=35, max_count=64, min_val=1, max_val=127):
    """
    For odd (MARKAA01): when count is max_count, target should be min_val;
    when count is min_count, target should be max_val.
    """
    count = max(min_count, min(max_count, count))
    frac = (count - min_count) / (max_count - min_count)
    return round(max_val - frac * (max_val - min_val))

def adjust_parity(candidate, desired_parity):
    # desired_parity: 0 for even, 1 for odd.
    if candidate % 2 != desired_parity:
        # Adjust by one (if candidate is 0 and we want even, that's fine; otherwise add 1)
        candidate += 1
    return candidate

def choose_candidate(target, allowed, usage_dict, delta=5):
    """
    Given a target value, allowed candidate list, usage dict, and a delta range,
    create a candidate pool of numbers within ±delta of target (and that are in allowed).
    Then choose one candidate weighted by 1/(1+usage).
    """
    # Build candidate pool: numbers in allowed with abs(candidate-target) <= delta.
    pool = [num for num in allowed if abs(num - target) <= delta]
    if not pool:
        # If empty, expand delta by 1 and try again.
        d = delta
        while not pool and d < max(allowed):
            d += 1
            pool = [num for num in allowed if abs(num - target) <= d]
    # Compute weights: lower usage -> higher weight.
    weights = [1 / (1 + usage_dict[num]) for num in pool]
    chosen = random.choices(pool, weights=weights, k=1)[0]
    # Increment usage.
    usage_dict[chosen] += 1
    return chosen

def process_location_file(filepath):
    data = load_json_file(filepath)
    if not data:
        return False
    # Navigate to BlockNames array: data["Exterior"]["ExteriorData"]["BlockNames"]
    exterior = data.get("Exterior", {})
    ext_data = exterior.get("ExteriorData", {})
    blocknames = ext_data.get("BlockNames")
    if not isinstance(blocknames, list):
        return False

    total_blocks = len(blocknames)
    changed = False

    # Process each element of blocknames.
    # We assume that if an element equals exactly "MARKAA00.RMB" or "MARKAA01.RMB",
    # we replace it.
    for i, name in enumerate(blocknames):
        if name == "MARKAA00.RMB":
            # Compute target for even numbers using linear mapping.
            base = linear_target(total_blocks, min_val=0, max_val=254)
            target = adjust_parity(base, 0)  # ensure even
            candidate = choose_candidate(target, allowed_even, usage_even, delta=5)
            new_name = f"MARKAA00-{candidate:03d}.RMB"
            blocknames[i] = new_name
            changed = True
        elif name == "MARKAA01.RMB":
            base = linear_target_odd(total_blocks, min_val=1, max_val=127)
            target = adjust_parity(base, 1)  # ensure odd
            candidate = choose_candidate(target, allowed_odd, usage_odd, delta=5)
            new_name = f"MARKAA01-{candidate:03d}.RMB"
            blocknames[i] = new_name
            changed = True

    if changed:
        # Save changes (overwrite original file)
        save_json_file(filepath, data)
    return changed

def process_all_locations():
    # Look for files matching location*.json (case-insensitive could be added if needed)
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

