import networkx as nx
import numpy as np
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

shipping_dist = dict()
#distance_file = '../data/port_shipping_distances.csv'
distance_file = '/home/larock.t/git/shipping/data/port_shipping_distances.csv'
with open(distance_file, 'r') as fin:
    for line in fin:
        u,v,dist = line.strip().split(',')
        shipping_dist[(u,v)] = float(dist)

output_file = '/scratch/larock.t/shipping/results/interpolated_paths/iterative_paths_with_routes'
redundancy_thresholds = [1.0]
distance_thresholds = [1.0, 1.05, 1.15, 1.25, 1.5, 1.75, 2.0]
all_shortest_paths(G, routes, output_file=output_file, distances=shipping_dist, redundancy_thresholds=redundancy_thresholds, distance_thresholds=distance_thresholds)
