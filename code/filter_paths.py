def filter_paths(paths, redundancy_thresh=0.5):
    '''
    Accepts a paths defaultdict(dict), the result of all_shortest_paths(G),
    and removes (in-place) all _redundant_  minimum-route paths. A path is
    considered redundant if there is a shorter path that uses the minimum
    number of routes and a subset of the same nodes.

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
    in the path arecompletely distinct, we do not consider it redundant.

    We test for redundancy by iterating over the paths from shortest to longest, then
    comparing each path with all of the paths longer than itself. The comparison works
    by stripping the source/target nodes from each path, then labeling a longer path
    redundant if its intersection with the shorter path is non-zero.

    Parameters
    ---------
    paths (defaultdict(dict)): A (potentially empty) defaultdict containing
                        all  minimum-routes paths from every source to every reahcable
                        target in G.
    Side Effect
    -----------
    Modifies paths in-place, removing redundant paths. Prints every 50,000 pairs.
    '''

    ## Counters for convenience because this process can be slow
    pair_counter = 0
    total_pairs = 0
    for pair in paths:
        ## If there is only 1 path, we have no choice
        if len(paths[pair]) == 1:
            continue

        ## Sort the paths by length and map them into strings of integers
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
                if (len(set(longer_cmp_path).intersection(compare_path)) / len(compare_path)) > redundancy_thresh:
                    removed_paths.add(tuple([c for c in longer_path]))
                    del paths[pair][longer_path]

        pair_counter += 1
        total_pairs += 1
        if pair_counter == 50_000:
            print(total_pairs)
            pair_counter = 0

