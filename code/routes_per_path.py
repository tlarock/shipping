import pickle
## Plot path length against number of routes
scratch_base = '/scratch/larock.t/shipping/results/interpolated_paths/'
#scratch_base = '../results/interpolated_paths/'
with open(scratch_base + 'iterative_paths.txt', 'r') as fin:
    num_routes = dict()
    pair = (-1,-1)
    prev_pair = None
    pair_counter = 0
    total_pairs = 0
    for line in fin:
        path, mr_dist, route_dist, *routes = line.strip().split('|')
        path = path.split(',')
        num_routes.setdefault(len(path)-1, list())
        num_routes[len(path)-1].append(len(routes))
        pair = path[0], path[-1]
        if pair != prev_pair:
            pair_counter += 1
            total_pairs += 1
            if pair_counter == 50_000:
                print(total_pairs, flush=True)
                pair_counter = 0
        prev_pair = pair

with open(scratch_base + 'routes_per_path.pickle', 'wb') as fpickle:
    pickle.dump(num_routes, fpickle)
