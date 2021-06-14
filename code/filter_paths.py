def filter_paths(paths, shipping_dists, redundancy_thresh=0.5, distance_thresh=2.0):
    '''
    Accepts a paths defaultdict(dict), the result of all_shortest_paths(G),
    and removes (in-place) all paths between all pairs of nodes whose
    total route distance is distance_thresh times the minimum distances
    computed over all paths between the pair, then removes paths that are
    redundant based on overlap with shorter paths that are also minimum-route.


    Parameters
    ---------
    paths (defaultdict(dict)): A (potentially empty) defaultdict containing
                        all  minimum-routes paths from every source to every reahcable
                        target in G.
    shipping_dists (dict): A dictionary keyed by tuples of node pairs with value
                        corresponding to the shipping distance between the pair
                        of nodes.
    redundancy_thresh (float): A value between 0 and 1 that governs the filtering
                        of paths based on redundancy. A value of 1 means only paths
                        that are completely contained in shorter paths are removed.
                        A value of 0 means no paths are removed.
    distance_thresh (float): A value > 1 that indicates how permissive the distance
                        filtering should be. A value of 1.5 means paths will be accepted
                        if their total distance is 50% larger than the minimum for that
                        pair of source/target nodes.
    Side Effect
    -----------
    Modifies paths in-place, filtering paths. Prints every 50,000 pairs.
    '''

    ## Counters for convenience because this process can be slow
    pair_counter = 0
    total_pairs = 0
    for pair in paths:
        print(pair)
        ## If there is only 1 path, we have no choice
        if len(paths[pair]) == 1:
            continue

        ## By definition, this will always keep *at least* the
        ## path with the minimum total route distance
        filter_distance(paths, pair, shipping_dists, distance_thresh)

        ## By definition, this will always keep *at least* the
        ## shortest length path
        filter_redundant(paths, pair, redundancy_thresh)
        pair_counter += 1
        total_pairs += 1
        if pair_counter == 50_000:
            print(total_pairs)
            pair_counter = 0

def filter_distance(paths, pair, shipping_dists, distance_thresh):
    '''
    Accepts a paths defaultdict(dict), the result of all_shortest_paths(G),
    and removes (in-place) all paths between the nodes indicated by pair whose
    total route distance is more than distance_thresh times the minimum distance
    computed over all paths between the pair of source/target nodes.

    '''
    ## Compute the total distance for every path
    total_distances = dict()
    for path in paths[pair]:
        d_r = 0.0
        for i in range(1, len(path)):
            d_r += shipping_dists[path[i-1], path[i]]
        total_distances[path] = d_r

    min_dist = min(total_distances.values())
    for path in total_distances:
        if total_distances[path] > min_dist*distance_thresh:
            del paths[pair][path]

def filter_redundant(paths, pair, redundancy_thresh):
    '''
    Accepts a paths defaultdict(dict), the result of all_shortest_paths(G),
    and removes (in-place) all _redundant_  minimum-route paths between the
    nodes indicated by pair. A path is considered redundant if there is a
    shorter path that uses the minimum number of routes and a subset of
    the same nodes based on redundancy_thresh.

    For example, consider the following set of 3 routes:
        r1: A-B-C
        r2: B-C-D
        r3: B-D
    In these routes, both the path A-B-C-D and A-B-D connect A and D using
    2 routes (r1-r2 and r1-r3, respectively). We consider A-B-C-D redundant
    because A-B-D is shorter, overlapping, and uses the same number of routes.

    In contrast, consider adding the following routes to the first 3:
        r4: A-E-C
        r5: C-D
    Now D can be reached from A using the path A-E-C-D (r4/r5). This route
    still uses 2 routes, but is longer than A-B-D. However, Since the nodes
    in the path are completely distinct, we do not consider it redundant.

    We test for redundancy by iterating over the paths from shortest to longest, then
    comparing each path with all of the paths longer than itself. The comparison works
    by stripping the source/target nodes from each path, then labeling a longer path
    redundant if the intersection between its nodes and those in the shorter path is
    larger than a threshold when normalized relative to the shorter path. That is:
        intersection(longer, shorter) / len(shorter) >= threshold

    When redundancy_thresh == 1, paths are only rejected if every port in the shorter
    path is visited in the longer path.

    '''
    ## Sort the paths by length
    sorted_paths = sorted(paths[pair].keys(), key=lambda p: len(p))
    max_path_len = len(sorted_paths[-1])
    removed_paths = set()
    for i in range(len(sorted_paths)):
        shorter_path = sorted_paths[i]
        if len(shorter_path) == max_path_len:
            ## The longest paths can't possibly be redundant,
            ## so once we reach one we can stop
            break
        elif shorter_path in removed_paths:
            ## Skip this path if we already removed it
            continue

        ## Remove the source and target
        compare_path = list(shorter_path)
        del compare_path[0], compare_path[-1]
        ## Check against all longer paths
        for j in range(i+1, len(sorted_paths)):
            longer_path = sorted_paths[j]
            if len(longer_path) == len(shorter_path) or longer_path in removed_paths:
                continue

            longer_cmp_path = list(longer_path)
            del longer_cmp_path[0], longer_cmp_path[-1]
            if (len(set(longer_cmp_path).intersection(compare_path)) / len(compare_path)) >= redundancy_thresh:
                removed_paths.add(tuple([c for c in longer_path]))
                del paths[pair][longer_path]
