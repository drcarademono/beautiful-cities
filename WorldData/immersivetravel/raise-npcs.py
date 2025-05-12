#!/usr/bin/env python3
import json
import glob
import sys

def fix_misc_flat(records):
    """
    Given a list of dicts (MiscFlatObjectRecords), set YPos to -4
    wherever it was -2.
    """
    for obj in records:
        if isinstance(obj, dict) and obj.get("YPos") == -2:
            obj["YPos"] = -4

def recurse(obj):
    """
    Recursively walk obj. Whenever you see a key 'MiscFlatObjectRecords'
    whose value is a list, call fix_misc_flat on it. Otherwise keep descending.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "MiscFlatObjectRecords" and isinstance(v, list):
                fix_misc_flat(v)
            else:
                recurse(v)
    elif isinstance(obj, list):
        for item in obj:
            recurse(item)

def process_file(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"✗ JSON error in {path}: {e}", file=sys.stderr)
        return

    recurse(data)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"✓ Updated {path}")

def main():
    files = glob.glob("*.RMB.json")
    if not files:
        print("No .RMB.json files found.", file=sys.stderr)
        sys.exit(1)

    for fn in files:
        process_file(fn)

if __name__ == "__main__":
    main()

