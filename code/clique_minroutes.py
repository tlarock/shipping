import networkx as nx
import pandas as pd
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

with open('../results/interpolated_paths/shortest_paths_clique.pickle', 'rb') as fpickle:
    paper_paths_dict = pickle.load(fpickle)

gwdata = pd.read_csv('../data/original/Nodes_2015_country_degree_bc_B_Z_P.csv', encoding='latin-1' ) ## Just need to get id to name mapping
port_mapping = dict(zip(gwdata.id.values,gwdata.port.values))

G = nx.DiGraph()
routes = []
## Keep track of a "directed clique-graph edgelist"
## I will use this to determine whether direct connections
## in the clique graph are actually viable directed routes
directed_clique_edges = set()
with open('../data/all_routes_2015.ngram', 'r') as fin:
    for route_id, line in enumerate(fin, start=1):
        path = remove_selfloops(line.strip().split(','))
        routes.append(path)
        for i in range(1, len(path)):
            if not G.has_edge(path[i-1], path[i]):
                G.add_edge(path[i-1], path[i], routes=set([route_id]))
            else:
                G[path[i-1]][path[i]]['routes'].add(route_id)

            if path[0] != path[-1]:
                for j in range(i, len(path)):
                    directed_clique_edges.add((path[i-1], path[j]))
            else:
                for j in range(len(path)):
                    if path[i-1] != path[j]:
                        directed_clique_edges.add((path[i-1], path[j]))

route_lengths_per_pair = []
route_lengths_dist = []
curr_count = 0
total_count = 0
N = len(G.nodes())
total_node_pairs = len(paper_paths_dict)
minimum_routes_sp = defaultdict(dict)
for pair in paper_paths_dict:
    mpair = (port_mapping[pair[0]], port_mapping[pair[1]])
    route_lengths = []
    for path in paper_paths_dict[pair]:
        mpath = [port_mapping[path[i]] for i in range(len(path))]
        ## If the nodes have a direct connection in the clique
        ## graph, they are part of the same route and so we say
        if len(mpath) == 2 and tuple(mpath) in directed_clique_edges:
            tpath = tuple(mpath)
            minimum_routes_sp[mpair][tpath] = 1

        ## Ignore shortest paths through the clique graph 
        ## that are not at all possible in the path based graph
        if not all([(mpath[i-1], mpath[i]) in G.edges() for i in range(1, len(mpath))]):
            route_lengths += [0]
            continue

        ## Check if the path is minimum-route by checking whether it appears
        ## in the unfiltered minimum-route paths
        tpath = tuple(mpath)
        if tpath in minroute_paths[mpair]:
            route_lengths.append(minroute_paths[mpair][tpath])
            minimum_routes_sp[mpair][tpath] = minroute_paths[mpair][tpath]

    route_lengths_dist += route_lengths
    route_lengths_per_pair.append(len(set(route_lengths)))

    curr_count+=1
    total_count+=1
    if curr_count == 50_000:
        print(f'{total_node_pairs-total_count} remaining.')
        curr_count = 0

with open('/scratch/larock.t/shipping/results/interpolated_paths/clique_minroute_paths.pickle', 'wb') as fpickle:
    pickle.dump(minimum_routes_sp, fpickle)
