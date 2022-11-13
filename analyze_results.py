import os
import json

results_folder = "results"

files = os.listdir(results_folder)

for file in files:
    if ".json" not in file:
        continue

    print(file + " results:")
    with open(os.path.join(results_folder, file), 'r') as fhand:
        res = json.load(fhand)

    total_agg = 0
    total_orig = 0
    total_same = 0
    for key in res:
        if res[key] == 'agg':
            total_agg += 1
        elif res[key] == 'orig':
            total_orig += 1
        elif res[key] == 'same':
            total_same += 1
    print(f"Agg:  {total_agg}")
    print(f"Orig: {total_orig}")
    print(f"Same: {total_same}")
