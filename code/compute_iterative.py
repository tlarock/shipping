import networkx as nx
import numpy as np
import sys
sys.path.append('../code/')
from iterative_minroutes import *


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

def has_selfloop(path):
    for i in range(1, len(path)):
        if path[i-1] == path[i]:
            return True
    return False

G = nx.DiGraph()
routes = []
with open('../data/all_routes_2015.ngram', 'r') as fin:
    for route_id, line in enumerate(fin, start=1):
        path = remove_selfloops(line.strip().split(','))
        routes.append(path)
        for i in range(1, len(path)):
            if not G.has_edge(path[i-1], path[i]):
                G.add_edge(path[i-1], path[i], routes=set([route_id]))
            else:
                G[path[i-1]][path[i]]['routes'].add(route_id)

shortest_paths, shortest_path_routes = all_shortest_paths(G, routes, num_cpus=1, print_st=True, log_every=1000)

import pickle
with open('../results/interpolated_paths/iterative_paths.pickle', 'wb') as fpickle:
    pickle.dump(shortest_paths, fpickle)
