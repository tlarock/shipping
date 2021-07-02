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


with open('/scratch/larock.t/shipping/results/interpolated_paths/iterative_paths_with_routes_filtered_dt-1.5_rt-1.0.txt', 'r') as fin:
	minroute_paths = dict()
	for line in fin:
		path, mr_dist, rt_dist, *_ = line.strip().split('|')
		path = path.strip().split(',')
		dist = int(mr_dist)
		minroute_paths.setdefault((path[0], path[-1]), dict())
		minroute_paths[(path[0], path[-1])][tuple(path)] = dist

with open('../results/interpolated_paths/shortest_paths_pathrep.pickle', 'rb') as fpickle:
    pg_paths = pickle.load(fpickle)

G = nx.DiGraph()
routes = []
## Keep track of a "directed clique-graph edgelist"
## I will use this to determine whether direct connections
## in the clique graph are actually viable directed routes
with open('../data/all_routes_2015.ngram', 'r') as fin:
    for route_id, line in enumerate(fin, start=1):
        path = remove_selfloops(line.strip().split(','))
        routes.append(path)
        for i in range(1, len(path)):
            if not G.has_edge(path[i-1], path[i]):
                G.add_edge(path[i-1], path[i], routes=set([route_id]))
            else:
                G[path[i-1]][path[i]]['routes'].add(route_id)

route_lengths_per_pair = []
route_lengths_dist = []
curr_count = 0
total_count = 0
N = len(G.nodes())
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
