#!/usr/bin/env python3
import json
import glob
import sys

def update_flags(obj):
    """
    Recursively walk JSON structure. Whenever we hit a dict with
    TextureArchive, TextureRecord, FactionID==8642 and Flags==0,
    adjust Flags according to the rules.
    """
    if isinstance(obj, dict):
        # Check for our target entries
        if (
            obj.get("FactionID") == 8642
            and obj.get("Flags") == 0
            and isinstance(obj.get("TextureArchive"), int)
            and isinstance(obj.get("TextureRecord"), int)
        ):
            ta = obj["TextureArchive"]
            tr = obj["TextureRecord"]
            # 184/25, 357/3, 182/25 → Flags=2
            if (ta, tr) in [(184, 25), (357, 3), (182, 25)]:
                obj["Flags"] = 2
            # 184/19 → Flags=34
            elif (ta, tr) == (184, 19):
                obj["Flags"] = 34

        # Recurse into all values
        for v in obj.values():
            update_flags(v)

    elif isinstance(obj, list):
        for item in obj:
            update_flags(item)

def process_file(path):
    with open(path, "r") as f:
        data = json.load(f)

    update_flags(data)

    # Overwrite file with updated JSON
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"✓ Updated {path}")

def main():
    files = glob.glob("*.RMB.json")
    if not files:
        print("No .RMB.json files found here.", file=sys.stderr)
        sys.exit(1)

    for fn in files:
        try:
            process_file(fn)
        except Exception as e:
            print(f"✗ Error processing {fn}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()

