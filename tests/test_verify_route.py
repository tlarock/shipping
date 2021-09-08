import pytest
import networkx as nx
import numpy as np
import sys
sys.path.append('../code/')
from parallel_dijkstra import verify_route
from tutils import *

def test_verify_route():
    for i in range(10):
        ## Generate a gnp graph
        G = generate_gnp_graph(set(range(np.random.randint(10, 100))), 0.2)
        routes = generate_routes(G, max_num=50, max_len=10)

        edge_indices = dict()
        for route_id, route in enumerate(routes, start=1):
            edge_indices[route_id] = dict()
            for i in range(1, len(route)):
                edge = (route[i-1], route[i])
                edge_indices[route_id].setdefault(edge, set())
                edge_indices[route_id][edge].add(i-1)

        ## Good Routes
        good_routes = [route for route in routes]
        good_route_ids = [[route_id]*(len(route)-1) for route_id, route in enumerate(routes, start=1)]
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i != j:
                    path_followed, path, path_routes = combine_routes(routes, i, j)
                    if path_followed:
                        good_routes.append(path)
                        good_route_ids.append(path_routes)
        for route_id, route in enumerate(good_routes, start=1):
            assert verify_route(route, good_route_ids[route_id-1], routes, edge_indices)

        ## Bad Routes
        routes = [['a','b','a','T','c','S','c','a']]
        edge_indices = {1:{(routes[0][i-1],routes[0][i]):{i} for i in range(1, len(routes[0]))}}
        path = ['S','c','a','T']
        path_routes = [1, 1, 1]
        assert not verify_route(path, path_routes, routes, edge_indices)
        path = ['T','c','a']
        path_routes = [1, 1]
        assert not verify_route(path, path_routes, routes, edge_indices)
        path = ['S','c','S']
        path_routes = [1, 1]
        assert not verify_route(path, path_routes, routes, edge_indices)
        path = ['S','c','a','b','a','T']
        path_routes = [1, 1, 1,1,1]
        assert verify_route(path, path_routes, routes, edge_indices)
