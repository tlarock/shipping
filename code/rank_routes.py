import sys
from iterative_minroutes import write_filtered

args = sys.argv

redundancy_thresh = 1.0
#scratch_base = '/scratch/larock.t/shipping/results/interpolated_paths/'
scratch_base = '../results/interpolated_paths/'
with open(scratch_base + 'iterative_paths.txt', 'r') as fin:
    route_counts = {'weighted':dict(), 'counts':dict()}
    pair_counter = 0
    total_pairs = 0
    first = True
    for line in fin:
        path, mr_dist, route_dist, *routes = line.strip().split('|')
        list_routes = []
        for route in routes:
            list_routes.append(route.split(','))
            for rt_str in route.split(','):
                try:
                    rt, num = rt_str.split(':')
                    route_counts['counts'].setdefault(rt, 0)
                    route_counts['weighted'].setdefault(rt, 0)
                    route_counts['counts'][rt] += 1
                    route_counts['weighted'][rt] += int(num)
                except Exception as e:
                    print(f'{rt_str} was not succesfully parsed.')
                    continue

        pair_counter += 1
        total_pairs += 1
        if pair_counter == 50_000:
            print(total_pairs)
            pair_counter = 0

import pickle
with open('../results/route_counts.pickle', 'wb') as fpickle:
    pickle.dump(route_counts, fpickle)
