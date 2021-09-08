def filter_distance(total_distances, filtered_paths, available_paths, distance_thresh):
    '''
    Accepts a paths defaultdict(dict), the result of all_shortest_paths(G),
    and removes (in-place) all paths between the nodes indicated by pair whose
    total route distance is more than distance_thresh times the minimum distance
    computed over all paths between the pair of source/target nodes.

    '''
    min_dist = min([total_distances[path] for path in available_paths]) ## will not change
    for path in available_paths:
        if total_distances[path] > min_dist*distance_thresh:
            filtered_paths.add(path)

    return filtered_paths

def filter_dist_detour(total_distances, filtered_paths, available_paths, shipping_dist):
    '''

    '''
    ## Set the threshold
    avail_tdists = {path:dist for path, dist in total_distances.items() if path in available_paths}
    ## detour factor for minimum path
    min_path,  min_dist = sorted(avail_tdists.items(), key=lambda kv: kv[1])[0]
    min_true_detour_fact = min_dist / shipping_dist
    all_min_detour_facts = {path:total_distances[path]/min_dist for path in available_paths-{min_path}}
    for path in all_min_detour_facts:
        if all_min_detour_facts[path] > min_true_detour_fact:
            filtered_paths.add(path)

    return filtered_paths

def filter_redundant(total_distances, redundancy_thresh):
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
    def get_compare_path(path, redundancy_thresh):
        if redundancy_thresh == 1.0:
            ## If the redundancy threhold is the whole path,
            ## we don't need to remove the endpoints.
            compare_path = set(path)
        else:
            ## Remove the source and target
            compare_path = list(path)
            del compare_path[0], compare_path[-1]
        return compare_path

    filtered_paths = set()
    ## Get sorted list of paths
    paths_by_length = dict()
    for path in total_distances.keys():
        paths_by_length.setdefault(len(path), set())
        paths_by_length[len(path)].add(path)

    sorted_lengths = sorted(paths_by_length.keys(), reverse=True)
    ## Filter based on redundancy
    ## Loop from longest to 2nd from shortest
    for i in range(len(sorted_lengths)-1):
        length = sorted_lengths[i]
        for longer_path in paths_by_length[length]:
            broken = False
            compare_path = get_compare_path(longer_path, redundancy_thresh)
            ## Check against all shorter paths
            ## Loop over all shortest path lengths
            for j in range(len(sorted_lengths)-1, i, -1):
                slength = sorted_lengths[j]
                for shorter_path in paths_by_length[slength]:
                    shorter_cmp_path = get_compare_path(shorter_path, redundancy_thresh)
                    if (len(shorter_cmp_path.intersection(compare_path)) / len(shorter_cmp_path)) >= redundancy_thresh:
                        filtered_paths.add(longer_path)
                        ## We can break as soon as we find one shorter_path
                        ## that longer_path is redundant with
                        broken = True
                        break
                if broken:
                    break

    return filtered_paths
