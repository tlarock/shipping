import pickle
import numpy as np
import pandas as pd
from collections import Counter


def get_xy(dist, normed=False):
    counter = Counter(dist)
    x=[];y=[]
    for xval in sorted(counter.keys()):
        x.append(xval)
        y.append(counter[xval])
    y = np.array(y)
    if normed:
        y = y/y.sum()
    return x, y

print("Reading shipping distances.", flush=True)
shipping_dist = dict()
with open('/home/larock.t/git/shipping/data/port_shipping_distances.csv', 'r') as fin:
    for line in fin:
        u,v,dist = line.strip().split(',')
        shipping_dist[(u,v)] = float(dist)

print("Computing filtered path stats.", flush=True)
scratch_base = '/scratch/larock.t/shipping/results/interpolated_paths/'
## Filtered paths
filtered_stats = {
    'num_paths':[],
    'route_lengths':[],
    'path_lengths':[],
    'distances':[],
    'routes_per_path':[]
}
filtered_paths = dict()
import sys
argv = sys.argv
if len(argv) > 1:
    rt_thresh = float(sys.argv[1])
    dt_thresh = float(sys.argv[2])
else:
    rt_thresh = 1.0
    dt_thresh = 1.5

with open(scratch_base + f'iterative_paths_filtered_dt-{dt_thresh}_rt-{rt_thresh}.txt', 'r') as fin:
    pair_counter = 0
    total_pairs = 0
    prev_pair = (-1,-1)
    first = True
    for line in fin:
        path, mr_dist, route_dist, *routes = line.strip().split('|')
        path = path.strip().split(',')
        dist = int(mr_dist)
        pair = (path[0], path[-1])
        filtered_paths.setdefault(pair, dict())
        filtered_paths[pair][tuple(path)] = dist
        filtered_stats['distances'].append(float(route_dist))
        filtered_stats['routes_per_path'].append(len(routes))
        if pair != prev_pair and not first:
            num_paths = len(filtered_paths[prev_pair])
            filtered_stats['num_paths'].append(num_paths)
            ## Compute over _all_ paths (same for all 4 path datasets)
            route_lengths = [p for p in filtered_paths[prev_pair].values()]
            filtered_stats['route_lengths'] += route_lengths
            path_lengths = [len(p)-1 for p in filtered_paths[prev_pair].keys()]
            filtered_stats['path_lengths'] += path_lengths
            pair_counter += 1
            total_pairs += 1
            if pair_counter == 50_000:
                print(f"{total_pairs} pairs processed.", flush=True)
                pair_counter = 0

        prev_pair = pair

        if first: first = False

## Do the last pair!
num_paths = len(filtered_paths[prev_pair])
filtered_stats['num_paths'].append(num_paths)
route_lengths = list(filtered_paths[prev_pair].values())
filtered_stats['route_lengths'] += route_lengths
path_lengths = [len(p)-1 for p in filtered_paths[prev_pair].keys()]
filtered_stats['path_lengths'] += path_lengths

import pickle
with open(scratch_base + f'iterative_paths_filtered_dt-{dt_thresh}_rt-{rt_thresh}_stats.pickle', 'wb') as fpickle:
    pickle.dump(filtered_stats, fpickle)

print("Computing clique path stats.", flush=True)
## Clique paths
clique_stats = {
    'num_paths':[],
    'route_lengths':[],
    'path_lengths':[],
    'distances':[]
}
with open(scratch_base + 'shortest_paths_clique.pickle', 'rb') as fpickle:
    paper_paths_dict = pickle.load(fpickle)
gwdata = pd.read_csv('../data/original/Nodes_2015_country_degree_bc_B_Z_P.csv', encoding='latin-1' ) ## Just need to get id to name mapping
port_mapping = dict(zip(gwdata.id.values,gwdata.port.values))
with open(scratch_base + 'clique_minroute_paths.pickle', 'rb') as fpickle:
    minimum_routes_sp = pickle.load(fpickle)
for pair in paper_paths_dict:
    num_paths = len(paper_paths_dict[pair])
    #num_paths_dist_cg.append(num_paths)
    clique_stats['num_paths'].append(num_paths)
    mpair = (port_mapping[pair[0]], port_mapping[pair[1]])
    if mpair in minimum_routes_sp:
        route_lengths = [p for p in minimum_routes_sp[mpair].values()]
        clique_stats['route_lengths'] += route_lengths
    path_lengths = [len(next(iter(paper_paths_dict[pair])))-1]*len(paper_paths_dict[pair])
    clique_stats['path_lengths'] += path_lengths

for pair in minimum_routes_sp:
    for path in minimum_routes_sp[pair]:
        #if path not in filtered_paths[pair]:
        #    continue
        ## Real distance
        d = 0.0
        for i in range(1, len(path)):
            d += shipping_dist[path[i-1], path[i]]
        clique_stats['distances'].append(d)


## coroute graph paths
print("Computing coroute path stats.", flush=True)
coroute_stats = {
    'num_paths':[],
    'route_lengths':[],
    'path_lengths':[],
    'distances':[]
}

with open(scratch_base + 'shortest_paths_coroute.pickle', 'rb') as fpickle:
    coroute_paths = pickle.load(fpickle)
with open(scratch_base + 'coroute_minroute_paths.pickle', 'rb') as fpickle:
    minimum_routes = pickle.load(fpickle)

for pair in coroute_paths:
    num_paths = len(coroute_paths[pair])
    coroute_stats['num_paths'].append(num_paths)
    if pair in minimum_routes:
        route_lengths = [p for p in minimum_routes[pair].values()]
        coroute_stats['route_lengths'] += route_lengths
    coroute_lengths = [len(next(iter(coroute_paths[pair])))-1]*len(coroute_paths[pair])
    coroute_stats['path_lengths'] += coroute_lengths

for pair in minimum_routes:
    for path in minimum_routes[pair]:
        #if path not in filtered_paths[pair]:
        #    continue
        ## Real distance
        d = 0.0
        for i in range(1, len(path)):
            d += shipping_dist[path[i-1], path[i]]
        coroute_stats['distances'].append(d)

## Path graph paths
print("Computing path path stats.", flush=True)
path_stats = {
    'num_paths':[],
    'route_lengths':[],
    'path_lengths':[],
    'distances':[]
}

with open(scratch_base + 'shortest_paths_pathrep.pickle', 'rb') as fpickle:
    pg_paths = pickle.load(fpickle)
with open(scratch_base + 'sp_pathrep_minroutes.pickle', 'rb') as fpickle:
    minimum_routes = pickle.load(fpickle)

for pair in pg_paths:
    num_paths = len(pg_paths[pair])
    path_stats['num_paths'].append(num_paths)
    route_lengths = [p for p in minimum_routes[pair].values()]
    path_stats['route_lengths'] += route_lengths
    path_lengths = [len(next(iter(pg_paths[pair])))-1]*len(pg_paths[pair])
    path_stats['path_lengths'] += path_lengths

for pair in pg_paths:
    for path in pg_paths[pair]:
        ## Real distance
        d = 0.0
        for i in range(1, len(path)):
            d += shipping_dist[path[i-1], path[i]]
        path_stats['distances'].append(d)


print("Dumping stats.", flush=True)
with open(scratch_base + f'path_comparison_stats_dt-{dt_thresh}_rt-{rt_thresh}.pickle', 'wb') as fpickle:
    pickle.dump((filtered_stats, clique_stats, coroute_stats, path_stats), fpickle)
