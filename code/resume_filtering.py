import sys
from file_read_backwards import FileReadBackwards
from iterative_minroutes import write_filtered

shipping_dist = dict()
distance_file = '../data/port_shipping_distances.csv'
#distance_file = '/home/larock.t/git/shipping/data/port_shipping_distances.csv'
with open(distance_file, 'r') as fin:
    for line in fin:
        u,v,dist = line.strip().split(',')
        shipping_dist[(u,v)] = float(dist)

distance_thresh = 'detour'
redundancy_thresh = 1.0
scratch_base = '/scratch/larock.t/shipping/results/interpolated_paths/'
## TODO Manually remove any incomplete pairs from files!
with FileReadBackwards(scratch_base + f'iterative_paths_with_routes_filtered_dt-{distance_thresh}_rt-{redundancy_thresh}_updated.txt') as frb:
    for line in frb:
        path, mr_dist, route_dist, *routes = line.strip().split('|')
        path = path.strip().split(',')
        dist = int(mr_dist)
        first_pair = (path[0], path[-1])
        break

filtered_paths = dict()
total_distances = dict()
with open(scratch_base + 'iterative_paths.txt', 'r') as fin:
    ## Skip to the correct line
    pair_found = False
    for line in fin:
        path, mr_dist, route_dist, *routes = line.strip().split('|')
        path = path.strip().split(',')
        dist = int(mr_dist)
        pair = (path[0], path[-1])
        if pair == first_pair:
            pair_found = True
        elif pair != first_pair and pair_found:
            ## Add this path, then break
            route_dist = float(route_dist)
            total_distances.setdefault(pair, dict())
            total_distances[pair][tuple(path)] = route_dist
            filtered_paths.setdefault(dist, dict())
            filtered_paths[dist].setdefault(pair[0], dict())
            filtered_paths[dist][pair[0]].setdefault(pair[1], dict())
            list_routes = []
            for route in routes:
                list_routes.append(route.split(','))
            filtered_paths[dist][pair[0]][pair[1]][tuple(path)] = list_routes
            break

    with open(scratch_base + f'iterative_paths_with_routes_filtered_dt-{distance_thresh}_rt-{redundancy_thresh}_updated.txt', 'a') as fout:
        ffilt = {distance_thresh:{redundancy_thresh:fout}}
        pair_counter = 0
        total_pairs = 0
        prev_pair = pair
        prev_dist = dist
        first = True
        for line in fin:
            path, mr_dist, route_dist, *routes = line.strip().split('|')
            path = path.strip().split(',')
            dist = int(mr_dist)
            pair = (path[0], path[-1])

            route_dist = float(route_dist)
            total_distances.setdefault(pair, dict())
            total_distances[pair][tuple(path)] = route_dist
            filtered_paths.setdefault(dist, dict())
            filtered_paths[dist].setdefault(pair[0], dict())
            filtered_paths[dist][pair[0]].setdefault(pair[1], dict())
            list_routes = []
            for route in routes:
                list_routes.append(route.split(','))
            filtered_paths[dist][pair[0]][pair[1]][tuple(path)] = list_routes

            if pair != prev_pair and not first:
                write_filtered(filtered_paths, prev_pair[0], prev_pair[1], total_distances[prev_pair], prev_dist, ffilt, [distance_thresh], shipping_dist[prev_pair])
                del filtered_paths[prev_dist][prev_pair[0]][prev_pair[1]]
                del total_distances[prev_pair]
                pair_counter += 1
                total_pairs += 1
                if pair_counter == 1000:
                    print(f"{total_pairs} processed.", flush=True)
                    pair_counter = 0

            prev_pair = pair
            prev_dist = dist
            if first: first = False

        ## Handle last pair
        write_filtered(filtered_paths, prev_pair[0], prev_pair[1], total_distances[prev_pair], prev_dist, ffilt, [distance_thresh], shipping_dist[prev_pair])

