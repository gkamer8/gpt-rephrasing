import os
import json
from math import comb

results_folder = "results"

files = os.listdir(results_folder)

agg_cum = 0
orig_cum = 0
same_cum = 0

# dict of (agg, same, orig)
res_dict = {}

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

        if key in res_dict:
            i = ['agg', 'same', 'orig'].index(res[key])
            res_dict[key][i] += 1
        else:
            res_dict[key] = [res[key]=='agg', res[key]=='same', res[key]=='orig']
    print(f"Agg:  {total_agg}")
    print(f"Orig: {total_orig}")
    print(f"Same: {total_same}")

    agg_cum += total_agg
    orig_cum += total_orig
    same_cum += total_same
print()
total = agg_cum + orig_cum + same_cum
print(f"Agg: {agg_cum/total}")
print(f"Orig: {orig_cum/total}")
print(f"Same: {same_cum/total}")
print(f"H2H: {agg_cum/(agg_cum+orig_cum)}")

# Statistical test

n = agg_cum + orig_cum
print(f"n: {n}")
print(f"agg: {agg_cum}")
# PMF: (n choose k) .5^(n)
p = 0
for k in range(agg_cum, n+1):
    p += comb(n, k) * .5**n
print(f"p-value: {p}")

for key in res_dict:
    print(f"({res_dict[key][0]}, {res_dict[key][1]}, {res_dict[key][2]}): {key}")