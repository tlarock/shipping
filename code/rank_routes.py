scratch_base = '/scratch/larock.t/shipping/results/interpolated_paths/'
#scratch_base = '../results/interpolated_paths/'
with open(scratch_base + 'iterative_paths.txt', 'r') as fin:
    route_counts = {'weighted':dict(), 'unweighted':dict()}
    pair = (-1,-1)
    prev_pair = None
    pair_counter = 0
    total_pairs = 0
    for line in fin:
        path, mr_dist, route_dist, *routes = line.strip().split('|')
        list_routes = []
        for route in routes:
            list_routes.append(route.split(','))
            for rt_str in route.split(','):
                try:
                    rt, num = rt_str.split(':')
                    route_counts['unweighted'].setdefault(rt, 0)
                    route_counts['weighted'].setdefault(rt, 0)
                    route_counts['unweighted'][rt] += 1
                    route_counts['weighted'][rt] += int(num)
                except Exception as e:
                    print(f'{rt_str} was not succesfully parsed.', flush=True)
                    continue

        pair = path[0], path[-1]
        if pair != prev_pair:
            pair_counter += 1
            total_pairs += 1
            if pair_counter == 50_000:
                print(total_pairs, flush=True)
                pair_counter = 0
        prev_pair = pair

import pickle
with open('../results/route_counts.pickle', 'wb') as fpickle:
    pickle.dump(route_counts, fpickle)
