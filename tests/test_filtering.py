import pytest
import networkx as nx
import numpy as np
import sys
sys.path.append('../code/')
from iterative_minroutes import all_shortest_paths, compute_route_dist
from filter_paths import filter_distance
from tutils import *


def test_distance_filtering():
    G = generate_gnp_graph(set(range(100)), p=0.01)
    routes = generate_routes(G, max_num=30, max_len=20)
    ## Routes by node and G
    G, routes_by_node = set_route_attributes(G, routes)
    G_indirect = indirect_graph(routes)
    shortest_paths = all_shortest_paths(G, routes)

    ## Set distances for each pair of nodes
    shipping_dist = dict()
    for u in G.nodes():
        for v in G.nodes():
            if u != v:
                shipping_dist[(u,v)] = np.random.uniform(100, 2000, 1)[0]

    ## Compute total distances for all paths between the
    ## pair of nodes with the largest number of paths
    max_val = 0
    max_pair = None
    max_mr_dist = 0
    for mr_dist in shortest_paths:
        for s in shortest_paths[mr_dist]:
            for t in shortest_paths[mr_dist][s]:
                if len(shortest_paths[mr_dist][s][t]) > max_val:
                    max_val = len(shortest_paths[mr_dist][s][t])
                    max_pair = (s,t)
                    max_mr_dist = mr_dist

    s, t = max_pair
    total_distances = {path:compute_route_dist(path, shipping_dist) for path in shortest_paths[max_mr_dist][s][t]}

    ## Pick number of paths to be filtered
    num_paths = len(total_distances)
    num_filtered = int(np.random.randint(1, num_paths-1, 1)[0])

    ## Set threshold such that those paths should be filtered
    sorted_paths = sorted(total_distances.items(), key  = lambda kv: kv[1], reverse=True)
    path_to_filter = sorted_paths[num_filtered][0]
    distance_to_filter = sorted_paths[num_filtered][1]
    minimum_distance = min(total_distances.values())
    distance_threshold = distance_to_filter / minimum_distance

    ## Run filtering
    filtered_paths = filter_distance(total_distances, set(), set(total_distances.keys()), distance_threshold)

    ## Assert that paths were filtered
    assert len(set(total_distances.keys())-filtered_paths) == len(total_distances.keys())-num_filtered
