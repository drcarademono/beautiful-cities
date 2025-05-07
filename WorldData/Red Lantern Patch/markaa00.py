#!/usr/bin/env python3
import json
import glob
import re
from pathlib import Path

# Match MARKAA + any number of digits + .RMB
pattern = re.compile(r'^MARKAA(\d+)\.RMB$')

for path in glob.glob('location*.json'):
    file_path = Path(path)
    try:
        data = json.loads(file_path.read_text(encoding='utf-8'))
    except (IOError, json.JSONDecodeError) as e:
        print(f"Warning: could not read {file_path}: {e}")
        continue

    ext_data = data.get('Exterior', {}).get('ExteriorData', {})
    block_names = ext_data.get('BlockNames', [])
    if not isinstance(block_names, list):
        continue

    changed = False
    new_block_names = []
    for name in block_names:
        m = pattern.match(name)
        if m:
            num = int(m.group(1))
            if num % 2 == 0:
                # even: replace with MARKAA00.RMB
                if name != 'MARKAA00.RMB':
                    new_block_names.append('MARKAA00.RMB')
                    changed = True
                else:
                    new_block_names.append(name)
            else:
                # odd: leave unchanged
                new_block_names.append(name)
        else:
            # not a MARKAA… entry: leave as‑is
            new_block_names.append(name)

    if changed:
        data['Exterior']['ExteriorData']['BlockNames'] = new_block_names
        try:
            file_path.write_text(json.dumps(data, indent=4), encoding='utf-8')
            print(f"Updated {file_path}")
        except IOError as e:
            print(f"Error writing {file_path}: {e}")

