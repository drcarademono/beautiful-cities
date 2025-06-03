#!/usr/bin/env python3
import json, glob, re
from pathlib import Path

pattern = re.compile(r'^MARKAA(\d+)\.RMB$')

for path in glob.glob('location*.json'):
    file_path = Path(path)
    try:
        data = json.loads(file_path.read_text(encoding='utf-8'))
    except (IOError, json.JSONDecodeError) as e:
        print(f"Warning: could not read {file_path}: {e}")
        continue

    ext = data.get('Exterior', {}).get('ExteriorData', {})
    block_names = ext.get('BlockNames', [])
    if not isinstance(block_names, list):
        continue

    changed = False
    new_block_names = []
    for name in block_names:
        m = pattern.match(name)
        if m:
            num = int(m.group(1))
            # even → 00, odd → 01
            replacement = 'MARKAA00.RMB' if num % 2 == 0 else 'MARKAA01.RMB'
            if name != replacement:
                changed = True
            new_block_names.append(replacement)
        else:
            new_block_names.append(name)

    if changed:
        data['Exterior']['ExteriorData']['BlockNames'] = new_block_names
        try:
            file_path.write_text(json.dumps(data, indent=4), encoding='utf-8')
            print(f"Updated {file_path}")
        except IOError as e:
            print(f"Error writing {file_path}: {e}")

