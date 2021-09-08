import pytest
import networkx as nx
import numpy as np
import sys
sys.path.append('../code/')
from iterative_minroutes import all_shortest_paths
from tutils import *


def test_distance_correctness():
    G = generate_gnp_graph(set(range(100)), p=0.01)
    routes = generate_routes(G, max_num=30, max_len=20)
    ## Routes by node and G
    G, routes_by_node = set_route_attributes(G, routes)
    G_indirect = indirect_graph(routes)
    shortest_paths = all_shortest_paths(G, routes)
    graph_distances = dict(nx.shortest_path_length(G_indirect))
    for mr_dist in shortest_paths:
        for s in shortest_paths[mr_dist]:
            for t in shortest_paths[mr_dist][s]:
                assert mr_dist == graph_distances[s][t]
