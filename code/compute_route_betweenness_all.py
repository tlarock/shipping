import pickle
import networkx as nx
import numpy as np
from route_betweenness import route_node_betweenness_from_file, route_edge_betweenness_from_file

scratch_base = '/scratch/larock.t/shipping/'
#filename = scratch_base + 'results/interpolated_paths/iterative_paths_with_routes.txt'
filename = scratch_base + 'results/interpolated_paths/iterative_paths_with_routes_filtered_dt-{}_rt-1.0.txt'
#alpha = 'all'
alpha  = 2.0
filename = filename.format(alpha)
## Read node betweenness
with open(scratch_base + 'results/interpolated_paths/route_node_betweenness_all.pickle', 'rb') as fpickle:
    rb = pickle.load(fpickle)
print("Read node betweenness.", flush=True)
## Compute route betweenness
route_betweenness = route_node_betweenness_from_file(filename)
print("Computed route betweenness.", flush=True)
for node, btw in route_betweenness.items():
    rb.setdefault(node, dict())
    rb[node][alpha] = btw
with open(scratch_base + 'results/interpolated_paths/route_node_betweenness_all.pickle', 'wb') as fpickle:
    pickle.dump(rb, fpickle)
print("Dumped results.", flush=True)

## Read edge betweenness
with open(scratch_base + 'results/interpolated_paths/route_edge_betweenness_all.pickle', 'rb') as fpickle:
    rb = pickle.load(fpickle)
print("Read edge betweenness", flush=True)
route_betweenness = route_edge_betweenness_from_file(filename)
print("Computed route betweenness.", flush=True)
for edge, btw in route_betweenness.items():
    rb.setdefault(edge, dict())
    rb[edge][alpha] = btw
with open(scratch_base + 'results/interpolated_paths/route_edge_betweenness_all.pickle', 'wb') as fpickle:
    pickle.dump(rb, fpickle)
print("Dumped results.", flush=True)
