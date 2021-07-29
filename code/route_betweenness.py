import numpy as np
import networkx as nx


def route_node_betweenness_from_paths(G, filtered_paths):
    '''
    Computes route betweenness for nodes starting from set of paths filtered_paths.
    Uses G only to get the number of nodes; could be done by iterating
    over pairs of nodes in filtered_paths or given as input parameter.

    Uses dense numpy arrays for computations.
    '''
    ## Zero array of dimensions len(G.nodes()) by len(filtered_paths)
    node_to_idx = {node:idx for idx, node in enumerate(G.nodes())}
    pair_to_idx = {pair:idx for idx, pair in enumerate(filtered_paths.keys())}
    numerator = np.zeros((len(G.nodes()), len(filtered_paths)))
    denominator = []
    for pair in filtered_paths:
        denominator.append(len(filtered_paths[pair]))
        for path in filtered_paths[pair]:
            for node in path:
                numerator[node_to_idx[node], pair_to_idx[pair]] += 1

    denominator = np.array(denominator)
    normalized_counts = numerator / denominator
    total_betweenness = normalized_counts.sum(axis=1)
    route_betweenness = {node:total_betweenness[idx] for node, idx in node_to_idx.items()}
    return route_betweenness


def route_node_betweenness_from_file(filename):
    '''
    Computes route betweenness for nodes by reading file filename.

    Uses dictionaries for computations.
    '''

    pair_counter = 0
    total_pairs = 0
    first = True
    node_to_pair_dict = dict()
    prev_pair = (-1, -1)
    filtered_paths = dict()
    with open(filename, 'r') as fin:
        for line in fin:
            path, *_ = line.strip().split('|')
            path = path.strip().split(',')
            pair = (path[0], path[-1])
            filtered_paths.setdefault(pair, list())
            filtered_paths[pair].append(path)
            if pair != prev_pair and not first:
                nodes_to_norm = set()
                for path in filtered_paths[prev_pair]:
                    for node in path:
                        node_to_pair_dict.setdefault(node, dict())
                        node_to_pair_dict[node].setdefault(prev_pair, 0)
                        node_to_pair_dict[node][prev_pair] += 1
                        nodes_to_norm.add(node)
                ## Normalize
                for node in nodes_to_norm:
                    node_to_pair_dict[node][prev_pair] /= len(filtered_paths[prev_pair])
                pair_counter += 1
                total_pairs += 1
                if pair_counter == 150_000:
                    print(f"{total_pairs} processed.", flush=True)
                    pair_counter = 0

            prev_pair = pair
            if first: first = False

    ## Handle the last pair
    for path in filtered_paths[prev_pair]:
        nodes_to_norm = set()
        for node in path:
            node_to_pair_dict.setdefault(node, dict())
            node_to_pair_dict[node].setdefault(prev_pair, 0)
            node_to_pair_dict[node][prev_pair] += 1
            nodes_to_norm.add(node)
    ## Normalize
    for node in nodes_to_norm:
        node_to_pair_dict[node][prev_pair] /= len(filtered_paths[prev_pair])

    ## Compute betweenness by summing over all pairs for each node
    route_betweenness = {node:sum(node_to_pair_dict[node].values()) for node in node_to_pair_dict}
    return route_betweenness

def route_edge_betweenness_from_paths(G, filtered_paths):
    '''
    Computes route betweenness for edges starting from set of paths filtered_paths.
    Uses G only to get the number of nodes; could be done by iterating
    over pairs of nodes in filtered_paths or given as input parameter.

    Uses dense numpy arrays for computations.

    '''
    ## Zero array of dimensions len(G.edges()) by len(filtered_paths)
    edge_to_idx = {edge:idx for idx, edge in enumerate(G.edges())}
    pair_to_idx = {pair:idx for idx, pair in enumerate(filtered_paths.keys())}
    numerator = np.zeros((len(G.edges()), len(filtered_paths)))
    denominator = []
    for pair in filtered_paths:
        denominator.append(len(filtered_paths[pair]))
        for path in filtered_paths[pair]:
            for i in range(1, len(path)):
                numerator[edge_to_idx[(path[i-1], path[i])], pair_to_idx[pair]] += 1

    denominator = np.array(denominator)
    normalized_counts = numerator / denominator
    total_betweenness = normalized_counts.sum(axis=1)
    route_betweenness = {edge:total_betweenness[idx] for edge, idx in edge_to_idx.items()}
    return route_betweenness


def route_edge_betweenness_from_file(filename):
    '''
    Computes route betweenness for edges by reading file filename.

    Uses dictionaries for computations.
    '''
    pair_counter = 0
    total_pairs = 0
    first = True
    edge_to_pair_dict = dict()
    prev_pair = (-1, -1)
    filtered_paths = dict()
    with open(filename, 'r') as fin:
        for line in fin:
            path, *_ = line.strip().split('|')
            path = path.strip().split(',')
            pair = (path[0], path[-1])
            filtered_paths.setdefault(pair, list())
            filtered_paths[pair].append(path)
            if pair != prev_pair and not first:
                edges_to_norm = set()
                for path in filtered_paths[prev_pair]:
                    for i in range(1, len(path)):
                        edge = path[i-1], path[i]
                        edge_to_pair_dict.setdefault(edge, dict())
                        edge_to_pair_dict[edge].setdefault(prev_pair, 0)
                        edge_to_pair_dict[edge][prev_pair] += 1
                        edges_to_norm.add(edge)
                ## Normalize
                for edge in edges_to_norm:
                    edge_to_pair_dict[edge][prev_pair] /= len(filtered_paths[prev_pair])
                pair_counter += 1
                total_pairs += 1
                if pair_counter == 150_000:
                    print(f"{total_pairs} processed.", flush=True)
                    pair_counter = 0

            prev_pair = pair
            if first: first = False

    ## Handle the last pair
    for path in filtered_paths[prev_pair]:
        edges_to_norm = set()
        for i in range(1, len(path)):
            edge = path[i-1], path[i]
            edge_to_pair_dict.setdefault(edge, dict())
            edge_to_pair_dict[edge].setdefault(prev_pair, 0)
            edge_to_pair_dict[edge][prev_pair] += 1
            edges_to_norm.add(edge)

    ## Normalize
    for edge in edges_to_norm:
        edge_to_pair_dict[edge][prev_pair] /= len(filtered_paths[prev_pair])

    ## Compute betweenness by summing over all pairs for each edge
    route_betweenness = {edge:sum(edge_to_pair_dict[edge].values()) for edge in edge_to_pair_dict}
    return route_betweenness
