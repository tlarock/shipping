import pickle
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter


def get_xy(dist, normed=False):
    counter = Counter(dist)
    x=[];y=[]
    for xval in sorted(counter.keys()):
        x.append(xval)
        y.append(counter[xval])
    y = np.array(y)
    if normed:
        y = y/y.sum()
    return x, y

print("Reading shipping distances.")
shipping_dist = dict()
with open('/home/larock.t/git/shipping/data/port_shipping_distances.csv', 'r') as fin:
    for line in fin:
        u,v,dist = line.strip().split(',')
        shipping_dist[(u,v)] = float(dist)

print("Computing filtered path stats.")
scratch_base = '/scratch/larock.t/shipping/results/interpolated_paths/'
## Filtered paths
num_paths_dist_mr_filt = [] ## list of ints
route_lengths_per_pair_mr_filt = [] ## list of ints (should be all 1s)
route_lengths_dist_mr_filt = [] ## list of ints
path_lengths_dist_mr_filt = []
routes_per_path_dist_filt = []
routes_per_path_dist = []
filtered_paths = dict()
filtered_distances = []
with open(scratch_base + 'iterative_paths_with_routes_filtered_dt-1.5_rt-1.0.txt', 'r') as fin:
    pair_counter = 0
    total_pairs = 0
    prev_pair = (-1,-1)
    first = True
    for line in fin:
        path, mr_dist, route_dist, *routes = line.strip().split('|')
        routes_per_path_dist.append(len(routes))
        path = path.strip().split(',')
        dist = int(mr_dist)
        pair = (path[0], path[-1])
        filtered_paths.setdefault(pair, dict())
        filtered_paths[pair][tuple(path[0:len(path)-1])] = dist
        filtered_distances.append(float(route_dist))
        if pair != prev_pair and not first:
            num_paths = len(filtered_paths[prev_pair])
            num_paths_dist_mr_filt.append(num_paths)
            route_lengths = [p for p in filtered_paths[prev_pair].values()]
            route_lengths_dist_mr_filt += route_lengths
            route_lengths_per_pair_mr_filt.append(len(set(route_lengths)))
            path_lengths = [len(p)-1 for p in filtered_paths[prev_pair].keys()]
            path_lengths_dist_mr_filt +=  path_lengths 
            pair_counter += 1
            total_pairs += 1
            if pair_counter == 50_000:
                print(f"{total_pairs} pairs processed.", flush=True)
                pair_counter = 0

        prev_pair = pair

        if first: first = False

import pickle
with open(scratch_base + 'iterative_paths_with_routes_stats.pickle', 'wb') as fpickle:
    pickle.dump((num_paths_dist_mr_filt, route_lengths_dist_mr_filt, route_lengths_per_pair_mr_filt, path_lengths_dist_mr_filt, routes_per_path_dist), fpickle)

print("Computing clique path stats.")
## Clique paths
with open(scratch_base + 'shortest_paths_clique.pickle', 'rb') as fpickle:
    paper_paths_dict = pickle.load(fpickle)
gwdata = pd.read_csv('../data/original/Nodes_2015_country_degree_bc_B_Z_P.csv', encoding='latin-1' ) ## Just need to get id to name mapping
port_mapping = dict(zip(gwdata.id.values,gwdata.port.values))
with open(scratch_base + 'clique_minroute_paths.pickle', 'rb') as fpickle:
    minimum_routes_sp = pickle.load(fpickle)
num_paths_dist_cg = [] ## list of ints
route_lengths_per_pair_cg = [] ## list of ints (should be all 1s)
route_lengths_dist_cg = [] ## list of intes
path_lengths_dist_cg = []
for pair in paper_paths_dict:
    num_paths = len(paper_paths_dict[pair])
    num_paths_dist_cg.append(num_paths)
    mpair = (port_mapping[pair[0]], port_mapping[pair[1]])
    if mpair in minimum_routes_sp:
        route_lengths = [p for p in minimum_routes_sp[mpair].values()]
        route_lengths_dist_cg += route_lengths
        route_lengths_per_pair_cg.append(len(set(route_lengths)))
    #path_lengths = [len(p) for p in paper_paths_dict[pair]]
    #path_lengths = [len(next(iter(paper_paths_dict[pair])))-1]
    path_lengths = [len(p)-1 for p in paper_paths_dict[pair]]
    path_lengths_dist_cg +=  path_lengths

clique_distances =  []
for pair in minimum_routes_sp:
    for path in minimum_routes_sp[pair]:
        if path not in filtered_paths[pair]:
            continue
        ## Real distance
        d = 0.0
        for i in range(1, len(path)):
            d += shipping_dist[path[i-1], path[i]]
        clique_distances.append(d)

## Path graph paths
print("Computing path path stats.")
with open(scratch_base + 'shortest_paths_pathrep.pickle', 'rb') as fpickle:
    pg_paths = pickle.load(fpickle)
with open(scratch_base + 'sp_pathrep_minroutes.pickle', 'rb') as fpickle:
    minimum_routes = pickle.load(fpickle)
num_paths_dist_pg = [] ## list of ints
route_lengths_per_pair_pg = [] ## list of ints (should be all 1s)
route_lengths_dist_pg = [] ## list of intes
path_lengths_dist_pg = []
for pair in pg_paths:
    num_paths = len(pg_paths[pair])
    num_paths_dist_pg.append(num_paths)
    route_lengths = [p for p in minimum_routes[pair].values()]
    route_lengths_dist_pg += route_lengths
    route_lengths_per_pair_pg.append(len(set(route_lengths)))
    path_lengths = [len(p)-1 for p in pg_paths[pair]]
    path_lengths_dist_pg +=  path_lengths

pg_distances =  []
for pair in pg_paths:
    for path in pg_paths[pair]:
        ## Real distance
        d = 0.0
        for i in range(1, len(path)):
            d += shipping_dist[path[i-1], path[i]]
        pg_distances.append(d)


print("Dumping stats.")
with open(scratch_base + 'path_comparison_stats.pickle', 'wb') as fpickle:
    pickle.dump((path_lengths_dist_mr_filt, path_lengths_dist_pg, path_lengths_dist_cg, filtered_distances, pg_distances, clique_distances, route_lengths_dist_mr_filt, route_lengths_dist_pg, route_lengths_dist_cg), fpickle)
## PLOTTING CODE ##
nrows=1
ncols=3
w = 3.0; h = 2.5
fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*w*1.5, nrows*h), sharey=True, squeeze=True, dpi=150)
plt.subplots_adjust(wspace=0.125)
for normed in [True, False]:
    if normed:
        x, y = get_xy(path_lengths_dist_mr_filt, normed=normed)
        axs[0].plot(x, y, label=fr'Filtered', color='DodgerBlue', marker='o', markersize=3)


        x, y = get_xy(path_lengths_dist_pg, normed=normed)
        axs[0].plot(x, y , label=fr'Path-graph', color='orange', marker='x', mfc='none', markersize=3)

        x, y = get_xy(path_lengths_dist_cg, normed=normed)
        axs[0].plot(x, y, label=fr'Clique-graph', color='purple', marker='^', mfc='none', markersize=3)

        axs[0].set_ylabel("Normalized Frequency")
        axs[0].set_xticks([i for i in range(0, 51, 10)])
        axs[0].set_xlabel("Path Length (edges)")
        axs[0].legend(fontsize=9, ncol=3, bbox_to_anchor=[0.79,-0.3], loc=2, framealpha=0)
        axs[0].text(0, 1.02, '(a)', transform=axs[0].transAxes, fontsize='large', ha='left', va='bottom', fontweight='bold')
        axs[0].set_yticks([0, 0.25, 0.5])
        axs[0].set_ylim(-0.02, 0.59)
    else:
        axi = axs[0].inset_axes([0.5,0.6,0.475,0.375])
        x, y = get_xy(path_lengths_dist_mr_filt, normed=normed)
        axi.plot(x, y, color='DodgerBlue', marker='^', mfc='none', markersize=3)
        x, y = get_xy(path_lengths_dist_pg, normed=normed)
        axi.plot(x, y, color='Orange', marker='^', mfc='none', markersize=3)
        x, y = get_xy(path_lengths_dist_cg, normed=normed)
        axi.plot(x, y, color='purple', marker='^', mfc='none', markersize=3)
        axi.set_xticks([0, 25, 50])
        axi.set_xticklabels(['0','25','50'], fontsize='small')
        axi.set_yticks([0, 10_000_000])
        axi.set_yticklabels(['0','10m'], fontsize='small')

######## route shipping distances ########
for normed in [True, False]:
    if normed:
        hist,bin_edges = np.histogram(filtered_distances, bins=25)
        hist = hist/hist.sum()
        axs[1].plot(((bin_edges[:-1] + bin_edges[1:])/2.)[hist>0], hist[hist>0], color='DodgerBlue', marker='o', markersize=3)

        hist,bin_edges = np.histogram(pg_distances, bins=bin_edges)
        hist = hist/hist.sum()
        axs[1].plot(((bin_edges[:-1] + bin_edges[1:])/2.)[hist>0], hist[hist>0], color='orange', marker='x', mfc='none', markersize=3)

        hist,bin_edges = np.histogram(clique_distances, bins=bin_edges, density=normed)
        hist = hist/hist.sum()
#         axs[1].set_ylabel("Normalized Frequency")
        axs[1].plot(((bin_edges[:-1] + bin_edges[1:])/2.)[hist>0], hist[hist>0], color='purple', marker='^', mfc='none', markersize=3)
        axs[1].set_xlabel("Route Distance (km)")
        xts = [0, 2.5e4, 5e4, 7.5e4, 1e5]
        xtl = ["%.0fk"%(i/1000) for i in xts]
        axs[1].set_xticks(xts)
        axs[1].set_xticklabels(xtl)
        axs[1].text(0, 1.02, '(b)', transform=axs[1].transAxes, fontsize='large', ha='left', va='bottom', fontweight='bold')
        axs[1].set_yticks([0, 0.25, 0.5])
        axs[1].set_ylim(-0.02, 0.59)
    else:
        axi = axs[1].inset_axes([0.5,0.6,0.475,0.375])
        hist,bin_edges = np.histogram(filtered_distances, bins=25)
        axi.plot(((bin_edges[:-1] + bin_edges[1:])/2.)[hist>0], hist[hist>0], color='DodgerBlue', marker='^', mfc='none', markersize=3)
        hist,bin_edges = np.histogram(pg_distances, bins=bin_edges)
        axi.plot(((bin_edges[:-1] + bin_edges[1:])/2.)[hist>0], hist[hist>0], color='Orange', marker='^', mfc='none', markersize=3)
        hist,bin_edges = np.histogram(clique_distances, bins=bin_edges, density=normed)
        axi.plot(((bin_edges[:-1] + bin_edges[1:])/2.)[hist>0], hist[hist>0], color='purple', marker='^', mfc='none', markersize=3)
        xts = [0, 50000, 100000]
        xtl = ["%.0fk"%(i/1000) for i in xts]
        axi.set_xticks(xts)
        axi.set_xticklabels(xtl, fontsize='small')
        axi.set_yticks([0, 5_000_000])
        axi.set_yticklabels(['0','5m'], fontsize='small')

######## number of routes ########
for normed in [True, False]:
    if normed:
        x, y = get_xy(route_lengths_dist_mr_filt, normed=normed)
        axs[2].plot(x, y, color='DodgerBlue', marker='o', markersize=3)

        x, y = get_xy(route_lengths_dist_pg, normed=normed)
        axs[2].plot(x, y, color='orange', marker='x', mfc='none', markersize=3)

        x, y = get_xy(route_lengths_dist_cg, normed=normed)
        axs[2].plot(x, y, color='purple', marker='^', mfc='none', markersize=3)
#         if normed:
#             axs[2].set_ylabel("Normalized Frequency")
#         else:
#             axs[2].set_ylabel("Frequency")
        axs[2].set_xticks(list(range(1, 11)))
        axs[2].set_xlabel("Number of Routes")
        axs[2].text(0, 1.02, '(c)', transform=axs[2].transAxes, fontsize='large', ha='left', va='bottom', fontweight='bold')
        axs[2].set_yticks([0, 0.25, 0.5])
        axs[2].set_ylim(-0.02, 0.59)
    else:
        axi = axs[2].inset_axes([0.5,0.6,0.475,0.375])
        x, y = get_xy(route_lengths_dist_mr_filt, normed=normed)
        axi.plot(x, y, color='DodgerBlue', marker='^', mfc='none', markersize=3)
        x, y = get_xy(route_lengths_dist_pg, normed=normed)
        axi.plot(x, y, color='Orange', marker='^', mfc='none', markersize=3)
        x, y = get_xy(route_lengths_dist_cg, normed=normed)
        axi.plot(x, y, color='purple', marker='^', mfc='none', markersize=3)
        axi.set_yticks([0, 2_000_000])
        axi.set_yticklabels(['0','2m'], fontsize='small')
        axi.set_xticks([0,5,10])
        axi.set_xticklabels([0,5,10], fontsize='small')

plt.savefig(scratch_base + 'filteredVScgVSpg.pdf', bbox_inches='tight')
