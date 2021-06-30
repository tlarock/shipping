## Number of paths per pair
## Number of minimum lengths (should be 1)
num_paths_dist_mrr = [] ## list of ints
route_lengths_per_pair_mrr = [] ## list of ints (should be all 1s)
route_lengths_dist_mrr = [] ## list of ints
path_lengths_dist_mrr = []
with open('iterative_paths.txt', 'r') as fin:
    pair_counter = 0
    total_pairs = 0
    prev_pair = (-1,-1)
    paths = dict()
    first = True
    for line in fin:
        a = line.strip().split(',')
        dist = int(a[-1])
        pair = (a[0], a[-2])
        paths.setdefault(pair, dict())
        paths[pair][tuple(a[0:len(a)-1])] = dist
        if pair != prev_pair and not first:
            num_paths = len(paths[prev_pair])
            num_paths_dist_mrr.append(num_paths)
            route_lengths = [p for p in paths[prev_pair].values()]
            route_lengths_dist_mrr += route_lengths
            route_lengths_per_pair_mrr.append(len(set(route_lengths)))
            path_lengths = [len(p)-1 for p in paths[prev_pair].keys()]
            path_lengths_dist_mrr +=  path_lengths 
            del paths[prev_pair]

            pair_counter += 1
            total_pairs += 1
            if pair_counter == 50_000:
                print(f"{total_pairs} pairs processed.", flush=True)
                pair_counter = 0

        prev_pair = pair
        
        if first: first = False

import pickle
print("Pickling distributions.", flush=True)
with open('iterative_paths_stats.pickle', 'wb') as fpickle:
    pickle.dump((num_paths_dist_mrr, route_lengths_dist_mrr, route_lengths_per_pair_mrr, path_lengths_dist_mrr), fpickle)
