import pytest
import networkx as nx
import numpy as np
import sys
sys.path.append('../code/')
from bohmova import gamma_transform, compute_d_GL_L
from tutils import *

def test_gamma_transform():
    G =  generate_gnp_graph(set(range(25)), p=0.1)
    routes = generate_routes(G, max_num=10, max_len=10, cycles=False)
    G, routes_by_node = set_route_attributes(G, routes)
    G_gamma = gamma_transform(G, routes, routes_by_node)
    ## Check number of nodes
    num_nodes = len(G.nodes()) + len(set([(node, str(r)) for r, route in enumerate(routes, start=1) for node in route ]))
    assert num_nodes == len(G_gamma.nodes())

    ## Check total edge weight
    expected_edge_weight = sum([1 for node in G_gamma.nodes() if (isinstance(node, tuple) and isinstance(node[1], str))])
    edge_weight = G_gamma.size(weight='weight')
    assert expected_edge_weight == edge_weight

def test_compute_dgll():
    np.random.seed(0)
    G =  generate_gnp_graph(set(range(25)), p=0.1)
    print(G.edges())
    routes = generate_routes(G, max_num=10, max_len=10, cycles=False)
    G, routes_by_node = set_route_attributes(G, routes)
    d_GL_L = compute_d_GL_L(G, routes, routes_by_node)
    ## Find the minimum distance over all lines for each pair
    min_by_pair = dict()
    for (v, t, l), d_gl_l in d_GL_L.items():
        if (v,t) not in min_by_pair:
            min_by_pair[(v,t)] = d_gl_l
        elif d_gl_l < min_by_pair[(v,t)]:
            min_by_pair[(v,t)] = d_gl_l

    ## Should be the same as the minimum-route distance
    ## computed in the clique graph
    G_indirect = indirect_graph(routes)
    print(G_indirect.edges())
    print(set(G_indirect.edges())-set(G.edges()))
    ## NOTE: This doesn't make sense. Why does it not work with (v,t)???
    for (t, v),d in min_by_pair.items():
        try:
            sp = nx.shortest_path_length(G_indirect, v, t)
        except nx.exception.NetworkXNoPath:
            sp = float('inf')

        assert sp == d
