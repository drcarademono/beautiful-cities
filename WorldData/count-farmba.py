#!/usr/bin/env python3
import json
import glob
import re
from collections import Counter

# Regex to match exactly FARMBA followed by two digits, then .RMB
pattern = re.compile(r'^FARMBA\d{2}\.RMB$')

counts = Counter()

for path in glob.glob('location*.json'):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Warning: could not read {path}: {e}")
        continue

    block_names = (
        data
        .get('Exterior', {})
        .get('ExteriorData', {})
        .get('BlockNames', [])
    )

    for name in block_names:
        if pattern.match(name):
            counts[name] += 1

# Print a sorted tally
print("Counts of FARMBA**.RMB in BlockNames:")
for variant in sorted(counts):
    print(f"  {variant}: {counts[variant]}")

