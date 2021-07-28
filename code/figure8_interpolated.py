import pandas as pd
import networkx as nx
import numpy as np


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

edgelist = set()
with open('../data/all_routes_2015.ngram', 'r') as fin:
    for line in fin:
        path = remove_selfloops(line.strip().split(','))
        for idx in range(1, len(path)-1):
            edgelist.add((path[idx-1], path[idx]))
print("Read edgelist.", flush=True)


distance_thresh = 1.0
interpolated_paths_dict = dict()
num_paths = 0
#with open(f'../results/interpolated_paths/iterative_paths_with_routes_filtered_dt-{distance_thresh}_rt-1.0.txt', 'r') as fin:
with open(f'../results/interpolated_paths/iterative_paths_with_routes.txt', 'r') as fin:
    for line in fin:
        path, mr_dist, rt_dist, *_ = line.strip().split('|')
        path = path.strip().split(',')
        dist = int(mr_dist)
        interpolated_paths_dict.setdefault((path[0], path[-1]), dict())
        interpolated_paths_dict[(path[0], path[-1])][tuple(path)] = dist
        num_paths += 1

print("Read paths.", flush=True)

paper_B = True
gwdata = pd.read_csv('../data/original/Nodes_2015_country_degree_bc_B_Z_P.csv', encoding='latin-1' )
if paper_B:
    B = dict(zip(gwdata.port,gwdata.B.values)) ## Gatewayness
    num_sc = 37
    core_ports = sorted(B.items(), key=lambda kv:kv[1], reverse=True)[0:num_sc]
    core_ports = [name for name,_ in core_ports]
    non_core_ports = [port for port in B if port not in core_ports]
else:
    import pickle
    with open("../results/structural_core_nodes.pickle", 'rb') as fpickle:
        core_ports = pickle.load(fpickle)
    num_sc = 49
    non_core_ports = [port for port in gwdata.port if port not in core_ports]

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
        distances[(u,v)] = dist

print("Loaded distances.", flush=True)

## Figure 8b
core_links = in_feeder_links = out_feeder_links = local_links = 0
core_lengths = in_feeder_lengths = out_feeder_lengths = local_lengths = 0
for e in edgelist:
    if e[0] in core_ports_set and e[1] in core_ports_set:
        core_links += 1
        core_lengths += distances[e]
    elif (e[0] in non_core_set) and (e[1] in non_core_set):
        local_links += 1
        local_lengths += distances[e]
    elif (e[0] in core_ports_set) and (e[1] in non_core_set):
        out_feeder_links += 1
        out_feeder_lengths += distances[e]
    elif (e[0] in non_core_set) and (e[1] in core_ports_set):
        in_feeder_links += 1
        in_feeder_lengths += distances[e]

total_links = core_links + local_links + in_feeder_links + out_feeder_links
assert total_links == len(edgelist), 'what'
total_lengths = core_lengths + local_lengths + in_feeder_lengths + out_feeder_lengths


core_vals = ((core_links / total_links)*100, (core_lengths / total_lengths)*100)
print("core: ", core_vals, " ", core_vals[1]/core_vals[0])
in_feeder_vals = ((in_feeder_links / total_links)*100, (in_feeder_lengths / total_lengths)*100)
print("in_feeder: ", in_feeder_vals, " ", in_feeder_vals[1]/in_feeder_vals[0])
out_feeder_vals = ((out_feeder_links / total_links)*100, (out_feeder_lengths / total_lengths)*100)
print("in_feeder: ", out_feeder_vals, " ", out_feeder_vals[1]/out_feeder_vals[0])
local_vals = ((local_links / total_links)*100, (local_lengths / total_lengths)*100)
print("local: ", local_vals, " ", local_vals[1]/local_vals[0])

core_vals_8b = tuple(core_vals)
in_feeder_vals_8b = tuple(in_feeder_vals)
out_feeder_vals_8b = tuple(out_feeder_vals)
local_vals_8b = tuple(local_vals)

print("Computed figure 8b stats.", flush=True)

total_clengths = total_llengths = total_inflengths = total_outflengths = 0
thru_core_clengths = thru_core_llengths = thru_core_inflengths = thru_core_outflengths = 0
number_no_paths = 0
num_paths = 0
for (s,t) in interpolated_paths_dict:
        ## Only want paths between *non-core* ports
        if s in core_ports or t in core_ports:
            number_no_paths +=1
            continue

        num_paths += 1
        curr_paths = interpolated_paths_dict[(s,t)]

        for path in curr_paths:
            core_lengths = in_feeder_lengths = out_feeder_lengths = local_lengths = 0
            for i in range(1, len(path)):
                e = path[i-1], path[i]
                if (e[0] in core_ports_set) and (e[1] in core_ports_set):
                    core_links += 1
                    core_lengths += distances[e]
                elif (e[0] in non_core_set) and (e[1] in non_core_set):
                    local_links += 1
                    local_lengths += distances[e]
                elif (e[0] in core_ports_set) and (e[1] in non_core_set):
                    out_feeder_links += 1
                    out_feeder_lengths += distances[e]
                elif (e[0] in non_core_set) and (e[1] in core_ports_set):
                    in_feeder_links += 1
                    in_feeder_lengths += distances[e]

            ## Length sums
            total_clengths += core_lengths
            total_llengths += local_lengths
            total_inflengths += in_feeder_lengths
            total_outflengths += out_feeder_lengths
            if core_lengths > 0:
                ## Length sums
                thru_core_clengths += core_lengths
                thru_core_llengths += local_lengths
                thru_core_inflengths += in_feeder_lengths
                thru_core_outflengths += out_feeder_lengths

## Totals
total_lengths = total_clengths + total_inflengths  + total_outflengths + total_llengths
## thru_core
total_thrucore_lengths = thru_core_clengths + thru_core_inflengths + thru_core_outflengths + thru_core_llengths

core_vals = ((total_clengths / total_lengths)*100, \
             core_vals_8b[0], \
             (thru_core_clengths / total_thrucore_lengths)*100)
print("core: ", core_vals, " total/corelinks", core_vals[0]/core_vals_8b[0], " thrucore/corelinks", core_vals[2]/core_vals_8b[0])

in_feeder_vals = ((total_inflengths / total_lengths)*100, \
               in_feeder_vals_8b[0], \
               (thru_core_inflengths / total_thrucore_lengths)*100)
print("feeder: ", in_feeder_vals, " total/corelinks", in_feeder_vals[0]/in_feeder_vals_8b[0], " thrucore/corelinks", in_feeder_vals[2]/in_feeder_vals_8b[0])

out_feeder_vals = ((total_outflengths / total_lengths)*100, \
               out_feeder_vals_8b[0], \
               (thru_core_outflengths / total_thrucore_lengths)*100)
print("feeder: ", out_feeder_vals, " total/corelinks", out_feeder_vals[0]/out_feeder_vals_8b[0], " thrucore/corelinks", out_feeder_vals[2]/out_feeder_vals_8b[0])


local_vals = ((total_llengths / total_lengths)*100, \
              local_vals_8b[0], \
              (thru_core_llengths / total_thrucore_lengths)*100)
print("local: ", local_vals, " total/corelinks", local_vals[0]/local_vals_8b[0], " thrucore/corelinks", local_vals[2]/local_vals_8b[0])

local_vals = tuple([local_vals[0], local_vals[2]])
in_feeder_vals = tuple([in_feeder_vals[0], in_feeder_vals[2]])
out_feeder_vals = tuple([out_feeder_vals[0], out_feeder_vals[2]])
core_vals = tuple([core_vals[0], core_vals[2]])

print("Computed figure 8c stats.", flush=True)

plot_vals = {
    'local': local_vals_8b + local_vals,
    'in-feeder': in_feeder_vals_8b + in_feeder_vals,
    'out-feeder': out_feeder_vals_8b + out_feeder_vals,
    'core': core_vals_8b + core_vals
}

import pickle
print("Dumping stats.", flush=True)
with open(f'../results/interpolated_paths/core_plot_vals_allpaths.pickle', 'wb') as fpickle:
    pickle.dump(plot_vals, fpickle)
