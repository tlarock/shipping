import multiprocessing
import pickle
import networkx as nx
import numpy as np
from route_betweenness import route_node_betweenness_from_file, route_edge_betweenness_from_file

def get_rb(filename, betw_type, alpha):
    if betw_type == 'node':
        return (alpha, betw_type, route_node_betweenness_from_file(filename))
    elif betw_type == 'edge':
        return (alpha, betw_type, route_edge_betweenness_from_file(filename))

with multiprocessing.Pool(14) as pool:
    scratch_base = '/scratch/larock.t/shipping/'
    filename = scratch_base + 'results/interpolated_paths/iterative_paths_filtered_dt-{}_rt-1.0.txt'
    alphas = [1.0, 1.05, 1.15, 1.25, 1.5, 1.75, 2.0]

    args = [(filename.format(alpha), betw_type, alpha) for alpha in alphas for betw_type in ['node', 'edge']]
    print(f'args: {args}', flush=True)
    results = pool.starmap(get_rb, args)
    rnb = dict()
    reb = dict()
    for alpha, betw_type, result in results:
        if betw_type == 'node':
            for node, btw in result.items():
                rnb.setdefault(node, dict())
                rnb[node][alpha] = btw
        if betw_type == 'edge':
            for edge, btw in result.items():
                reb.setdefault(edge, dict())
                reb[edge][alpha] = btw

with open(scratch_base + 'results/interpolated_paths/route_node_betweenness_all.pickle', 'wb') as fpickle:
    pickle.dump(rnb, fpickle)
with open(scratch_base + 'results/interpolated_paths/route_edge_betweenness_all.pickle', 'wb') as fpickle:
    pickle.dump(reb, fpickle)

print("Dumped results, starting full data computation.", flush=True)

filename = scratch_base + 'results/interpolated_paths/iterative_paths.txt'
print("Starting edge betweenness.", flush=True)
_, _, edge_betw = get_rb(filename, 'edge', 'all')
print("Edge betweenness done.", flush=True)
for edge, btw in edge_betw.items():
    reb.setdefault(edge, dict())
    reb[edge][alpha] = btw

with open(scratch_base + 'results/interpolated_paths/route_edge_betweenness_all.pickle', 'wb') as fpickle:
    pickle.dump(reb, fpickle)
print("Dumped edge betweenness results.", flush=True)

print("Starting node betweenness.", flush=True)
_, _, node_betw = get_rb(filename, 'node', 'all')
print("Node betweenness done.", flush=True)
for node, btw in node_betw.items():
    rnb.setdefault(node, dict())
    rnb[node][alpha] = btw

with open(scratch_base + 'results/interpolated_paths/route_node_betweenness_all.pickle', 'wb') as fpickle:
    pickle.dump(rnb, fpickle)
print("Dumped node results.", flush=True)

