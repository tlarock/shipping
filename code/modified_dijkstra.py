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

def reverse_paths(prev_dict, start_node, source):
    '''
    Given the output of the modified dijkstra function,
    find all paths that use the minimum number of routes
    '''
    stack = []
    visited = set()
    for next_node, next_route, next_dist in prev_dict[start_node]:
        stack.append((next_node, next_route, next_dist, start_node))

    paths = set()
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
            paths.add(tuple(save_path))

            ## Reset path to continue reading stack
            curr_path = curr_path[0:-1]
        else:
            ## Should we add this node to the path?
            add_to_path = False
            for next_node,next_route,next_dist in prev_dict[node]:
                ## if the routes match, accept this node
                if next_route == route:
                    stack.append((next_node, next_route, next_dist, node))
                    add_to_path = True
                ## If the routes don't match, only accept if the distance
                ## from the next node is 1 less than the current, meaning we are
                ## changing routes in a move _towards_ the source
                elif next_route != route and next_dist == (dist - 1):
                    stack.append((next_node, next_route, next_dist, node))
                    add_to_path = True

            ## Actually add the node to the path
            if add_to_path:
                curr_path.append(node)

    return paths

def shortest_paths_from_prev(prev_dict, source):
    shortest_paths = defaultdict(set)
    for node in prev_dict:
        paths = reverse_paths(prev_dict, node, source)
        for path in paths:
            shortest_paths[node].add(path)

    return shortest_paths
