import pickle
import networkx as nx
import numpy as np
from route_betweenness import route_node_betweenness_from_file, route_edge_betweenness_from_file

scratch_base = '/scratch/larock.t/shipping/'
filename = scratch_base + 'results/interpolated_paths/iterative_paths_with_routes_filtered_dt-{}_rt-1.0_updated.txt'
alphas = [1.0, 1.05, 1.15, 1.25, 1.5, 1.75, 2.0]
rnb = dict()
reb = dict()
for alpha in alphas:
    filename = filename.format(alpha)
    ## Compute route betweenness
    route_betweenness = route_node_betweenness_from_file(filename)
    print(f"Computed route node betweenness for alpha={alpha}.", flush=True)
    for node, btw in route_betweenness.items():
        rnb.setdefault(node, dict())
        rnb[node][alpha] = btw
    with open(scratch_base + 'results/interpolated_paths/route_node_betweenness_all.pickle', 'wb') as fpickle:
        pickle.dump(rnb, fpickle)
    print("Dumped results.", flush=True)

    ## Read edge betweenness
    route_betweenness = route_edge_betweenness_from_file(filename)
    print(f"Computed route edge betweenness for alpha={alpha}.", flush=True)
    for edge, btw in route_betweenness.items():
        reb.setdefault(edge, dict())
        reb[edge][alpha] = btw
    with open(scratch_base + 'results/interpolated_paths/route_edge_betweenness_all.pickle', 'wb') as fpickle:
        pickle.dump(reb, fpickle)
    print("Dumped results.", flush=True)


filename = scratch_base + 'results/interpolated_paths/iterative_paths_with_routes.txt'
## Compute route betweenness
route_betweenness = route_node_betweenness_from_file(filename)
print("Computed route node betweenness for all paths.", flush=True)
for node, btw in route_betweenness.items():
    rnb.setdefault(node, dict())
    rnb[node][alpha] = btw
with open(scratch_base + 'results/interpolated_paths/route_node_betweenness_all.pickle', 'wb') as fpickle:
    pickle.dump(rnb, fpickle)
print("Dumped results.", flush=True)

## Read edge betweenness
route_betweenness = route_edge_betweenness_from_file(filename)
print("Computed route edge betweenness for all paths.", flush=True)
for edge, btw in route_betweenness.items():
    reb.setdefault(edge, dict())
    reb[edge][alpha] = btw
with open(scratch_base + 'results/interpolated_paths/route_edge_betweenness_all.pickle', 'wb') as fpickle:
    pickle.dump(reb, fpickle)
print("Dumped results.", flush=True)


