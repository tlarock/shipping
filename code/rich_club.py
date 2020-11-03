import numpy as np
import pathpy as pp


def rich_club(hy):
    # Given: A hypa.Hypa instance
    # Output: Rich-club coefficient for every degree

    ## For each node, assign it to its degree
    nodes_by_degree = dict()
    node_to_name_map = hy.hypa_net.node_to_name_map()
    reverse_name_map = {name:node for node, name in node_to_name_map.items()}
    degrees = hy.hypa_net.degrees(mode='degree')  ## Use total degree (undirected)
    for i, deg in enumerate(degrees):
        nodes_by_degree.setdefault(deg, list())
        nodes_by_degree[deg].append(reverse_name_map[i])

    ## For each degree, calculate rich-club
    degrees_list = sorted(list(nodes_by_degree.keys()))
    phi = dict()
    for i in range(max(degrees_list)+1):
        nodes_above_k = []
        for j in range(i, max(degrees_list)+1):
            if j in degrees_list:
                ## Count the actual edges among the nodes
                ## since the graph is directed, we need a doubly nested loop to check for all edges
                nodes_above_k += nodes_by_degree[j]

        existing_edges = set()
        for node1 in nodes_above_k:
            for node2 in nodes_above_k:
                if node1 != node2:
                    ## orient edges min --> max in the set to avoid duplicates
                    if (node1, node2) in hy.hypa_net.edges:
                        existing_edges.add((min(node1, node2), max(node1,node2)))

        if len(nodes_above_k) > 1:
            possible_edges = len(nodes_above_k) * (len(nodes_above_k)-1)
            phi[i] = (2*len(existing_edges)) / possible_edges
        else:
            ## If there is only 1 node above the degree,
            ## there is not anything to compute here or at higher degrees
            break

    return phi
