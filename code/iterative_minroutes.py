import networkx as nx
from collections import defaultdict, Counter

def has_cycle(path):
    node_counts = Counter(path)
    if max(node_counts.values()) > 1:
        return True
    else:
        return False

def all_shortest_paths(G, all_routes, num_cpus=1, log_every=50000, print_st=False):
    '''
    Accepts a route-labeled graph G and computes all pairs minimum-route paths
    for nodes in G. A minimum-route path should exist between every pair (source, target)
    for which nx.has_path(G, source, target) is true.

    Parameters
    ---------
    G (nx.DiGraph): A networkx DiGraph with set of routes as a property  for
                    each edge, e.g. G[u][v]['routes'] = set({r1, r2, r3}).
                    Route labels can be arbitrary in principle, but must
                    be == comparable.
    Returns
    ---------
    shortest_paths (defaultdict(dict)): A (potentially empty) defaultdict containing
                        all  minimum-routes paths from every source to every reahcable
                        target in G.
    '''
    def _add_open_walk(route, route_id, i, j, shortest_paths,pairs_counted):
        for i in range(len(route)):
            for j in range(i+1, len(route)):
                if route[i] != route[j]:
                    path = route[i:j+1]
                    if not has_cycle(path):
                        shortest_paths[dist].setdefault(route[i], dict())
                        shortest_paths[dist][route[i]].setdefault(route[j], dict())
                        shortest_paths[dist][route[i]][route[j]].setdefault(tuple(path), set())
                        shortest_paths[dist][route[i]][route[j]][tuple(path)].add(tuple([route_id]*(len(path)-1)))
                        pairs_counted[(route[i], route[j])] = dist

    def _add_closed_walk(route, route_id, i, j, shortest_paths, pairs_counted):
        for i in range(len(route)):
            for j in range(len(route)):
                if route[i] != route[j]:
                    if i < j:
                        path = route[i:j+1]
                        shortest_paths[dist].setdefault(route[i], dict())
                        shortest_paths[dist][route[i]].setdefault(route[j], dict())
                        shortest_paths[dist][route[i]][route[j]].setdefault(tuple(path), set())
                        shortest_paths[dist][route[i]][route[j]][tuple(path)].add(tuple([route_id]*(len(path)-1)))
                    else:
                        if i < len(route):
                            path = route[i:]
                        else:
                            path = [route[i]]
                        if j == 0 and path[-1] != route[0]:
                            path += [route[0]]
                        elif j > 0:
                            path += route[1:j+1]
                        shortest_paths[dist].setdefault(route[i], dict())
                        shortest_paths[dist][route[i]].setdefault(route[j], dict())
                        shortest_paths[dist][route[i]][route[j]].setdefault(tuple(path), set())
                        shortest_paths[dist][route[i]][route[j]][tuple(path)].add(tuple([route_id]*(len(path)-1)))

                    pairs_counted[(route[i], route[j])] = dist


    assert min([rt for _,_, edat in G.edges(data=True) for rt in edat['routes']]) > 0, "Route labels must begin with 1."
    ## Logging variables
    num_pairs = 0
    pair_count = 0
    total_pairs = len(G.nodes())*len(G.nodes())

    ## Edge indices + clique distances
    G_indirect = nx.DiGraph()
    for route_id, route in enumerate(all_routes, start=1):
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

    ## Compute all pairs min route paths
    ## Get all reachable pairs
    reachable_pairs = set()
    for node in G.nodes():
        reachable_pairs.update([(node, ne) for ne in nx.descendants(G, node)])

    pairs_counted = dict()
    shortest_paths = defaultdict(dict)

    ## Compute all 1-route pairs
    dist = 1
    for route_id, route in enumerate(all_routes, start=1):
        if route[0] == route[-1]:
            ## Closed walk
            _add_closed_walk(route, route_id, i, j, shortest_paths, pairs_counted)
        else:
            ## Open walk
            _add_open_walk(route, route_id, i, j, shortest_paths, pairs_counted)

    remaining_pairs = reachable_pairs-set(pairs_counted.keys())
    print(f'{len(remaining_pairs)} remaining after distance 1.')
    while len(remaining_pairs) > 0:
        dist+=1
        ## Add another route
        for (s,t) in remaining_pairs:
            true_distance = nx.shortest_path_length(G_indirect, s, t)
            if true_distance > dist:
                continue
            for w in shortest_paths[dist-1][s]:
                if w not in shortest_paths[1]:
                    ## If w can't reach any other nodes in 1 route,
                    ## then it certainly cannot reach t using 1
                    ## additional route, so skip it
                    continue
                ## If t can be reached from w using 1 additional route,
                ## then t can be reached using dist routes
                if t in shortest_paths[1][w]:
                    for p1 in shortest_paths[dist-1][s][w]:
                        for p2 in shortest_paths[1][w][t]:
                            shortest_paths[dist].setdefault(s, dict())
                            shortest_paths[dist][s].setdefault(t, dict())
                            shortest_paths[dist][s][t].setdefault(p1[0:]+p2[1:], list())
                            for r1 in shortest_paths[dist-1][s][w][p1]:
                                for r2 in shortest_paths[1][w][t][p2]:
                                    shortest_paths[dist][s][t][p1[0:]+p2[1:]].append(r1+r2)

                            pairs_counted[(s,t)] = dist

        remaining_pairs = reachable_pairs-set(pairs_counted.keys())
        print(f'{len(remaining_pairs)} remaining after distance {dist}.')

    return shortest_paths
