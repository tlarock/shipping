import networkx as nx
import pickle
from collections import defaultdict

def remove_selfloops(path):
    i = 1
    end = len(path)
    while i < end:
        if path[i-1] == path[i]:
            del path[i-1]
            end-=1
        else:
            i+=1
    return path


print("Reading minimum route paths.", flush=True)
with open('/scratch/larock.t/shipping/results/interpolated_paths/iterative_paths_with_routes.txt', 'r') as fin:
	minroute_paths = dict()
	for line in fin:
		path, mr_dist, rt_dist, *_ = line.strip().split('|')
		path = path.strip().split(',')
		dist = int(mr_dist)
		minroute_paths.setdefault((path[0], path[-1]), dict())
		minroute_paths[(path[0], path[-1])][tuple(path)] = dist

print("Reading path graph paths.", flush=True)
with open('../results/interpolated_paths/shortest_paths_pathrep.pickle', 'rb') as fpickle:
    pg_paths = pickle.load(fpickle)

print("Starting computation.", flush=True)
route_lengths_per_pair = []
route_lengths_dist = []
curr_count = 0
total_count = 0
total_node_pairs = len(pg_paths)
minimum_routes = defaultdict(dict)
for pair in pg_paths:
    route_lengths = []
    for path in pg_paths[pair]:
        ## Check if the path is minimum-route by checking whether it appears
        ## in the unfiltered minimum-route paths
        tpath = tuple(path)
        if tpath in minroute_paths[pair]:
            route_lengths.append(minroute_paths[pair][tpath])
            minimum_routes[pair][tpath] = minroute_paths[pair][tpath]

    route_lengths_dist += route_lengths
    route_lengths_per_pair.append(len(set(route_lengths)))

    curr_count+=1
    total_count+=1
    if curr_count == 50_000:
        print(f'{total_node_pairs-total_count} remaining.')
        curr_count = 0

with open('/scratch/larock.t/shipping/results/interpolated_paths/sp_pathrep_minroutes.pickle', 'wb') as fpickle:
    pickle.dump(minimum_routes, fpickle)
