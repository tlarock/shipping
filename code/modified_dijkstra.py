from collections import defaultdict
from heappq import HeapPQ

def route_dijkstra(G, source):
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
                        nxt_route in [pr for _,pr,_ in prev[node]]:
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
    path = [target]
    stack = list()
    for prev_node, route, d in prev[target]:
        #print(f'0. Added to stack: {(prev_node, route, d, 1, target)}')
        stack.append((prev_node, route, d, 1, target))

    while stack:
        curr_node, curr_route, curr_d, total_d, last_node = stack.pop()

        if curr_node in path:
            continue

        if path[0] != curr_node:
            path = path[path.index(last_node):]

        path = [curr_node] + path
        for prev_node, prev_route, prev_d in prev[curr_node]:
            if prev_node == source:
                ## Case 1: We found the source. Save the path.
                path = [source] + path
                if (prev_d == curr_d and curr_route == prev_route):
                    shortest_paths[(source,target)][tuple(path)] = total_d
                elif (prev_d == curr_d-1 and curr_route != prev_route):
                    shortest_paths[(source,target)][tuple(path)] = total_d+1

                path = path[path.index(curr_node):]
            elif (prev_d == curr_d and curr_route == prev_route):
                ## Case 2: The next route continues the same route.
                stack.append((prev_node, prev_route, prev_d, total_d, curr_node))
            elif (prev_d == curr_d-1 and curr_route != prev_route):
                ## Case 3: The next route represents a transfer
                stack.append((prev_node, prev_route, prev_d, total_d+1, curr_node))

def all_shortest_paths(G):
    shortest_paths = defaultdict(dict)
    for source in G.nodes():
        distances, prev_dict = route_dijkstra(G, source)
        for target in prev_dict:
            ## If there is an edge between them, that is the only path we
            ## are interested in
            if G.has_edge(source,target):
                shortest_paths[(source,target)][tuple([source, target])] = 1
            else:
                reverse_paths(shortest_paths, prev_dict, source, target)

    return shortest_paths
