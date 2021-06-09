from collections import defaultdict
from heappq import HeapPQ

def route_dijkstra(G, source, routes_by_node):
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
                        Route labels can be arbitrary in principle, but must
                        be == comparable.
    source (object): The source node (must appear in G.nodes()) from which
                        minimum-route distances to all other reachable nodes
                        will be computed.
    routes_by_node (dict): A dictionary keyed by node with value corresopnding
                        to the set of routes leaving a node. Speeds up checking
                        whether a route can possibly follow a node.
    Returns
    --------
    distances (dict): Dictionary keyed by target node with value corresponding
                        to the minimum-route distance from the source.
    prev (dict): Dictionary keyed by target node with value a set of tuples of
                        the form (previous_node, route, distance). Can be passed
                        to reverse_paths() to recover actual minimum-route paths.
    '''
    ## Distances and prev dictionaries
    distances = defaultdict(int)
    prev = defaultdict(set)
    ## This is a convenience data structure that makes it
    ## easy to check whether a (route, distance) edge appears
    ## in prev of any node. The information should match prev.
    rd_pairs = defaultdict(set)
    Q = HeapPQ()
    for neighbor in G[source]:
        distances[neighbor] = 1
        for route_id in sorted(G[source][neighbor]['routes']):
            Q.add_task((neighbor, route_id, source), priority=1)
            prev[neighbor].add((source, route_id, distances[neighbor]))
            rd_pairs[neighbor].add((route_id,distances[neighbor]))

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
                    if distances.get(neighbor, float('inf')) >= distances[node]:
                        ## Check if this route is on a minimum-route path
                        if (nxt_route, distances[node]) in rd_pairs[node]:
                            distances[neighbor] = distances[node]
                            prev[neighbor].add((node, nxt_route, distances[node]))
                            rd_pairs[neighbor].add((nxt_route, distances[node]))
                            if (distances[node], neighbor, nxt_route, node) not in visited:
                                Q.add_task((neighbor, nxt_route, node), priority=distances[node])
                else:
                    ## Case 2: Next edge is not on the same route as previous edge
                    ## In this case, we may need to transfer routes. We use
                    ## strictly greater than because if the distances are equal,
                    ## there is already a path using fewer routes.
                    if distances.get(neighbor, float('inf')) > distances[node]:
                        ## We are adding a route, so increase the distance
                        distances[neighbor] = distances[node] + 1
                        prev[neighbor].add((node, nxt_route, distances[neighbor]))
                        rd_pairs[neighbor].add((nxt_route, distances[neighbor]))
                        if (distances[neighbor], neighbor, nxt_route, node) not in visited:
                            Q.add_task((neighbor, nxt_route, node), priority=distances[neighbor])
                    elif distances.get(neighbor, float('inf')) == distances[node]:
                        ## If the distances are equal, we still may want to include a prev
                        ## entry if it is possible that this route will be shorter for another
                        ## target besides neighbor
                        ## Check whether nxt_route also appears after neighbor
                        if nxt_route in routes_by_node[neighbor]:
                            prev[neighbor].add((node, nxt_route, distances[node]+1))
                            rd_pairs[neighbor].add((nxt_route, distances[node]+1))
                            if (distances[node]+1, neighbor, nxt_route, node) not in visited:
                                Q.add_task((neighbor, nxt_route, node), priority=distances[node]+1)

    return distances, prev

def verify_route(path, path_routes, all_routes):
    '''
    Verify that a route is actually possible. Necessary to allow paths
    with cycles in them, especially from cyclic routes.
    '''
    previous_route = -1
    for i in range(len(path)-1):
        edge = [path[i], path[i+1]]
        curr_route_id = path_routes[i]
        roi = all_routes[curr_route_id-1]
        if previous_route == curr_route_id:
            ## Need to check that the previous and
            ## current edges appear in sequence
            previous_edge = [path[i-1], path[i]]
            ## First check if they are at the ends
            found_edge = False
            if previous_edge == roi[-2:] and edge == roi[0:2]:
                found_edge = True
            else:
                ## Otherwise check the whole route
                for j in range(1, len(roi)+1):
                    if previous_edge == roi[j-1:j+1] and edge == roi[j:j+2]:
                        found_edge = True
                        break
        else:
            ## Check that the edge exists somewhere in the route
            found_edge = False
            for j in range(len(roi)+1):
                if edge == roi[j:j+2]:
                    found_edge = True
                    break
        if not found_edge:
            break
        previous_route = curr_route_id

    return found_edge

def reverse_paths(shortest_paths, shortest_path_routes, prev, source, target, all_routes, distances):
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
    def compute_reset(path, noi, ln_count):
        if ln_count == 1:
            reset_idx = -(len(path) - (path[::-1].index(noi)+1))+1
        else:
            path_count = 0
            for idx, node in enumerate(path[::-1]):
                if node == noi:
                    path_count += 1
                if path_count == ln_count:
                    reset_idx = -idx-1
                    break
        return reset_idx

    def count_nodes(path):
        cycle_nodes = set()
        node_counts = dict.fromkeys(set(path), 0)
        for node in path:
            node_counts[node] += 1
            if node_counts[node] > 1:
                cycle_nodes.add(node)

        return node_counts, len(cycle_nodes)

    path = [target]
    path_routes = []
    stack = list()
    ## Initialize the stack with entries from prev[target]
    for prev_node, route, d in prev[target]:
        stack.append((prev_node, route, d, 1, target, 1))

    while stack:
        ## Pop the next tuple off the stack
        curr_node, curr_route, curr_d, total_d, last_node, ln_count = stack.pop()
        ## Reset the path to start at last_node
        ## Note: It is vital that this happens
        ## _before_ checking if curr_node is in
        ## path, otherwise output is determined
        ## by the order of stack and may be incorrect!
        num_ln = sum([1 for u in path if u == last_node])
        if path[0] != last_node or num_ln > ln_count:
            if num_ln > 1:
                reset_idx = compute_reset(path, last_node, ln_count)
            else:
                reset_idx = path.index(last_node)

            if path[reset_idx] == last_node:
                path = path[reset_idx:]
            else:
                path = path[reset_idx-1:]

            if len(path) == 1:
                path_routes = []
            elif path_routes[reset_idx:] == len(path)-1:
                path_routes = path_routes[reset_idx:]
            else:
                path_routes = path_routes[len(path_routes)-len(path)+1:]
            assert len(path) == len(path_routes)+1, f'1. {path}, {path_routes}, {reset_idx}'

        ## This conditional should prevent us from getting trapped in infinite cycles
        node_counts, num_cycles = count_nodes([curr_node] + path)
        if node_counts[curr_node] > 2 or num_cycles > 1:
            reset_idx = compute_reset(path, last_node, ln_count)
            path = path[reset_idx:]
            if len(path) == 1:
                path_routes = []
            else:
                path_routes = path_routes[reset_idx:]
            assert len(path) == len(path_routes)+1, f'2. {path}, {path_routes}, {reset_idx}'
            continue

        path = [curr_node] + path
        path_routes = [curr_route] + path_routes
        for prev_node, prev_route, prev_d in prev[curr_node]:
            if prev_node == source:
                ## Case 1: We found the source. Save the path.
                ## Extra conditionals just make sure we only
                ## have the paths at the right distance
                path = [source] + path
                path_routes = [prev_route] + path_routes
                ## Verify the route
                if (prev_d == curr_d and curr_route == prev_route) and total_d == distances[target]:
                    if verify_route(path, path_routes, all_routes):
                        shortest_paths[(source, target)][tuple(path)] = total_d
                        shortest_path_routes[(source,target)].setdefault(tuple(path),[])
                        shortest_path_routes[(source,target)][tuple(path)].append(path_routes)
                elif (prev_d == curr_d-1 and curr_route != prev_route) and total_d+1 == distances[target]:
                    if verify_route(path, path_routes, all_routes):
                        shortest_paths[(source, target)][tuple(path)] = total_d+1
                        shortest_path_routes[(source,target)].setdefault(tuple(path),[])
                        shortest_path_routes[(source,target)][tuple(path)].append(path_routes)

                ## Reset path to the most recent occuurence of curr_node
                reset_idx = path.index(curr_node)
                path = path[reset_idx:]
                if len(path) == 1:
                    path_routes = []
                else:
                    path_routes = path_routes[reset_idx:]
                assert len(path) == len(path_routes)+1, f'3. {path}, {path_routes}'
            elif prev_d == curr_d and curr_route == prev_route and prev_node != target:
                ## Case 2: The next route continues the same route.
                stack.append((prev_node, prev_route, prev_d, total_d, curr_node, node_counts[curr_node]))
            elif prev_d == curr_d-1 and curr_route != prev_route and prev_node != target:
                ## Case 3: The next route represents a transfer
                stack.append((prev_node, prev_route, prev_d, total_d+1, curr_node, node_counts[curr_node]))
            ## Otherwise, ignore this entry because it will not get us closer to
            ## the source without unnecessary routes in this instance.

def all_shortest_paths(G, all_routes, log_every=50000, print_st=False):
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
    assert min([rt for _,_, edat in G.edges(data=True) for rt in edat['routes']]) > 0, "Route labels must begin with 1."
    ## Logging variables
    num_pairs = 0
    pair_count = 0
    total_pairs = len(G.nodes())*len(G.nodes())

    ## Routes by node
    routes_by_node = dict()
    for node in G.nodes():
        routes_by_node[node] = set()
        for neighbor in G[node]:
            routes_by_node[node].update(set([route for route in G[node][neighbor]['routes']]))

    ## Compute all pairs min route paths
    shortest_paths = defaultdict(dict)
    shortest_path_routes = defaultdict(dict)
    for source in G.nodes():
        if print_st:
            print(f'Source: {source}', flush=True)

        distances, prev_dict = route_dijkstra(G, source, routes_by_node)
        for target in prev_dict:
            if print_st:
                print(f'\tTarget: {target}', flush=True)

            ## If there is an edge between them, that is the only path we
            ## are interested in
            if G.has_edge(source, target):
                shortest_paths[(source, target)][tuple([source, target])] = 1
                shortest_path_routes[(source,target)][(source,target)] = []
                for route_id in G[source][target]['routes']:
                    shortest_path_routes[(source,target)][(source,target)].append([route_id])
            else:
                reverse_paths(shortest_paths, shortest_path_routes, prev_dict, source, target, all_routes, distances)

            num_pairs += 1
            pair_count +=1
            if num_pairs == log_every:
                num_pairs = 0
                print(f'Approx. {total_pairs-pair_count} remaining.', flush=True)

    return shortest_paths, shortest_path_routes
