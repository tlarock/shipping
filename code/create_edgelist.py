import sys
import networkx as nx

def remove_selfloops(path):
    i = 1
    end = len(path)
    while i < end:
        if path[i-1] == path[i]:
            del path[i-1]
            end-=1
        else:
            i+=1
    return path

## Construct the network using networkx
def read_network(network_type='directed'):
    def add_to_mapping(node, mapping, idx):
        if node not in mapping:
            mapping[node] = idx
            return idx+1
        return idx

    def add_edge(G, mapping, u, v):
        if not G.has_edge(mapping[u], mapping[v]):
            G.add_edge(mapping[u], mapping[v], weight=1)
        else:
            G.edges[(mapping[u], mapping[v])]['weight'] +=1

    assert network_type in ['directed', 'clique', 'coroute'], f'Network types are directed, clique, and coroute.'

    mapping = dict()
    idx = 0
    if network_type == 'directed' or network_type == 'coroute':
        G = nx.DiGraph()
    elif network_type == 'clique':
        G = nx.Graph()

    with open('../data/all_routes_2015.ngram', 'r') as infile:
        for line in infile:
            path = remove_selfloops(line.strip().split(","))
            if network_type == 'directed':
                for i in range(1, len(path)):
                    u,v = path[i-1],path[i]
                    if u != v:
                        idx = add_to_mapping(u, mapping, idx)
                        idx = add_to_mapping(v, mapping, idx)

                        add_edge(G, mapping, u, v)

            elif network_type == 'clique':
                nodes = set(path)
                for u in nodes:
                    for v in nodes:
                        if u != v:
                            idx = add_to_mapping(u, mapping, idx)
                            idx = add_to_mapping(v, mapping, idx)
                            add_edge(G, mapping, u,v)
            elif network_type == 'coroute':
                for i in range(len(path)):
                    if path[0] != path[-1]:
                        start = i+1
                    else:
                        start = 0
                    for j in range(start, len(path)):
                        u = path[i]
                        v = path[j]
                        if u != v:
                            idx = add_to_mapping(u, mapping, idx)
                            idx = add_to_mapping(v, mapping, idx)
                            add_edge(G, mapping, u,v)

    return G, mapping

def write_edgelist(G, mapping, filename):
    rev_map = {val:key for key,val in mapping.items()}
    with open(filename + '.edgelist', 'w') as fout:
        for tup in nx.generate_edgelist(G, delimiter=',', data=False):
            u, v = map(int, tup.strip().split(','))
            fout.write(f'{u},{v}\n')

    with open(filename + '.mapping', 'w') as fout:
        for node, idx in rev_map.items():
            fout.write(f'{node},{idx}\n')

if __name__ == '__main__':
    network_type = sys.argv[1]
    filename = sys.argv[2]

    G, mapping = read_network(network_type=network_type)

    write_edgelist(G, mapping, filename)


