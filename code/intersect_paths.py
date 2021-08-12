import networkx as nx
import pandas as pd
import pickle
from collections import defaultdict

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

def greedy_number_of_routes(path, subgraph, routes):
    minroute_length = 1
    for i in range(1, len(path)-1):
        ## Does next edge have same as prev edge?
        if len(subgraph[path[i-1]][path[i]]['routes'].intersection(subgraph[path[i]][path[i+1]]['routes'])) == 0:
            minroute_length += 1
    return minroute_length

print("Reading clique graph paths.", flush=True)
with open('../results/interpolated_paths/shortest_paths_clique.pickle', 'rb') as fpickle:
    paper_paths_dict = pickle.load(fpickle)

gwdata = pd.read_csv('../data/original/Nodes_2015_country_degree_bc_B_Z_P.csv', encoding='latin-1' ) ## Just need to get id to name mapping
port_to_id = dict(zip(gwdata.port.values,gwdata.id.values))
id_to_port = dict(zip(gwdata.id.values,gwdata.port.values))

print("Reading coroute graph paths.", flush=True)
with open('../results/interpolated_paths/shortest_paths_coroute.pickle', 'rb') as fpickle:
    cr_paths = pickle.load(fpickle)


print("Reading path graph paths.", flush=True)
with open('../results/interpolated_paths/shortest_paths_pathrep.pickle', 'rb') as fpickle:
    pg_paths = pickle.load(fpickle)

## Keep track of a "directed clique-graph edgelist"
## I will use this to determine whether direct connections
## in the clique graph are actually viable directed routes
routes = []
G_indirect = nx.DiGraph()
G = nx.DiGraph()
with open('../data/all_routes_2015.ngram', 'r') as fin:
    for route_id, line in enumerate(fin, start=1):
        route = remove_selfloops(line.strip().split(','))
        routes.append(route)
        for i in range(1, len(route)):
            if G.has_edge(route[i-1], route[i]):
                G[route[i-1]][route[i]]['routes'].add(route_id)
            else:
                G.add_edge(route[i-1], route[i], routes=set([route_id]))

            edge = (route[i-1], route[i])

        if route[0] != route[-1]:
            for i in range(len(route)):
                for j in range(i+1, len(route)):
                    if route[i] != route[j]:
                        G_indirect.add_edge(route[i], route[j])
        else:
            for i in range(len(route)):
                for j in range(len(route)):
                    if route[i] != route[j]:
                        G_indirect.add_edge(route[i], route[j])

directed_clique_edges = set(G_indirect.edges())


print("Reading minimum route paths.", flush=True)
with open('/scratch/larock.t/shipping/results/interpolated_paths/iterative_paths_with_routes.txt', 'r') as fin:
    minroute_paths = dict()
    ## These two dictionaries are the output
    minroutes_cg = dict()
    minroutes_pg = dict()
    minroutes_cr = dict()
    pair_counter = 0
    total_pairs = 0
    prev_pair = (-1, -1)
    first = True
    for line in fin:
        path, mr_dist, route_dist, *_ = line.strip().split('|')
        path = path.strip().split(',')
        dist = int(mr_dist)
        pair = (path[0], path[-1])
        minroute_paths.setdefault(pair, dict())
        minroute_paths[pair][tuple(path)] = dist
        if pair != prev_pair and not first:
            ## mpair is now mapped to id rather than node name!!
            mpair = (port_to_id[prev_pair[0]], port_to_id[prev_pair[1]])

            ## CLIQUE GRAPH PATHS
            for path in paper_paths_dict[mpair]:
                mpath = [id_to_port[path[i]] for i in range(len(path))]
                ## Ignore shortest paths through the clique graph
                ## that are not at all possible in the path based graph
                if not all([(mpath[i-1], mpath[i]) in G.edges() for i in range(1, len(mpath))]):
                    continue

                ## Check if the path is minimum-route by checking whether it appears
                ## in the unfiltered minimum-route paths
                tpath = tuple(mpath)
                if tpath in minroute_paths[prev_pair]:
                    minroutes_cg.setdefault(prev_pair, dict())
                    minroutes_cg[prev_pair][tpath] = int(minroute_paths[prev_pair][tpath])
                else:
                    subgraph = nx.DiGraph()
                    for i in range(1, len(mpath)):
                        subgraph.add_edge(mpath[i-1], mpath[i], routes=G[mpath[i-1]][mpath[i]]['routes'])
                    number_of_routes = greedy_number_of_routes(path, subgraph, routes)
                    tpath = tuple(mpath)
                    route_lengths.append(number_of_routes)
                    minroutes_cg.setdefault(prev_pair, dict())
                    minroutes_cg[prev_pair][tpath] = number_of_routes

            ## COROUTE GRAPH PATHS
            for path in cr_paths[prev_pair]:
                ## Ignore shortest paths through the coroute graph
                ## that are not at all possible in the path based graph
                if not all([(path[i-1], path[i]) in G.edges() for i in range(1, len(path))]):
                    continue

                ## Check if the path is minimum-route by checking whether it appears
                ## in the unfiltered minimum-route paths
                tpath = tuple(path)
                if tpath in minroute_paths[prev_pair]:
                    minroutes_cr.setdefault(prev_pair, dict())
                    minroutes_cr[prev_pair][tpath] = int(minroute_paths[prev_pair][tpath])
                else:
                    noi = set(path)
                    subgraph = nx.DiGraph()
                    for i in range(1, len(path)):
                        subgraph.add_edge(path[i-1], path[i], routes=G[path[i-1]][path[i]]['routes'])

                    number_of_routes = greedy_number_of_routes(path, subgraph, routes)
                    minroutes_cr.setdefault(prev_pair, dict())
                    minroutes_cr[prev_pair][tpath] = number_of_routes


            ## PATH GRAPH PATHS
            for path in pg_paths[prev_pair]:
                ## Check if the path is minimum-route by checking whether it appears
                ## in the unfiltered minimum-route paths
                tpath = tuple(path)
                if tpath in minroute_paths[prev_pair]:
                    minroutes_pg.setdefault(prev_pair, dict())
                    minroutes_pg[prev_pair][tpath] = int(minroute_paths[prev_pair][tpath])
                else:
                    noi = set(path)
                    subgraph = nx.DiGraph()
                    for i in range(1, len(path)):
                        subgraph.add_edge(path[i-1], path[i], routes=G[path[i-1]][path[i]]['routes'])

                    number_of_routes = greedy_number_of_routes(path, subgraph, routes)
                    minroutes_pg.setdefault(prev_pair, dict())
                    minroutes_pg[prev_pair][tpath] = number_of_routes

            del minroute_paths[prev_pair]

            pair_counter += 1
            total_pairs += 1
            if pair_counter == 5_000:
                print(f"{total_pairs} pairs processed.", flush=True)
                pair_counter = 0

        prev_pair = pair

        if first: first = False


## Need to handle the last pair...TODO: Turn these into functions so we don't just copy and paste!
## mpair is now mapped to id rather than node name!!
mpair = (port_to_id[prev_pair[0]], port_to_id[prev_pair[1]])

## CLIQUE GRAPH PATHS
for path in paper_paths_dict[mpair]:
    mpath = [id_to_port[path[i]] for i in range(len(path))]
    ## Ignore shortest paths through the clique graph
    ## that are not at all possible in the path based graph
    if not all([(mpath[i-1], mpath[i]) in G.edges() for i in range(1, len(mpath))]):
        continue

    ## Check if the path is minimum-route by checking whether it appears
    ## in the unfiltered minimum-route paths
    tpath = tuple(mpath)
    if tpath in minroute_paths[prev_pair]:
        minroutes_cg.setdefault(prev_pair, dict())
        minroutes_cg[prev_pair][tpath] = int(minroute_paths[prev_pair][tpath])
    else:
        subgraph = nx.DiGraph()
        for i in range(1, len(mpath)):
            subgraph.add_edge(mpath[i-1], mpath[i], routes=G[mpath[i-1]][mpath[i]]['routes'])
        number_of_routes = greedy_number_of_routes(path, subgraph, routes)
        tpath = tuple(mpath)
        route_lengths.append(number_of_routes)
        minroutes_cg.setdefault(prev_pair, dict())
        minroutes_cg[prev_pair][tpath] = number_of_routes

## COROUTE GRAPH PATHS
for path in cr_paths[prev_pair]:
    ## Ignore shortest paths through the coroute graph
    ## that are not at all possible in the path based graph
    if not all([(path[i-1], path[i]) in G.edges() for i in range(1, len(path))]):
        continue

    ## Check if the path is minimum-route by checking whether it appears
    ## in the unfiltered minimum-route paths
    tpath = tuple(path)
    if tpath in minroute_paths[prev_pair]:
        minroutes_cr.setdefault(prev_pair, dict())
        minroutes_cr[prev_pair][tpath] = int(minroute_paths[prev_pair][tpath])
    else:
        noi = set(path)
        subgraph = nx.DiGraph()
        for i in range(1, len(path)):
            subgraph.add_edge(path[i-1], path[i], routes=G[path[i-1]][path[i]]['routes'])

        number_of_routes = greedy_number_of_routes(path, subgraph, routes)
        minroutes_cr.setdefault(prev_pair, dict())
        minroutes_cr[prev_pair][tpath] = number_of_routes

## PATH GRAPH PATHS
for path in pg_paths[prev_pair]:
    ## Check if the path is minimum-route by checking whether it appears
    ## in the unfiltered minimum-route paths
    tpath = tuple(path)
    if tpath in minroute_paths[prev_pair]:
        minroutes_pg.setdefault(prev_pair, dict())
        minroutes_pg[prev_pair][tpath] = int(minroute_paths[prev_pair][tpath])
    else:
        noi = set(path)
        subgraph = nx.DiGraph()
        for i in range(1, len(path)):
            subgraph.add_edge(path[i-1], path[i], routes=G[path[i-1]][path[i]]['routes'])

        number_of_routes = greedy_number_of_routes(path, subgraph, routes)
        minroutes_pg.setdefault(prev_pair, dict())
        minroutes_pg[prev_pair][tpath] = number_of_routes

with open('/scratch/larock.t/shipping/results/interpolated_paths/clique_minroute_paths.pickle', 'wb') as fpickle:
    pickle.dump(minroutes_cg, fpickle)

with open('/scratch/larock.t/shipping/results/interpolated_paths/sp_pathrep_minroutes.pickle', 'wb') as fpickle:
    pickle.dump(minroutes_pg, fpickle)

with open('/scratch/larock.t/shipping/results/interpolated_paths/coroute_minroute_paths.pickle', 'wb') as fpickle:
    pickle.dump(minroutes_cr, fpickle)
