from filter_paths import *

distance_thresh = 1.5
redundancy_thresh = 1.0
shipping_dist = dict()
with open('../data/port_shipping_distances.csv', 'r') as fin:
    for line in fin:
        u,v,dist = line.strip().split(',')
        shipping_dist[(u,v)] = float(dist)

with open('/scratch/larock.t/shipping/results/interpolated_paths/iterative_paths.txt', 'r') as fin:
    filtered_paths = dict()
    pair_counter = 0
    total_pairs = 0
    prev_pair = (-1,-1)
    first = True
    for line in fin:
        a = line.strip().split(',')
        dist = int(a[-1])
        pair = (a[0], a[-2])
        filtered_paths.setdefault(pair, dict())
        filtered_paths[pair][tuple(a[0:len(a)-1])] = dist

        if pair != prev_pair and not first:
            if len(filtered_paths[prev_pair]) > 1:
                filter_distance(filtered_paths, prev_pair, shipping_dist, distance_thresh)
                filter_redundant(filtered_paths, prev_pair, redundancy_thresh)
            pair_counter += 1
            total_pairs += 1
            if pair_counter == 10_000:
                print(f"{total_pairs} processed.", flush=True)
                pair_counter = 0

        prev_pair = pair
        
        if first: first = False


with open('/scratch/larock.t/shipping/results/interpolated_paths/iterative_paths_filtered.txt', 'w') as fout:
    for pair in filtered_paths:
        for path in filtered_paths[pair]:
            fout.write(','.join(path) + ',' + str(filtered_paths[pair][path]) + '\n')        
