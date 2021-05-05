import networkx as nx
import numpy as np
from modified_dijkstra import *
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

test = False
if test:
    routes = [
        ['a','b','c','d'],
        ['b','c','e','a','b'],
        ['d','a','b','c','f','b'],
        ['b','c','g'],
        ['g','h'],
        ['a','e','c', 'f']
    ]
    G = nx.DiGraph()
    for route_id, route in enumerate(routes, start=1):
        for i in range(1, len(route)):
            if not G.has_edge(route[i-1], route[i]):
                G.add_edge(route[i-1], route[i], routes=set([route_id]))
            else:
                G[route[i-1]][route[i]]['routes'].add(route_id)
else:
    routes =[]
    G = nx.DiGraph()
    with open('../data/all_routes_2015.ngram', 'r') as fin:
        for route_id, line in enumerate(fin):
            path = remove_selfloops(line.strip().split(','))
            routes.append(path)
            for i in range(1, len(path)):
                if not G.has_edge(path[i-1], path[i]):
                    G.add_edge(path[i-1], path[i], routes=set([route_id]))
                else:
                    G[path[i-1]][path[i]]['routes'].add(route_id)

shortest_paths = all_shortest_paths(G)

import pickle
with open('mrnrp.pickle', 'wb') as fpickle:
    pickle.dump(shortest_paths, fpickle)
