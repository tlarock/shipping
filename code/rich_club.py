import numpy as np
import pathpy as pp
from hypa import Hypa
from random import shuffle

def rich_club(hy, normalized=False, degree_type='degree'):
    # Given: A hypa.Hypa instance
    # Output: Rich-club coefficient for every degree
    ## For now, I will allow passing either a pp.Network object
    ## OR a hypa.Hypa object
    if isinstance(hy, Hypa):
        network = hy.hypa_net
        hy_obj = True
    elif isinstance(hy, pp.Network):
        network = hy
        hy_obj = False
    else:
        print("Need either a hypa.Hypa or a pathpy.Network() object.")

    ## For each node, assign it to its degree
    nodes_by_degree = dict()
    node_to_name_map = network.node_to_name_map()
    reverse_name_map = {name:node for node, name in node_to_name_map.items()}
    degrees = get_degree(network, degree_type=degree_type) ## Use total degree (undirected)

    for i, deg in enumerate(degrees):
        nodes_by_degree.setdefault(deg, list())
        nodes_by_degree[deg].append(reverse_name_map[i])

    ## For each degree, calculate rich-club
    degrees_list = sorted(list(nodes_by_degree.keys()))
    phi = dict()
    #print("Phi in rich_club")
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
                    if (node1, node2) in network.edges:
                        existing_edges.add((min(node1, node2), max(node1,node2)))

        if len(nodes_above_k) > 1:
            possible_edges = len(nodes_above_k) * (len(nodes_above_k)-1)
            phi[i] = (2*len(existing_edges)) / possible_edges
            #print(i, len(existing_edges), possible_edges/2, phi[i])
        else:
            ## If there is only 1 node above the degree,
            ## there is not anything to compute here or at higher degrees
            break

    if normalized:
        if hy_obj:
            phi = normalize(hy, phi, degree_type)
        else:
            print("You must pass a Hypa object, not pp.Network, for normalization.")

    return phi

def normalize(hy, phi, degree_type, bad_swap_lim=100):
    num_edges = len(hy.hypa_net.edges)
    rnd_net = swap_edges(hy, num_swaps=num_edges, bad_swap_lim=num_edges)
    if degree_type == 'degree':
        phi_rnd = rich_club(rnd_net, normalized=False, degree_type='degree')

    for deg in phi:
        ## Normalize
        phi[deg] = phi[deg] / phi_rnd[deg]

    return phi

def get_degree(network, degree_type='degree'):
    if degree_type == 'degree':
        degrees = network.degrees(mode='degree')
    elif degree_type == 'sample_degree':
        degrees = []
        node_to_name_map = network.node_to_name_map()
        for node in node_to_name_map:
            degree = 0
            counted_edges = set()
            for neighbor in network.successors[node]:
                if network.edges[(node, neighbor)]['sampled_weight'] > 0:
                    degree += 1
                    counted_edges.add((node, neighbor))
            for neighbor in network.predecessors[node]:
                if (node, neighbor) in counted_edges:
                    continue ## Already counted this edge (assuming undirected)
                if network.edges[(neighbor, node)]['sampled_weight'] > 0:
                    degree += 1

            degrees.append(int(degree))
    elif degree_type == 'weight':
        weights = []
        node_to_name_map = network.node_to_name_map()
        for node in node_to_name_map:
            weight = 0
            for neighbor in network.successors[node]:
                weight += network.edges[(node, neighbor)]['weight']
            for neighbor in network.predecessors[node]:
                weight += network.edges[(neighbor, node)]['weight']
            weights.append(int(weight))
        degrees = weights

    return degrees

def swap_edges(hy, num_swaps, bad_swap_lim=100):
    new_network = pp.Network(directed=False)
    edges = [edge for edge, data in hy.hypa_net.edges.items() if 'weight' in data and data['weight'] > 0]
    shuffle(edges)
    swaps = 0
    bad_swaps = 0
    while swaps < num_swaps and edges:
        shuffle(edges)
        edge = edges[-1]
        if len(edges) == 1:
            new_network.add_edge(edge[0], edge[1])
            break

        ## Choose a random edge to swap
        edge_num = np.random.choice(len(edges)-1)
        swap_edge = edges[edge_num]

        ## Check if this is a good pair of edges to swap
        if (edge[0] == swap_edge[0] or edge[1] == swap_edge[1]) or \
           ((edge[0], swap_edge[1]) in new_network.edges or (swap_edge[0], edge[1]) in new_network.edges):
            bad_swaps += 1
            if bad_swaps == bad_swap_lim:
                print("Reached bad swap limit before finished swapping. Returning.")
                return new_network

        ## Create new edges
        new_network.add_edge(edge[0], swap_edge[1])
        new_network.add_edge(swap_edge[0], edge[1])

        edges.remove(edge)
        edges.remove(swap_edge)

        ## Success!
        swaps += 1

    return new_network
