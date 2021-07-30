import pickle
import networkx as nx
import numpy as np
from route_betweenness import route_node_betweenness_from_file, route_edge_betweenness_from_file

filename = '../results/interpolated_paths/iterative_paths_with_routes.txt'
alpha = 'all'
## Read node betweenness
with open('../results/interpolated_paths/route_node_betweenness_fromfile.pickle', 'rb') as fpickle:
    rb = pickle.load(fpickle)
print("Read node betweenness.")
## Compute route betweenness
route_betweenness = route_node_betweenness_from_file(filename)
print("Computed route betweenness.")
for node, btw in route_betweenness.items():
    rb.setdefault(node, dict())
    rb[node][alpha] = btw
with open('../results/interpolated_paths/route_node_betweenness_all.pickle', 'wb') as fpickle:
    pickle.dump(rb, fpickle)
print("Dumped results.")

## Read edge betweenness
with open('../results/interpolated_paths/route_edge_betweenness_fromfile.pickle', 'rb') as fpickle:
    rb = pickle.load(fpickle)
print("Read edge betweenness")
route_betweenness = route_edge_betweenness_from_file(filename)
print("Computed route betweenness.")
for edge, btw in route_betweenness.items():
    rb.setdefault(edge, dict())
    rb[edge][alpha] = btw
with open('../results/interpolated_paths/route_edge_betweenness_all.pickle', 'wb') as fpickle:
    pickle.dump(rb, fpickle)
print("Dumped results.")
