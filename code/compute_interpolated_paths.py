import networkx as nx
import numpy as np
from parallel_dijkstra import *
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

if __name__ == '__main__':
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
            for route_id, line in enumerate(fin, start=1):
                path = remove_selfloops(line.strip().split(','))
                routes.append(path)
                for i in range(1, len(path)):
                    if not G.has_edge(path[i-1], path[i]):
                        G.add_edge(path[i-1], path[i], routes=set([route_id]))
                    else:
                        G[path[i-1]][path[i]]['routes'].add(route_id)

    mr_paths, mr_path_routes = all_shortest_paths(G, routes, num_cpus=4)

    import pickle
    with open('../results/interpolated_paths/mr_paths_june14.pickle', 'wb') as fpickle:
        pickle.dump(mr_paths, fpickle)
    with open('../results/interpolated_paths/mr_path_routes_june14.pickle', 'wb') as fpickle:
        pickle.dump(mr_path_routes, fpickle)
