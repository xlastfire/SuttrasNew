from glob import glob
import json
import os
from tqdm import tqdm

# Configuration
path_filepath = 'paths'
index_filepath = 'index'

def get_file(path):
    """Loads JSON data from a file, returns empty list if file doesn't exist."""
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_file(obj, path):
    """Saves object to a JSON file with pretty printing."""
    with open(path, 'w', encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=4)

# 1. Load existing data
path_data = get_file(path_filepath)
index_data = get_file(index_filepath)

# 2. Track existing IDs for fast lookup
index_added_ids = {each['id'] for each in index_data if isinstance(each, dict) and 'id' in each}

# 3. Process files
files = glob('*.json')
starting_count = len(index_data)
added_count = 0
error_files = []

print("ගොනු පරීක්ෂා කරමින් පවතී...\n")

for file_name in tqdm(files, desc="Processing JSON files"):
    
    if file_name in [path_filepath, index_filepath]:
        continue

    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        print(f"Error reading {file_name}. Skipping...")
        error_files.append(file_name)
        continue

    if not isinstance(data, dict):
        print(f"වැරදි දත්ත ව්‍යුහය (Not a JSON object/dict): {file_name}")
        error_files.append(file_name)
        continue

    item_id = data.get('id')
    if not item_id:
        continue

    if item_id not in path_data:
        path_data.append(item_id)

    if item_id not in index_added_ids:
        temp = {
            "nikaya": data.get("nikaya"),
            "vagga": data.get("vagga"),
            "sutta_title": data.get("sutta_title"),
            "short_summary": data.get('short_summary'),
            "id": item_id
        }

        discovery = data.get('discovery_content')
        if isinstance(discovery, dict) and 'short_summary' in discovery:
            temp['short_summary'] = discovery['short_summary']

        index_data.append(temp)
        index_added_ids.add(item_id)
        added_count += 1

# 4. Save results
save_file(path_data, path_filepath)
save_file(index_data, index_filepath)

# 5. Final Report
print("-" * 30)
print("Processing Complete")
print("-" * 30)
print(f"Files scanned:      {len(files)}")
print(f"Existing in index:  {starting_count}")
print(f"New items added:    {added_count}")
print(f"Final total count:  {len(index_data)}")
print("-" * 30)

if error_files:
    print("\nදෝෂ සහිත ගොනු ලැයිස්තුව (Error Files):")
    for err in error_files:
        print(f"- {err}")
    print("-" * 30)