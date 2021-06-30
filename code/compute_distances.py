shipping_dist = dict()
with open('/home/larock.t/git/shipping/data/port_shipping_distances.csv', 'r') as fin:
    for line in fin:
        u,v,dist = line.strip().split(',')
        shipping_dist[(u,v)] = float(dist)

distances=[]
num = 0
total = 0
with open('iterative_paths.txt', 'r') as fin:
    for line in fin:
        a = line.strip().split(',')
        dist = int(a[-1])
        path = a[0:len(a)-1]
        d = 0.0
        for i in range(1, len(path)):
            d += shipping_dist[path[i-1], path[i]]
        distances.append(d)
        num+=1
        total+=1
        if num == 10_000_000:
            num = 0
            print(total, flush=True)

import pickle
with open('iterative_paths_distances.pickle', 'wb') as fpickle:
    pickle.dump(distances, fpickle)
