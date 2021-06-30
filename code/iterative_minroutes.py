import networkx as nx
from contextlib import ExitStack
from collections import defaultdict, Counter

def all_shortest_paths(G, all_routes, output_file='', distances=None):
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
    def compute_route_dist(path, distances):
        d = 0.0
        for i in range(1, len(path)):
            d += distances[path[i-1], path[i]]
        return d

    def write_pair(shortest_paths, s, t, mr_dist, fout, distances):
        for path, route_list in shortest_paths[mr_dist][s][t].items():
            if distances is None:
                fout.write(','.join(path) + '|' + str(mr_dist) + '|' + '|'.join([','.join(map(str, r)) for r in route_list]) + '\n')
            else:
                fout.write(','.join(path) + '|' + str(mr_dist) + '|' + str(compute_route_dist(path, distances)) + '|' + '|'.join([','.join(map(str, r)) for r in route_list]) + '\n')

    def _add_open_walk(route, route_id, shortest_paths,pairs_counted):
        for i in range(len(route)):
            for j in range(i+1, len(route)):
                if route[i] != route[j]:
                    path = route[i:j+1]
                    ## If the target appears more than once ignore this  path
                    if path.count(route[j]) == 1:
                        shortest_paths[1].setdefault(route[i], dict())
                        shortest_paths[1][route[i]].setdefault(route[j], dict())
                        shortest_paths[1][route[i]][route[j]].setdefault(tuple(path), set())
                        route_list = [route_id]*(len(path)-1)
                        shortest_paths[1][route[i]][route[j]][tuple(path)].add(tuple(route_list))
                        pairs_counted[(route[i], route[j])] = dist

    def _add_closed_walk(route, route_id, shortest_paths, pairs_counted):
        for i in range(len(route)):
            for j in range(len(route)):
                if route[i] != route[j]:
                    if i < j:
                        path = route[i:j+1]
                    else:
                        if i < len(route):
                            path = route[i:]
                        else:
                            path = [route[i]]
                        if j == 0 and path[-1] != route[0]:
                            path += [route[0]]
                        elif j > 0:
                            path += route[1:j+1]
                    shortest_paths[1].setdefault(route[i], dict())
                    shortest_paths[1][route[i]].setdefault(route[j], dict())
                    shortest_paths[1][route[i]][route[j]].setdefault(tuple(path), set())
                    route_list = [route_id]*(len(path)-1)
                    shortest_paths[1][route[i]][route[j]][tuple(path)].add(tuple(route_list))
                    pairs_counted[(route[i], route[j])] = dist


    assert min([rt for _,_, edat in G.edges(data=True) for rt in edat['routes']]) > 0, "Route labels must begin with 1."

    ## Get all reachable pairs
    reachable_pairs = set()
    for node in G.nodes():
        reachable_pairs.update([(node, ne) for ne in nx.descendants(G, node)])

    ## Compute co-route graph
    G_indirect = nx.DiGraph()
    for route_id, route in enumerate(all_routes, start=1):
        ## Open
        if route[0] != route[-1]:
            for i in range(len(route)):
                for j in range(i+1, len(route)):
                    if route[i] != route[j]:
                        G_indirect.add_edge(route[i], route[j])
        ## Closed
        else:
            for i in range(len(route)):
                for j in range(len(route)):
                    if route[i] != route[j]:
                        G_indirect.add_edge(route[i], route[j])

    all_distances = {(s,t):nx.shortest_path_length(G_indirect, s, t) for (s,t) in reachable_pairs}
    ## Compute all pairs min route paths 
    pairs_counted = dict()
    shortest_paths = defaultdict(dict)

    ## This context manager allows me to conditionally write to a file on the fly
    with ExitStack() as stack:
        fout = None
        if output_file != '':
            fout = stack.enter_context(open(output_file, 'w'))

        ## Compute all 1-route pairs
        dist = 1
        for route_id, route in enumerate(all_routes, start=1):
            if route[0] == route[-1]:
                ## Closed walk
                _add_closed_walk(route, route_id, shortest_paths, pairs_counted)
            else:
                ## Open walk
                _add_open_walk(route, route_id, shortest_paths, pairs_counted)

        ##  Write to file if specified
        if fout is not None:
            for (s,t) in pairs_counted.keys():
                write_pair(shortest_paths, s, t, dist, fout, distances)
        for (s,t) in all_distances.keys():
            if all_distances[(s,t)] == 1:
                assert (s,t) in pairs_counted, f"({s},{t}) not in pairs_counted!"

        remaining_pairs = reachable_pairs-set(pairs_counted.keys())
        print(f'{len(remaining_pairs)} remaining after distance 1.', flush=True)
        while len(remaining_pairs) > 0:
            dist+=1
            ## Add another route
            for (s,t) in remaining_pairs:
                true_distance = all_distances[(s,t)]
                if true_distance > dist:
                    continue
                found_t = False
                for w in shortest_paths[dist-1][s]:
                    if w not in shortest_paths[1]:
                        ## If w can't reach any other nodes in 1 route,
                        ## then it certainly cannot reach t using 1
                        ## additional route, so skip it
                        continue
                    ## If t can be reached from w using 1 additional route,
                    ## then t can be reached using dist routes
                    if t in shortest_paths[1][w]:
                        found_t = True
                        for p1 in shortest_paths[dist-1][s][w]:
                            for p2 in shortest_paths[1][w][t]:
                                shortest_paths[dist].setdefault(s, dict())
                                shortest_paths[dist][s].setdefault(t, dict())
                                path = p1[0:] + p2[1:]
                                shortest_paths[dist][s][t].setdefault(path, list())
                                for r1 in shortest_paths[dist-1][s][w][p1]:
                                    for r2 in shortest_paths[1][w][t][p2]:
                                        route_list = r1+r2
                                        ## Sometimes a specific ordering of routes actually violates
                                        ## the closed vs. open walk assumption, resulting in a route
                                        ## trajectory that looks shorter than what is actually possible.
                                        ## Although these paths are technically valid, they require 1
                                        ## more transfer (at least), so we do not want to record them.
                                        ## We just ignore these cases using the below conditional.
                                        if len(set(route_list)) == dist:
                                            shortest_paths[dist][s][t][path].append(route_list)

                assert found_t, f"Did not find t {t} from s {s}."
                assert t in shortest_paths[dist][s], f"shortest_paths[{dist}[{s}] does not contain {t}."
                assert len(shortest_paths[dist][s][t]) > 0, f"No paths found between {s} and {t}."
                pairs_counted[(s,t)] = dist

                if fout is not None:
                    write_pair(shortest_paths, s, t, dist, fout, distances)


            remaining_pairs = reachable_pairs-set(pairs_counted.keys())
            print(f'{len(remaining_pairs)} remaining after distance {dist}.', flush=True)

    return shortest_paths
