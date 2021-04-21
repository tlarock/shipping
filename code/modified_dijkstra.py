from collections import defaultdict
from heappq import HeapPQ

def route_dijkstra(G, source, num_routes):
    ## initialize data structure
    route_distances = defaultdict(int)
    route_prev = defaultdict(set)
    prev = defaultdict(set)
    Q = HeapPQ()
    total_queue_size = 0
    for node in G.nodes():
        if node == source:
            continue
        route_distances[node] = float('inf')
        for route_id in range(1, num_routes+1):
            route_distances[node] = float('inf')

        ## add node to the queue once per route
        for ne in G.successors(node):
            for route_id in G[node][ne]['routes']:
                Q.add_task((node, route_id), priority=float('inf'))
                total_queue_size+=1
    route_distances[source] = 0
    for ne in G.successors(source):
        route_distances[ne] = 1
        for route_id in G[source][ne]['routes']:
            Q.add_task((ne, route_id), priority=route_distances[ne])
            total_queue_size+=1
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
                if route_id in G[node][ne]['routes'] and route_id in route_prev[node]:
                    route_distances[ne] = route_distances[node]
                    route_prev[ne].add(route_id)
                    prev[ne].add((node, route_id, route_distances[ne]))
                elif route_distances[ne] > route_distances[node] and route_id not in route_prev[node]:
                    route_distances[ne] = route_distances[node] + 1
                    route_prev[ne].add(route_id)
                    prev[ne].add((node, route_id, route_distances[ne]))

                for next_route_id in G[node][ne]['routes']:
                    if (route_distances[ne], ne, next_route_id) not in visited:
                        Q.add_task((ne, next_route_id), priority=route_distances[ne])
                        total_queue_size += 1

    return route_distances, prev

def reverse_paths(prev_dict, shortest_paths, start_node, source, precomputed_paths):
    '''
    Given the output of the modified dijkstra function,
    find all paths that use the minimum number of routes
    '''
    stack = []
    visited = set()
    for next_node, next_route, next_dist in prev_dict[start_node]:
        stack.append((next_node, next_route, next_dist, start_node))

    sub_paths = dict()
    curr_path = [start_node]
    while stack:
        node, route, dist, prev_node = stack.pop()

        ## Reset curr_path if (1) the last node is the source (we just completed a path)
        ## OR the last node is not the start node and does not match the prev from the stack
        if curr_path[-1] == source or (curr_path[-1] != start_node and curr_path[-1] != prev_node):
            curr_path = curr_path[0:curr_path.index(prev_node)+1]

        ## Adding this node would create a cyle
        if node in curr_path:
            continue
        ## If we've found the source, save the path
        if node == source:
            curr_path.append(node)
            save_path = list(curr_path)
            save_path.reverse()
            shortest_paths[(source, start_node)].add(tuple(save_path))
            print("Saving path: ", save_path)
            ## save sub paths for reuse
            for i in range(1, len(save_path)):
                if save_path[i] == save_path[-1]:
                    continue
                precomputed_paths[(save_path[i], save_path[-1], route)].add(tuple(save_path[i:]))

            ## Reset path to continue reading stack
            curr_path = curr_path[0:-1]
        else:
            ## Should we add this node to the path?
            add_to_path = False
            for next_node,next_route,next_dist in prev_dict[node]:
                ## if the routes match, accept this node
                if next_route == route:
                    ## Check for precomputed paths
                    if (source, next_node, next_route) in precomputed_paths:
                        for precomp_path in precomputed_paths[(source, next_node, next_route)]:
                            save_path = list(curr_path)
                            save_path.reverse()
                            save_path = list(precomp_path) + [node] + save_path
                            shortest_paths[(source, start_node)].add(tuple(save_path))
                    else:
                        stack.append((next_node, next_route, next_dist, node))
                        add_to_path = True

                ## If the routes don't match, only accept if the distance
                ## from the next node is 1 less than the current, meaning we are
                ## changing routes in a move _towards_ the source
                elif next_route != route and next_dist == (dist - 1):
                    ## Check for precomputed paths
                    if (source, next_node, next_route) in precomputed_paths:
                        for precomp_path in precomputed_paths[(source, next_node, next_route)]:
                            save_path = list(curr_path)
                            save_path.reverse()
                            save_path = list(precomp_path) + [node] + save_path
                            shortest_paths[(source, start_node)].add(tuple(save_path))
                    else:
                        stack.append((next_node, next_route, next_dist, node))
                        add_to_path = True

            ## Actually add the node to the path
            if add_to_path:
                curr_path.append(node)


def all_shortest_paths(G, routes):
    shortest_paths = defaultdict(set)
    precomputed_paths = defaultdict(set)
    for source in G.nodes():
        distances, prev_dict = route_dijkstra(G, source, len(routes))
        for target in prev_dict:
            ## If there is an edge between them, that is the only path we
            ## are interested in
            if G.has_edge(source,target):
                shortest_paths[(source,target)].add(tuple([source, target]))
            else:
                reverse_paths(prev_dict, shortest_paths, target, source, precomputed_paths)

    return shortest_paths
