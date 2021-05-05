import re
from collections import defaultdict
from heappq import HeapPQ

def route_dijkstra(G, source):
    '''
    Accepts a route-labeled graph G and source node. Computes
    single source minimum-route distance to all nodes using a
    modified dijkstra procedure. Returns dictionary keyed by
    target node with values distance, as well as prev dictionary
    that can be passed to reverse_paths to recover minimum-route paths.

    Parameters
    ---------
    G (nx.DiGraph): A networkx DiGraph with set of routes as a property  for
                        each edge, e.g. G[u][v]['routes'] = set({r1, r2, r3}).
                        Route labels can be arbitrary, but are compared with ==.
    source (object): The source node (must appear in G.nodes()) from which
                        minimum-route distances to all other reachable nodes
                        will be computed.
    Returns
    --------
    distances (dict): Dictionary keyed by target node with value corresponding
                        to the minimum-route distance from the source.
    prev (dict): Dictionary keyed by target node with value a set of tuples of
                        the form (previous_node, route, distance). Can be passed
                        to reverse_paths() to recover actual minimum-route paths.
    '''
    distances = defaultdict(int)
    prev = defaultdict(set)
    Q = HeapPQ()
    for neighbor in G[source]:
        distances[neighbor] = 1
        for route_id in sorted(G[source][neighbor]['routes']):
            Q.add_task((neighbor, route_id, source), priority=1)
            prev[neighbor].add((source, route_id, distances[neighbor]))

    visited = set()
    while True:
        popped = Q.pop_task()
        if not popped:
            break
        else:
            d, (node, route_id, prev_node) = popped

        visited.add((d, node, route_id, prev_node))
        for neighbor in G[node]:
            ## It is possible to have cycles since
            ## we are not finding shortest paths.
            if neighbor == source:
                continue

            for nxt_route in sorted(G[node][neighbor]['routes']):
                if nxt_route == route_id:
                    ## Case 1: Next edge is the same route as previous edge
                    ## In this case, we can get to neighbor using the same
                    ## number of routes. If this is advantageous, do it.
                    ## We use greater than or equal because we want to keep
                    ## track of *all* paths in prev, not just a single path.
                    if distances.get(neighbor, float('inf')) >= distances[node] and \
                        nxt_route in [pr for _, pr, _ in prev[node]]:
                        ## If it is a strict >, reset prev
                        if distances.get(neighbor, float('inf')) > distances[node]:
                            if neighbor in prev:
                                del prev[neighbor]
                        distances[neighbor] = distances[node]
                        prev[neighbor].add((node, nxt_route, distances[neighbor]))
                        if (distances[neighbor], neighbor, nxt_route, node) not in visited:
                            Q.add_task((neighbor, nxt_route, node), priority=distances[neighbor])
                else:
                    ## Case 2: Next edge is not on the same route as previous edge
                    ## In this case, we may need to transfer routes. We use
                    ## strictly greater than because if the distances are equal,
                    ## there is already a path using fewer routes.
                    if distances.get(neighbor, float('inf')) > distances[node]:
                        ## We are adding a route, so increase the distance
                        distances[neighbor] = distances[node] + 1
                        prev[neighbor].add((node, nxt_route, distances[neighbor]))
                        if (distances[neighbor], neighbor, nxt_route, node) not in visited:
                            Q.add_task((neighbor, nxt_route, node), priority=distances[neighbor])
    return distances, prev

def reverse_paths(shortest_paths, prev, source, target):
    '''
    Accepts a (potentially empty) collections.defaultdict(dict), a
    dictionary prev (output of route_dijkstra(G, source)), a source
    node, and a target node. Follows entries in prev back to the source
    and adds all minimum-route paths discovered to shortest_paths[(source,target)]
    with value the minimum-route distance.

    Parameters
    ---------
    shortest_paths (defaultdict(dict)): A (potentially empty) defaultdict that will
                        be updated with any minimum-routes paths discovered between
                        source and target.
    prev (dict): Dictionary keyed by target node with value a set of tuples of
                        the form (previous_node, route, distance). Must be the
                        output of route_dijkstra(G, source).
    source (object): a source node (must appear in at least one prev entry)
    target (object): a target node (prev[target] must exist and be non-empty)
    '''

    path = [target]
    stack = list()
    ## Initialize the stack with entries from prev[target]
    for prev_node, route, d in prev[target]:
        stack.append((prev_node, route, d, 1, target))

    while stack:
        ## Pop the next tuple off the stack
        curr_node, curr_route, curr_d, total_d, last_node = stack.pop()

        ## Reset the path to start at last_node
        ## Note: It is vital that this happens
        ## _before_ checking if curr_node is in
        ## path, otherwise output is determined
        ## by the order of stack and may be incorrect!
        path = path[path.index(last_node):]

        if curr_node in path:
            continue

        path = [curr_node] + path
        for prev_node, prev_route, prev_d in prev[curr_node]:
            if prev_node == source:
                ## Case 1: We found the source. Save the path.
                path = [source] + path
                if (prev_d == curr_d and curr_route == prev_route):
                    shortest_paths[(source, target)][tuple(path)] = total_d
                elif (prev_d == curr_d-1 and curr_route != prev_route):
                    shortest_paths[(source, target)][tuple(path)] = total_d+1
                path = path[path.index(curr_node):]
            elif (prev_d == curr_d and curr_route == prev_route):
                ## Case 2: The next route continues the same route.
                stack.append((prev_node, prev_route, prev_d, total_d, curr_node))
            elif (prev_d == curr_d-1 and curr_route != prev_route):
                ## Case 3: The next route represents a transfer
                stack.append((prev_node, prev_route, prev_d, total_d+1, curr_node))
            ## Otherwise, ignore this entry because it will not get us closer to
            ## the source without unnecessary routes in this instance.

def all_shortest_paths(G):
    '''
    Accepts a route-labeled graph G and computes all pairs minimum-route paths
    for nodes in G. A minimum-route path should exist between every pair (source, target)
    for which nx.has_path(G, source, target) is true.

    Parameters
    ---------
    G (nx.DiGraph): A networkx DiGraph with set of routes as a property  for
                        each edge, e.g. G[u][v]['routes'] = set({r1, r2, r3}).
                        Route labels can be arbitrary, but are compared with ==.
    Returns
    ---------
    shortest_paths (defaultdict(dict)): A (potentially empty) defaultdict containing
                        all  minimum-routes paths from every source to every reahcable
                        target in G.
    '''
    shortest_paths = defaultdict(dict)
    for source in G.nodes():
        distances, prev_dict = route_dijkstra(G, source)
        for target in prev_dict:
            ## If there is an edge between them, that is the only path we
            ## are interested in
            if G.has_edge(source, target):
                shortest_paths[(source, target)][tuple([source, target])] = 1
            else:
                reverse_paths(shortest_paths, prev_dict, source, target)

    return shortest_paths



def remove_redundant_paths(paths):
    '''
    Accepts a paths defaultdict(dict), the result of all_shortest_paths(G),
    and removes (in-place) all _redundant_  minimum-route paths. A path is
    considered redundant if there is a shorter path that uses the minimum
    number of routes and touches the same nodes.

    Achieves this by mapping all paths between a given (source, target) pair
    to strings of integers, then using regular expressions to determine which
    paths are redundant.

    Parameters
    ---------
    shortest_paths (defaultdict(dict)): A (potentially empty) defaultdict containing
                        all  minimum-routes paths from every source to every reahcable
                        target in G.
    '''
    def map_path(mapping, reverse_mapping, map_idx, path):
        '''
        Convenience function that maps a path into a string of integers
        that can be more easily evaluated with regular expressions.
        '''
        mapped_sp = []
        for i in range(len(path)):
            if path[i] not in mapping:
                mapping[path[i]] = map_idx
                reverse_mapping[map_idx] = path[i]
                map_idx +=1
            mapped_sp.append(str(mapping[path[i]]))
        return mapped_sp, mapping, reverse_mapping, map_idx

    ## Counters for convenience because this process can be slow
    pair_counter = 0
    total_pairs = 0

    ## Variables to keep track of the mapping from node --> int and
    ## from int --> node.
    map_idx = 0
    mapping = dict()
    reverse_mapping = dict()

    for pair in paths:
        ## Sort the paths by length
        sorted_paths = sorted(paths[pair].keys(), key=lambda p: len(p))
        mapped_paths = []
        for path in sorted_paths:
            mapped_path, mapping, reverse_mapping, map_idx = map_path(mapping, reverse_mapping, map_idx, path)
            mapped_paths.append(mapped_path)

        max_path_len = len(sorted_paths[-1])
        removed_paths = set()
        for i in range(len(sorted_paths)):
            shorter_path = sorted_paths[i]
            if len(shorter_path) == max_path_len:
                break
            elif shorter_path in removed_paths:
                continue

            mapped_sp = mapped_paths[i]
            ## create the regex for this path
            shorter_path_pattern = ''.join([mapped_sp[i] + '.*' if i < len(mapped_sp)-1 else mapped_sp[i] for i in range(len(mapped_sp))])
            pattern = re.compile(shorter_path_pattern)
            ## Check against all longer paths
            for j in range(i+1, len(sorted_paths)):
                longer_path = sorted_paths[j]
                if len(longer_path) == len(shorter_path) or longer_path in removed_paths:
                    continue

                mapped_lp = mapped_paths[j]
                if pattern.match(''.join(mapped_lp)):
                    removed_paths.add(tuple([c for c in longer_path]))
                    del paths[pair][longer_path]

        pair_counter += 1
        total_pairs += 1
        if pair_counter == 50_000:
            print(total_pairs)
            pair_counter = 0
