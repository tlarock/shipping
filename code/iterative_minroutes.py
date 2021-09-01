import os
import networkx as nx
from contextlib import ExitStack
from collections import defaultdict, Counter


def compute_route_dist(path, distances):
    d = 0.0
    for i in range(1, len(path)):
        d += distances[path[i-1], path[i]]
    return d

def write_pair(shortest_paths, s, t, mr_dist, open_outfile, distances):
    total_distances = dict()
    if distances is not None:
        total_distances = {path:compute_route_dist(path, distances) for path in shortest_paths[mr_dist][s][t]}
    for path, route_list in shortest_paths[mr_dist][s][t].items():
        if distances is None:
            open_outfile.write(','.join(path) + '|' + str(mr_dist) + '|' + '|'.join([','.join(map(str, r)) for r in route_list]) + '\n')
        else:
            open_outfile.write(','.join(path) + '|' + str(mr_dist) + '|' + str(total_distances[path]) + '|' + '|'.join([','.join(map(str, r)) for r in route_list]) + '\n')

    return total_distances

def write_filtered(shortest_paths, s, t, total_distances, mr_dist, ffilt, dr_thresholds):
    def get_compare_path(path, redundancy_thresh):
        if redundancy_thresh == 1.0:
            ## If the redundancy threhold is the whole path,
            ## we don't need to remove the endpoints.
            compare_path = path
        else:
            ## Remove the source and target
            compare_path = list(path)
            del compare_path[0], compare_path[-1]
        return compare_path

    filtered_paths = set()
    ## Get sorted list of paths
    paths_by_length = dict()
    for path in total_distances.keys():
        paths_by_length.setdefault(len(path), set())
        paths_by_length[len(path)].add(path)

    sorted_lengths = sorted(paths_by_length.keys(), reverse=True)
    ## Filter based on redundancy
    ## Loop from longest to 2nd from shortest
    for i in range(len(sorted_lengths)-1):
        length = sorted_lengths[i]
        for longer_path in paths_by_length[length]:
            broken = False
            #compare_path = get_compare_path(longer_path, redundancy_thresh=1.0)
            compare_path = set(longer_path)
            ## Check against all shorter paths
            ## Loop over all shortest path lengths
            for j in range(len(sorted_lengths)-1, i, -1):
                slength = sorted_lengths[j]
                for shorter_path in paths_by_length[slength]:
                    #shorter_cmp_path = get_compare_path(shorter_path, redundancy_thresh=1.0)
                    shorter_cmp_path = set(shorter_path)
                    if (len(shorter_cmp_path.intersection(compare_path)) / len(shorter_cmp_path)) >= 1.0:
                        filtered_paths.add(longer_path)
                        ## We can break as soon as we find one shorter_path
                        ## that longer_path is redundant with
                        broken = True
                        break
                if broken:
                    break

    redundancy_filtered = set(filtered_paths)
    available_paths = set(shortest_paths[mr_dist][s][t])-redundancy_filtered
    min_dist = min([total_distances[path] for path in available_paths])
    for (distance_thresh, _) in dr_thresholds:
        ## Compute minimum distance among remaining paths
        filtered_paths = set(redundancy_filtered)
        ## Do final distance filtering
        for path in available_paths:
            if total_distances[path] > min_dist*distance_thresh:
                filtered_paths.add(path)

        assert len(filtered_paths) != len(shortest_paths[mr_dist][s][t]), f"All paths filtered for pair {s} and {t}!\nTotal distances:\n{total_distances}"

        for path, route_list in shortest_paths[mr_dist][s][t].items():
            if path not in filtered_paths:
                ffilt[distance_thresh][1.0].write(','.join(path) + '|' + str(mr_dist) + '|' + str(total_distances[path]) + '|' + '|'.join([','.join(map(str, r)) for r in route_list]) + '\n')


def all_shortest_paths(G, all_routes, output_file='', distances=None, distance_thresholds=[], redundancy_thresholds=[]):
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
    def _add_path(shortest_paths, source, target, path, route_id):
        shortest_paths[1].setdefault(source, dict())
        shortest_paths[1][source].setdefault(target, dict())
        path_tup = tuple(path)
        shortest_paths[1][source][target].setdefault(path_tup, set())
        route_list = [f'{route_id}:{len(path)-1}']
        shortest_paths[1][source][target][path_tup].add(tuple(route_list))

    def _add_open_walk(route, route_id, shortest_paths, pairs_counted):
        for i in range(len(route)):
            for j in range(i+1, len(route)):
                if route[i] != route[j]:
                    path = route[i:j+1]
                    ## Add the path as long as the target appears only once
                    if path.count(route[j]) == 1:
                        _add_path(shortest_paths, route[i], route[j], path, route_id)
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

                    ## Add the path as long as the target appears only once
                    if path.count(route[j]) == 1:
                        _add_path(shortest_paths, route[i], route[j], path, route_id)
                        pairs_counted[(route[i], route[j])] = dist

    assert min([rt for _,_, edat in G.edges(data=True) for rt in edat['routes']]) > 0, "Route labels must begin with 1."
    dr_thresholds = []
    if (len(distance_thresholds) > 0 or len(redundancy_thresholds) > 0):
        assert output_file != '', "Filtering only makes sense if output_file is specified."
        assert len(distance_thresholds) > 0 and len(redundancy_thresholds) > 0, 'Include at least 1 value for each threshold for filtering.'
        dr_thresholds = []
        for dt in distance_thresholds:
            for rt in redundancy_thresholds:
                dr_thresholds.append((dt,rt))

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
            fout = stack.enter_context(open(output_file + '.txt', 'w'))
            if len(dr_thresholds) > 0:
                ## Open file for outputting filtered paths
                ffilt = dict()
                for (distance_threshold, redundancy_threshold) in dr_thresholds:
                    ffilt.setdefault(distance_threshold, dict())
                    ffilt[distance_threshold][redundancy_threshold] = stack.enter_context(open(output_file + f'_filtered_dt-{distance_threshold}_rt-{redundancy_threshold}.txt', 'w'))

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
                total_distances = write_pair(shortest_paths, s, t, dist, fout, distances)
                if len(dr_thresholds) > 0:
                    write_filtered(shortest_paths, s, t, total_distances, dist, ffilt, dr_thresholds)

        ## Ensure we've got paths for every pair we should
        for (s,t) in all_distances.keys():
            if all_distances[(s,t)] == 1:
                assert (s,t) in pairs_counted, f"({s},{t}) not in pairs_counted!"

        remaining_pairs = reachable_pairs-set(pairs_counted.keys())
        print(f'{len(remaining_pairs)} remaining after distance 1.', flush=True)
        fout.flush()
        os.fsync(fout.fileno())
        for (distance_thresh,_) in dr_thresholds:
            ffilt[distance_thresh][1.0].flush()
            os.fsync(ffilt[distance_thresh][1.0].fileno())

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
                                all_path_routes = []
                                for r1 in shortest_paths[dist-1][s][w][p1]:
                                    for r2 in shortest_paths[1][w][t][p2]:
                                        route_list = r1+r2
                                        all_path_routes.append(route_list)
                                        ## Sometimes a specific ordering of routes actually violates
                                        ## the closed vs. open walk assumption, resulting in a route
                                        ## trajectory that looks shorter than what is actually possible.
                                        ## Although these paths are technically valid, they require 1
                                        ## more transfer (at least), so we do not want to record them.
                                        ## We just ignore these cases using the below conditional.
                                        if len(set(route_list)) == dist:
                                            shortest_paths[dist][s][t][path].append(route_list)

                                ## If for there are *no* valid route combinations that do not use
                                ## the same route multiple times, assign all_path_routes
                                if len(shortest_paths[dist][s][t][path]) == 0:
                                    shortest_paths[dist][s][t][path] = list(all_path_routes)


                assert found_t, f"Did not find t {t} from s {s}."
                assert t in shortest_paths[dist][s], f"shortest_paths[{dist}[{s}] does not contain {t}."
                assert len(shortest_paths[dist][s][t]) > 0, f"No paths found between {s} and {t}."

                ## Add (s,t) to pairs_counted
                pairs_counted[(s,t)] = dist

                if fout is not None:
                    total_distances = write_pair(shortest_paths, s, t, dist, fout, distances)
                    if len(dr_thresholds) > 0:
                        write_filtered(shortest_paths, s, t, total_distances, dist, ffilt, dr_thresholds)

            remaining_pairs = reachable_pairs-set(pairs_counted.keys())
            print(f'{len(remaining_pairs)} remaining after distance {dist}.', flush=True)
            fout.flush()
            os.fsync(fout.fileno())
            for (distance_thresh,_) in dr_thresholds:
                ffilt[distance_thresh][1.0].flush()
                os.fsync(ffilt[distance_thresh][1.0].fileno())


    return shortest_paths
