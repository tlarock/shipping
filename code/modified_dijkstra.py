from collections import defaultdict
from heappq import HeapPQ

def route_dijkstra(G, source):
    ## initialize data structures
    ## Dictionary keyed by nodes with value corresponding
    ## to the minimum number of routes from source to every other node
    route_distances = defaultdict(int)
    ## Dicitionary keyed by nodes with value corresponding
    ## to the set of previous nodes, routes,distances that can
    ## be followed back to the source usingin minimum routes
    prev = defaultdict(set)
    ## Dictionary keyed by nodes with value corresponding
    ## to the set of previous routes followable back to
    ## the source node using minimum routes
    ##  Should satisfy: route_prev[node] = set([rt for _, rt, _ in prev[node]])
    route_prev = defaultdict(set)

    Q = HeapPQ()
    for node in G.nodes():
        if node == source:
            continue
        route_distances[node] = float('inf')

        ## add node to the queue once per route
        for ne in G.successors(node):
            for route_id in G[node][ne]['routes']:
                Q.add_task((node, route_id), priority=float('inf'))

    route_distances[source] = 0
    for ne in G.successors(source):
        route_distances[ne] = 1
        for route_id in G[source][ne]['routes']:
            Q.add_task((ne, route_id), priority=route_distances[ne])
            route_prev[ne].add(route_id)
            prev[ne].add((source, route_id, 1))

    visited = set()
    while True:
        ## Get the next node from the queue based on shortest path
        popped = Q.pop_task()
        if not popped:
            ## Empty queue returns false
            break
        else:
            d, (node, route_id) = popped

        visited.add((d, node, route_id))
        ## For every successor of the node
        for ne in G.successors(node):
            if route_distances[ne] >= route_distances[node]:
                ## Continue existing route
                if route_id in G[node][ne]['routes'] and route_id in route_prev.get(node, set()):
                    if route_distances[ne] > route_distances[node]:
                        if ne in route_prev:
                            del route_prev[ne], prev[ne]
                        route_distances[ne] = route_distances[node]
                    route_prev[ne].add(route_id)
                    prev[ne].add((node, route_id, route_distances[ne]))
                ## Transfer routes if it would not increase route_distances[ne]
                elif route_distances[ne] > route_distances[node] and route_id not in route_prev.get(node, set()):
                    route_distances[ne] = route_distances[node] + 1
                    if ne in prev:
                        ne_prev = set(prev[ne])
                        for tup in ne_prev:
                            if tup[-1] > route_distances[ne]:
                                prev[ne].remove(tup)

                    route_prev[ne].add(route_id)
                    prev[ne].add((node, route_id, route_distances[ne]))

                ## Add (successor, route) pairs to Q if they aren't there yet
                if ne in route_prev:
                    for next_route_id in G[node][ne]['routes']:
                        if (route_distances[ne], ne, next_route_id) not in visited and next_route_id in route_prev.get(ne, set()):
                            Q.add_task((ne, next_route_id), priority=route_distances[ne])

    return route_distances, prev


def reverse_paths(prev_dict, shortest_paths, target, source, sp_routes, G):
    '''
    Given the output of the modified dijkstra function,
    find all paths that use the minimum number of routes
    '''
    stack = []
    visited = set()
    for next_node, next_route, next_dist in prev_dict[target]:
        stack.append((next_node, next_route, next_dist, 1, target))

    curr_path = [target]
    path_routes = []
    while stack:
        node, route, dist, total_dist, prev_node = stack.pop()
        ## Reset curr_path if (1) the last node is the source (we just completed a path)
        ## OR the last node is not the start node and does not match the prev from the stack
        if curr_path[-1] == source or (curr_path[-1] != target and curr_path[-1] != prev_node):
            reset_ind = curr_path.index(prev_node)+1
            curr_path = curr_path[0:reset_ind]
            path_routes = path_routes[0:reset_ind]

        ## Adding this node would create a cyle
        if node in curr_path:
            continue

        ## If this node is connected to the source, make that connection
        if source in G.predecessors(node):
            curr_path.append(node)
            save_path = list(curr_path) + [source]
            save_path.reverse()
            save_path = tuple(save_path)

            save_dist = total_dist
            if route not in G[source][node]['routes']:
                save_dist += 1
                path_routes.append(next(iter(G[source][node]['routes'])))

            save_routes = path_routes
            save_routes.reverse()
            save_routes = tuple(save_routes)

            ## remove any paths that are no longer optimal
            min_so_far = float('inf')
            if (source, target) in shortest_paths and len(shortest_paths[(source,target)]) > 0:
                min_so_far = min([r for _, r in shortest_paths[(source,target)].items()])
            if min_so_far < float('inf') and save_dist < min_so_far:
                del shortest_paths[(source,target)]
                del sp_routes[(source,target)]

            if save_path in shortest_paths[(source, target)]:
                if shortest_paths[(source, target)][save_path] > save_dist:
                    shortest_paths[(source, target)][save_path] = save_dist
                    sp_routes[(source, target)][save_path] = save_routes
            elif save_dist <= min_so_far:
                shortest_paths[(source, target)][save_path] = save_dist
                sp_routes[(source, target)][save_path] = save_routes

            ## Reset path to continue reading stack
            curr_path = curr_path[0:-1]
            path_routes = path_routes[0:-1]
        else:
            add_to_path = False
            for next_node,next_route,next_dist in prev_dict[node]:
                ## if the routes match, accept this node
                if next_route == route and next_dist <= dist:
                    stack.append((next_node, next_route, next_dist, total_dist, node))
                    add_to_path = True

                ## If the routes don't match, only accept if the distance
                ## from the next node is 1 less than the current, meaning we are
                ## changing routes in a move _towards_ the source
                elif next_dist == (dist - 1):
                    stack.append((next_node, next_route, next_dist, total_dist+1, node))
                    add_to_path = True

            ## Actually add the node to the path
            if add_to_path:
                curr_path.append(node)
                if len(path_routes) == 0 or route != path_routes[-1]:
                    path_routes.append(route)



def all_shortest_paths(G):
    shortest_paths = defaultdict(dict)
    sp_routes = defaultdict(dict)
    for source in G.nodes():
        print(f"Source: {source}.")
        distances, prev_dict = route_dijkstra(G, source)
        for target in prev_dict:
            ## If there is an edge between them, that is the only path we
            ## are interested in
            if G.has_edge(source,target):
                shortest_paths[(source,target)][tuple([source, target])] = 1
                for route in G[source][target]['routes']:
                    sp_routes[(source,target)][tuple([source,target])] = tuple([route])
            else:
                reverse_paths(prev_dict, shortest_paths, target, source, sp_routes, G)

    return shortest_paths, sp_routes
