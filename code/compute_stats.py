## Number of paths per pair
## Number of minimum lengths (should be 1)
num_paths_dist_mrr = [] ## list of ints
route_lengths_per_pair_mrr = [] ## list of ints (should be all 1s)
route_lengths_dist_mrr = [] ## list of ints
path_lengths_dist_mrr = []
routes_per_path_dist = []
distances_per_path = []
with open('/scratch/larock.t/shipping/results/interpolated_paths/iterative_paths_with_routes.txt', 'r') as fin:
    pair_counter = 0
    total_pairs = 0
    prev_pair = (-1,-1)
    paths = dict()
    first = True
    for line in fin:
        path, mr_dist, route_dist, *routes = line.strip().split('|')
        distances_per_path.append(float(route_dist)) 
        routes_per_path_dist.append(len(routes))
        path = path.strip().split(',')
        dist = int(mr_dist)
        pair = (path[0], path[-1])
        paths.setdefault(pair, dict())
        paths[pair][tuple(path[0:len(path)-1])] = dist
        if pair != prev_pair and not first:
            num_paths = len(paths[prev_pair])
            num_paths_dist_mrr.append(num_paths)
            #route_lengths = [next(iter(filtered_paths[prev_pair].values()))]
            ## Compute over _all_ paths (same for all 4 path datasets)
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

## Do the last pair!
num_paths = len(paths[prev_pair])
num_paths_dist_mrr.append(num_paths)
#route_lengths = [next(iter(filtered_paths[prev_pair].values()))]
route_lengths = [p for p in paths[prev_pair].values()]
route_lengths_dist_mrr += route_lengths
route_lengths_per_pair_mrr.append(len(set(route_lengths)))
path_lengths = [len(p)-1 for p in paths[prev_pair].keys()]
path_lengths_dist_mrr +=  path_lengths 

import pickle
print("Pickling distributions.", flush=True)
with open('/scratch/larock.t/shipping/results/interpolated_paths/iterative_paths_with_routes_stats.pickle', 'wb') as fpickle:
    pickle.dump((num_paths_dist_mrr, route_lengths_dist_mrr, route_lengths_per_pair_mrr, path_lengths_dist_mrr, routes_per_path_dist, distances_per_path), fpickle)
