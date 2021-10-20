import pickle
import numpy as np
from scipy.stats import entropy
from create_edgelist import read_network
from collections import Counter

G, mapping = read_network(network_type='directed')

scratch_base = '/scratch/larock.t/shipping/results/interpolated_paths/'
#scratch_base = '../results/interpolated_paths/'
data = dict()
with open(scratch_base + 'iterative_paths.txt', 'r') as fin:
    pair = (-1,-1)
    first = True
    prev_pair = None
    pair_counter = 0
    total_pairs = 0
    degs = []
    all_routes = []
    for line in fin:
        path, mr_dist, route_dist, *routes = line.strip().split('|')
        path = path.split(',')
        pair = path[0], path[-1]

        print(path, routes)
        if pair != prev_pair and not first:
            deg_counts = [d for _,d in sorted(dict(Counter(degs)).items())]
            deg_ent = entropy(deg_counts)
            rt_counts = [d for _,d in sorted(dict(Counter(all_routes)).items())]
            rt_ent = entropy(rt_counts)
            data[prev_pair] = {'deg_ent':deg_ent, 'deg_ent_normed':deg_ent / np.log(len(deg_counts)),  \
                               'route_ent': rt_ent, 'route_ent_normed': rt_ent / np.log(len(rt_counts))}
            print(f'deg_ent:  {data[prev_pair]["deg_ent"]} normed: {data[prev_pair]["deg_ent_normed"]} seq: {deg_counts}')
            print(f'route_ent:  {data[prev_pair]["route_ent"]} {data[prev_pair]["route_ent_normed"]} seq: {rt_counts}')
            import sys
            sys.exit()
            degs = []
            all_routes = []
            pair_counter += 1
            total_pairs += 1
            if pair_counter == 50_000:
                print(total_pairs, flush=True)
                pair_counter = 0
        degs += [G.degree(mapping[node]) for node in path]
        all_routes += [r for rt in routes for r in rt]
        prev_pair = pair
        if first: first = False

with open(scratch_base + 'deg_route_entropy.pickle', 'wb') as fpickle:
    pickle.dump(data, fpickle)
