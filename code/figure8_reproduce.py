import sys
import pickle
import pandas as pd
import networkx as nx
import numpy as np
from create_edgelist import *

# Read shortest paths
print("Reading shortest_paths_clique.pickle")
with open("../results/interpolated_paths/shortest_paths_clique.pickle", 'rb') as fpickle:
    shortest_paths = pickle.load(fpickle)
print("Done")
gwdata = pd.read_csv('../data/original/Nodes_2015_country_degree_bc_B_Z_P.csv', encoding='latin-1' )
B = dict(zip(gwdata.id,gwdata.B.values)) ## Gatewayness
num_sc = 37
core_ports = sorted(B.items(), key=lambda kv:kv[1], reverse=True)[0:num_sc]
core_ports = [name for name,_ in core_ports]
non_core_ports = [port for port in B if port not in core_ports]

print("Loaded B.", flush=True)
core_ports_set = set(core_ports)
non_core_set = set(non_core_ports)

distances = dict()
ddf = pd.read_csv('../data/port_shipping_distances.csv', names=['u','v','dist']) ## Distances Data Frame
port_mapping = dict(zip(gwdata.id.values,gwdata.port.values))
rev_map = {val:key for key,val in port_mapping.items()}
with open('../data/port_shipping_distances.csv', 'r') as fin:
    for line in fin:
        u,v,dist = line.strip().split(',')
        dist = float(dist)
        distances[(rev_map[u],rev_map[v])] = dist
print("Loaded distances.", flush=True)

G, G_map = read_network(network_type="clique")
G_rev = {value:key for key, value in G_map.items()}
edgelist = set()
for u,v in G.edges():
    edgelist.add((rev_map[G_rev[u]], rev_map[G_rev[v]]))

print("Read edgelist.", flush=True)

## Figure 8b
core_links = feeder_links = local_links = 0
core_lengths = feeder_lengths = feeder_lengths = local_lengths = 0
for e in edgelist:
    if e[0] in core_ports_set and e[1] in core_ports_set:
        core_links += 1
        core_lengths += distances[e]
    elif (e[0] in non_core_set) and (e[1] in non_core_set):
        local_links += 1
        local_lengths += distances[e]
    elif ((e[0] in core_ports_set) and (e[1] in non_core_set)) or \
            ((e[0] in non_core_set) and (e[1] in core_ports_set)):
        feeder_links += 1
        feeder_lengths += distances[e]

total_links = core_links + local_links + feeder_links

# ToDo: Add edgelist back to assert this
# assert total_links == len(edgelist), 'what'
total_lengths = core_lengths + local_lengths + feeder_lengths


core_vals = ((core_links / total_links)*100, (core_lengths / total_lengths)*100)
print("core: ", core_vals, " ", core_vals[1]/core_vals[0])
feeder_vals = ((feeder_links / total_links)*100, (feeder_lengths / total_lengths)*100)
print("feeder: ", feeder_vals, " ", feeder_vals[1]/feeder_vals[0])
local_vals = ((local_links / total_links)*100, (local_lengths / total_lengths)*100)
print("local: ", local_vals, " ", local_vals[1]/local_vals[0])

core_vals_8b = tuple(core_vals)
feeder_vals_8b = tuple(feeder_vals)
local_vals_8b = tuple(local_vals)

print("Computed figure 8b stats.", flush=True)

total_clengths = total_llengths = total_flengths = 0
thru_core_clengths = thru_core_llengths = thru_core_flengths = 0
number_no_paths = 0
num_paths = 0
for (s,t) in shortest_paths:
        ## Only want paths between *non-core* ports
        if s in core_ports or t in core_ports:
            number_no_paths +=1
            continue

        num_paths += 1
        curr_paths = shortest_paths[(s,t)]

        for path in curr_paths:
            core_lengths = feeder_lengths = local_lengths = 0
            for i in range(1, len(path)):
                e = path[i-1], path[i]
                if (e[0] in core_ports_set) and (e[1] in core_ports_set):
                    core_links += 1
                    core_lengths += distances[e]
                elif (e[0] in non_core_set) and (e[1] in non_core_set):
                    local_links += 1
                    local_lengths += distances[e]
                elif (e[0] in core_ports_set) and (e[1] in non_core_set) or ((e[0] in non_core_set) and (e[1] in core_ports_set)):
                    feeder_links += 1
                    feeder_lengths += distances[e]

            ## Length sums
            total_clengths += core_lengths
            total_llengths += local_lengths
            total_flengths += feeder_lengths
            if core_lengths > 0:
                ## Length sums
                thru_core_clengths += core_lengths
                thru_core_llengths += local_lengths
                thru_core_flengths += feeder_lengths

## Totals
total_lengths = total_clengths + total_flengths + total_llengths
## thru_core
total_thrucore_lengths = thru_core_clengths +  + thru_core_flengths + thru_core_llengths

core_vals = ((total_clengths / total_lengths)*100, \
             core_vals_8b[0], \
             (thru_core_clengths / total_thrucore_lengths)*100)
print("core: ", core_vals, " total/corelinks", core_vals[0]/core_vals_8b[0], " thrucore/corelinks", core_vals[2]/core_vals_8b[0])

feeder_vals = ((total_flengths / total_lengths)*100, \
               feeder_vals_8b[0], \
               (thru_core_flengths / total_thrucore_lengths)*100)
print("feeder: ", feeder_vals, " total/corelinks", feeder_vals[0]/feeder_vals_8b[0], " thrucore/corelinks", feeder_vals[2]/feeder_vals_8b[0])


local_vals = ((total_llengths / total_lengths)*100, \
              local_vals_8b[0], \
              (thru_core_llengths / total_thrucore_lengths)*100)
print("local: ", local_vals, " total/corelinks", local_vals[0]/local_vals_8b[0], " thrucore/corelinks", local_vals[2]/local_vals_8b[0])

local_vals = tuple([local_vals[0], local_vals[2]])
feeder_vals = tuple([feeder_vals[0], feeder_vals[2]])
core_vals = tuple([core_vals[0], core_vals[2]])

print("Computed figure 8c stats.", flush=True)

plot_vals = {
    'local': local_vals_8b + local_vals,
    'feeder': feeder_vals_8b + feeder_vals,
    'core': core_vals_8b + core_vals
}

import pickle
print("Dumping stats.", flush=True)
with open(f'../results/interpolated_paths/core_plot_vals_reproduce.pickle', 'wb') as fpickle:
    pickle.dump(plot_vals, fpickle)
