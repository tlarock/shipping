
# coding: utf-8

# In[1]:


import pathpy as pp
import hypa
import pandas as pd
import geopy.distance as gd
import numpy as np

import matplotlib.pyplot as plt
get_ipython().magic('matplotlib inline')


# In[2]:


plt.rcParams['font.size'] = 30


# In[3]:


## Should do paths both by # ships and by tonnage
paths = pp.Paths.read_file('../data/international_routes_2015_vessels.ngram', frequency=True)
paths_tonnage = pp.Paths.read_file('../data/international_routes_2015_TEU.ngram', frequency=True)


# In[4]:


print(paths)
print('\n\n')
print(paths_tonnage)


# ### Degree Distribution

# In[5]:


import sys
sys.path.append('../../debruijn-nets/code/')
from analysis import *


# In[6]:


hy = hypa.Hypa(paths) 
hy.initialize_xi(k=1, constant_xi=True, verbose=False)
network = hy.network


# In[7]:


plot_degree(network, degree='degree', num_bins=150, log_bins=False);


# In[8]:


plot_degree(network, degree='degree', num_bins=150, log_bins=True);
plt.title("Degree Distribution");


# In[10]:


plt.figure(figsize=(12,10))
plot_randomized_degree(hy, degree='degree', num_bins=150, log_bins=True, num_samples=10);
plt.title("Degree Distribution");


# In[11]:


plot_degree(network, degree='weight', num_bins=150, log_bins=False);
plt.title('Strength Distribution');


# In[12]:


plt.title('Strength Distribution');
plot_degree(network, degree='weight', num_bins=150, log_bins=True);


# In[14]:


plt.figure(figsize=(12,10))
plot_randomized_degree(hy, degree='weight', num_bins=50, log_bins=True, num_samples=10);
plt.title("Strength Distribution");


# In[15]:


plt.title('in-Weight Distribution (log-log scale)');
plot_degree(network, degree='inweight', num_bins=150, log_bins=True);


# In[16]:


plt.title('out-Weight Distribution (log-log scale)');
plot_degree(network, degree='outweight', num_bins=150, log_bins=True);


# In[17]:


## Edge weight distribution
edge_weights = []
for edge, attr in hy.network.edges.items():
    edge_weights.append(attr['weight'])
plt.title('Edge Weight Distribution')
plt.xlabel('Weight')
plt.ylabel('Frequency')
plt.hist(edge_weights, bins = 50, log=True);


# In[ ]:





# In[ ]:





# In[18]:


import pathpy.algorithms.statistics as pstats


# In[19]:


hy_TEU = hypa.Hypa(paths_tonnage)
hy_TEU.initialize_xi(k=1, constant_xi=False, verbose=False)



# In[20]:


## Edge weight distribution
edge_weights = []
for edge, attr in hy_TEU.network.edges.items():
    edge_weights.append(attr['weight'])
edge_weights = np.array(edge_weights)
bins = pstats.get_bins(edge_weights, num_bins=50, log_bins=True)
y, _ = np.histogram(edge_weights, bins=bins, density=False)
x = bins[1:] - np.diff(bins)/2.0

plt.title('Edge Weight Distribution')
plt.xlabel('Weight')
plt.ylabel('Frequency')
plt.loglog(x, y, 'o');
#plt.hist(edge_weights, bins=bins)
#plt.xscale('log')


# In[ ]:





# In[ ]:





# ### Path Length Distributions

# In[21]:


plt.figure(figsize=(12, 7), dpi=150)
unique = dict()
for k in sorted(paths.paths.keys()):
    if k > 0:
        unique[k] = paths.unique_paths(l=k, consider_longer_paths=False)
plt.bar(unique.keys(), unique.values())
plt.title('Unique Paths')
plt.xlabel('Length')
plt.ylabel('# Unique Paths')
plt.tight_layout()
plt.savefig('../plots/preliminary_report/unique_path_histogram.png')


# In[22]:


plt.figure(figsize=(12, 7), dpi=150)
## Get the number of longest paths with length k for each k
path_lengths_dict = paths.path_lengths()
dist = [path_lengths_dict[k][1] for k in sorted(path_lengths_dict.keys())]

plt.bar(list(range(len(dist))), dist)
plt.title('Distribution of Vessels Per Path Length')
plt.xlabel('Path Length')
plt.ylabel("# Vessels per Path Length")
plt.tight_layout()
plt.savefig('../plots/preliminary_report/path_length_versus_vessels.png')


# There is a very large number of vessels traveling on short, 3 port trips (spike at k=2). 

# In[23]:


plt.figure(figsize=(12, 7), dpi=150)
path_lengths_dict = paths_tonnage.path_lengths()
dist = [path_lengths_dict[k][1] for k in sorted(path_lengths_dict.keys())]

plt.bar(list(range(len(dist))), dist)
plt.title('Distribution of TEU Per Path Length')
plt.xlabel('Path Length')
plt.ylabel("TEU per Path Length")
plt.tight_layout()
plt.savefig('../plots/preliminary_report/path_length_versus_TEU.png')


# Interestingly, most of the tonnage is concentrated on the middle-distance trips, e.g. from 9-16 ports. Despite making up a large proporition of the total vessels, the k=2 trips do not carry nearly the most tonnage. The very long distance trips, e.g. with path length > 20, carry the least amount of tonnage.

# ### From Path Length to Trip Distance

# In[ ]:


## Get coordinates
coords = pd.read_csv('../data/ports_2015.csv', sep=',')
port_coord = {row['port']: (row['lat'], row['lng']) for idx, row in coords.iterrows()}
port_info = {row['port']: {'country_name':row['country_name'], 'counry_code':row['country_code']} for idx, row in coords.iterrows()}


# In[ ]:


## Scatter total tonnage vs. total distance traveled
distances = []
path_lengths_scat = []
tonnages = []
tonnages_normed = []
for k, k_paths in paths_tonnage.paths.items():
    if k > 0:
        for path, data in k_paths.items():
            if data[1] > 0:
                distance = 0.0
                for i in range(1, len(path)):
                    try:
                        loc_orig, loc_dest = (port_coord[path[i-1]], port_coord[path[i]])
                    except KeyError as e:
                        print(e)
                    distance += gd.distance(loc_orig, loc_dest).km

                distances.append(distance)
                tonnages.append(data[1])
                tonnages_normed.append(data[1] / paths.paths[k][path][1])
                path_lengths_scat.append(k)


# In[ ]:


plt.figure(figsize=(12,7), dpi=150)
plt.hist(distances, bins=100)
plt.xlabel('Total Trip Distance (km)')
plt.ylabel('Frequency')
plt.tight_layout()
plt.savefig('../plots/preliminary_report/route_distance_histogram.png')


# In[ ]:


plt.figure(figsize=(12, 7), dpi=150)
plt.scatter(distances, tonnages)
plt.xlabel('Total Trip Distance (km)')
plt.ylabel('TEU')
plt.tight_layout()
plt.savefig('../plots/preliminary_report/route_distance_versus_TEU.png')


# In[ ]:


plt.figure(figsize=(12, 7), dpi=150)
plt.scatter(distances, tonnages_normed)
plt.xlabel('Total Trip Distance (km)')
plt.ylabel('TEU / # Ships')
plt.tight_layout()
#plt.savefig('../plots/preliminary_report/route_distance_versus_TEU.png')


# In[ ]:


plt.figure(figsize=(12, 7), dpi=150)
plt.scatter(distances, path_lengths_scat)
plt.xlabel('Total Trip Distance (km)')
plt.ylabel('Path Length')
plt.tight_layout()
plt.savefig('../plots/preliminary_report/route_distance_versus_path_length.png')


# ## Multi-order Graphical Model

# In[ ]:


graphical_model = pp.MultiOrderModel(paths, max_order=4)


# ### Optimal Order Estimation
# Here each order (memory length) is tested statistically against the previous order. The statistical test quantifies the tradeoff between degrees of freedom (higher orders = more free parameters in the Markov model) and explanatory power (not under or over fitting the real data).

# In[ ]:


graphical_model.estimate_order()


# The optimal order detected is 2, meaning 2 steps of memory, e.g. (C | A-->B), are best to represent this dataset.

# In[ ]:


## same for paths_tonnage
graphical_model = pp.MultiOrderModel(paths_tonnage, max_order=5)
graphical_model.estimate_order()


# In[ ]:





# ### Basic Visualization

# In[ ]:


hon = pp.HigherOrderNetwork(paths, k=2)


# In[ ]:


params = dict()
params['width'] = 1000
params['height'] = 1000
params['label_opacity'] = 0.0


# In[ ]:


#pp.visualisation.plot(hon, **params)


# ## HYPA Anomalous Paths
# 
# In this section, we use HYPA to compute a probability for each edge in the higher order network. The probability is of the form $P(f(u,v) \leq X)$, where $f(u,v)$ is the observed frequency of the (higher-order) edge from $u$ to $v$ and $X$ is a random variable representing the possible observations. If this probability is very close to 1, then it is unlikely we would ever observe a weight larger than the one we observed. If it is close to 0, then it is unlikely we would ever observe a weight smaller than the one we observed. If a threshold $\alpha$ (or $1-\alpha$) is exceeded in either direction, we call this edge weight significantly deviating and note that edge.
# 
# First, for convenience we focus on the 2nd order edges (each 3 port path in the system). I chose 2nd order because the graphical model found evidence for 2nd order being significant.
# 
# ### Distance correlations
# Now we compute a histogram showing the number of over- and under-represented paths for each geographic distance.

# In[ ]:


## Constuct the hypergeometric ensemble
k=2
hy = hypa.Hypa(paths)
hy.construct_hypa_network(k=k)


# In[ ]:


## Get coordinates
coords = pd.read_csv('../data/ports_2015.csv', sep=',')
port_coord = {row['port']: (row['lat'], row['lng']) for idx, row in coords.iterrows()}
port_info = {row['port']: {'country_name':row['country_name'], 'counry_code':row['country_code']} for idx, row in coords.iterrows()}


# In[ ]:


## Get distances for each edge
for e,edat in hy.hypa_net.edges.items():
    orig = e[0].split(',')[0]
    dest = e[1].split(',')[-1]

    try:
        loc_orig, loc_dest = (port_coord[i] for i in (orig, dest))
    except KeyError:
        continue

    hy.hypa_net.edges[e]['dist_od'] = gd.distance(loc_orig, loc_dest).km
    
## Put distances into a matrix for conveience
dist_hypa_k = np.array([(d['dist_od'], d['pval']) for e,d in hy.hypa_net.edges.items()])


# In[ ]:


M = hy.adjacency.sum()
print(str(1.0/M))


# In[ ]:


## Filter significance values (using parameter \alpha in HYPA)
po = pu = 0.000001
po = pu = 1.0 / M

## distance filter - here I am not filtering by distance at all (hence the max)
idx_shortdist = dist_hypa_k[:,0] <= np.max(dist_hypa_k)
idx_over = np.logical_and(dist_hypa_k[:,1] > np.log(1-po), idx_shortdist)
idx_under = np.logical_and(dist_hypa_k[:,1] < np.log(pu), idx_shortdist)


# In[ ]:


plt.figure(figsize=(16,9), dpi=200)
plt.hist((dist_hypa_k[idx_under,0], dist_hypa_k[idx_over,0]), bins=30, density=False, label=('Under', "Over"))
plt.xlabel("Origin-destination distance [km]")
plt.ylabel("# Significant")
plt.legend(title='HYPA({})'.format(k))
plt.tight_layout()


# This plot shows a couple of things:
# * The spike in under-represented transitions at distance 0 means that returning to the same port, meaning transitions A-B-A, is not likely
# * Interestingly, there are also some over-represnted transitions at distance 0, which means that sometimes this does happen. Perhaps we can find an explanation for this.

# In[ ]:


## get the over-represented transitions with distance 0
idx_zerodist = dist_hypa_k[:,0] == 0
idx_over = np.logical_and(dist_hypa_k[:,1] > np.log(1-po), idx_zerodist)
idx_under = np.logical_and(dist_hypa_k[:,1] < np.log(pu), idx_zerodist)


# In[ ]:


plt.figure(figsize=(16,9), dpi=200)
plt.hist((dist_hypa_k[idx_under,0], dist_hypa_k[idx_over,0]), bins=30, density=False, label=('Under', "Over"))
plt.xlabel("Origin-destination distance [km]")
plt.ylabel("# Significant")
plt.legend(title='HYPA({})'.format(k))
plt.tight_layout()


# In[ ]:


distance_sort = sorted(hy.hypa_net.edges.items(), key=lambda kv: kv[1]['dist_od'], reverse=False)
filtered_ports = list(filter(lambda kv: (kv[1]['pval'] > np.log(1-po) and kv[1]['dist_od'] == 0), distance_sort))


# In[ ]:


link = {'source':list(), 'target':list(), 'value':list()}
labels = list()
idx=0
mapping = dict()
plot_net = pp.Network()
for edge_data in filtered_ports:
    edge, edge_dict = edge_data
    path = edge[0].split(',')[0], edge[0].split(',')[1], edge[1].split(',')[1]
    for i in range(1, len(path)):
        source = path[i-1]
        target = path[i]
        if source not in labels:
            labels.append(source)
            mapping[source] = idx
            idx+=1
        if target not in labels:
            labels.append(target)
            mapping[target] = idx
            idx+=1

        link['source'].append(mapping[source])
        link['target'].append(mapping[target])
        link['value'].append(edge_dict['weight'])
        plot_net.add_edge(source, target, weight=edge_dict['weight'])
pp.visualisation.plot(plot_net, width=800, height=800, label_size='30px')


# In[ ]:


import networkx as nx
import cartopy.crs as ccrs


# In[ ]:


coords = pd.read_csv('../data/ports_2015.csv', sep=',')
port_coord = {row['port']: (row['lng'], row['lat']) for idx, row in coords.iterrows()}
G = nx.DiGraph()

edges = dict()
for edge_data in filtered_ports:
    edge, edge_dict = edge_data
    path = edge[0].split(',')[0], edge[0].split(',')[1], edge[1].split(',')[1]
    for i in range(1, len(path)):
        source = path[i-1]
        target = path[i]
        if source not in G.nodes():
            G.add_node(source, pos=port_coord[source])
        if target not in G.nodes():
            G.add_node(target, pos=port_coord[target])
        edges.setdefault((source, target), {'weight':0.0})
        #edges[(source, target)]['weight'] += float(edge_dict['weight'])
        edges[(source, target)]['weight'] = 1

edge_tups = [(u,v,d['weight']) for (u,v),d in edges.items()]
G.add_weighted_edges_from(edge_tups, weight='weight')
print(nx.info(G))
edges = G.edges()
weights_normed = np.array([G[u][v]['weight'] for u,v in edges])
#a = 1 
#b = 10.0 
#weights_normed = ((b-a) * (weights_normed-weights_normed.min())) / (weights_normed.max() - weights_normed.min()) + a 
plt.figure(figsize=(20,20))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
ax.stock_img()
nx.draw(G, nx.get_node_attributes(G, 'pos'), edges=edges, width=weights_normed,         with_labels=False, font_size=5, node_size=5, arrowsize=1, edge_color='blue')


# From the above, it seems like the over-represented 0 distance 3 port trips are usually geographically convenient, e.g. they are in the same country (China) or same region (Italy --> Malta --> Italy)

# Note to self: No data on North Korean ports? Do they not use maritime shipping? Seems like they would since they trade with African and Central American countries.

# ### What if we repeat this on the 3rd order?

# In[ ]:


## Constuct the hypergeometric ensemble
k=3
hy = hypa.Hypa(paths)
hy.construct_hypa_network(k=k)


# In[ ]:


## Get coordinates
coords = pd.read_csv('../data/ports_2015.csv', sep=',')
port_coord = {row['port']: (row['lat'], row['lng']) for idx, row in coords.iterrows()}
port_info = {row['port']: {'country_name':row['country_name'], 'counry_code':row['country_code']} for idx, row in coords.iterrows()}


# In[ ]:


## Get distances for each edge
for e,edat in hy.hypa_net.edges.items():
    orig = e[0].split(',')[0]
    dest = e[1].split(',')[-1]

    try:
        loc_orig, loc_dest = (port_coord[i] for i in (orig, dest))
    except KeyError:
        continue

    hy.hypa_net.edges[e]['dist_od'] = gd.distance(loc_orig, loc_dest).km
    
## Put distances into a matrix for conveience
dist_hypa_k = np.array([(d['dist_od'], d['pval']) for e,d in hy.hypa_net.edges.items()])


# In[ ]:


## Filter significance values (using parameter \alpha in HYPA)
po = pu = 0.000001

## distance filter - here I am not filtering by distance at all (hence the max)
idx_shortdist = dist_hypa_k[:,0] <= np.max(dist_hypa_k)
idx_over = np.logical_and(dist_hypa_k[:,1] > np.log(1-po), idx_shortdist)
idx_under = np.logical_and(dist_hypa_k[:,1] < np.log(pu), idx_shortdist)


# In[ ]:


plt.figure(figsize=(16,9), dpi=200)
plt.hist((dist_hypa_k[idx_under,0], dist_hypa_k[idx_over,0]), bins=30, density=False, label=('Under', "Over"))
plt.xlabel("Origin-destination distance [km]")
plt.ylabel("Frequency")
plt.legend(title='HYPA({})'.format(k))
plt.tight_layout()


# In[ ]:





# ### Total distance rather than origin destination

# In[ ]:


## Get coordinates
coords = pd.read_csv('../data/ports_2015.csv', sep=',')
port_coord = {row['port']: (row['lat'], row['lng']) for idx, row in coords.iterrows()}
port_info = {row['port']: {'country_name':row['country_name'], 'counry_code':row['country_code']} for idx, row in coords.iterrows()}


# In[ ]:


## Constuct the hypergeometric ensemble
k=2
hy = hypa.Hypa(paths)
hy.construct_hypa_network(k=k)


# In[ ]:


## Get distances for each edge
for e,edat in hy.hypa_net.edges.items():
    orig = e[0].split(',')[0]
    dest = e[1].split(',')[-1]

    path = e[0].split(',') + [e[1].split(',')[-1]]
    distance = 0
    for i in range(1, len(path)):
        try:
            loc_orig, loc_dest = (port_coord[path[i-1]], port_coord[path[i]])
        except KeyError as e:
            print(e)
        distance += gd.distance(loc_orig, loc_dest).km

    hy.hypa_net.edges[e]['dist_total'] = distance
    
## Put distances into a matrix for conveience
dist_hypa_k = np.array([(d['dist_total'], d['pval']) for e,d in hy.hypa_net.edges.items()])


# In[ ]:


M = hy.adjacency.sum()
print(str(1.0/M))


# In[ ]:


## Filter significance values (using parameter \alpha in HYPA)
po = pu = 0.00001
po = pu = 1.0 / M

## distance filter - here I am not filtering by distance at all (hence the max)
idx_shortdist = dist_hypa_k[:,0] <= np.max(dist_hypa_k)
idx_over = np.logical_and(dist_hypa_k[:,1] > np.log(1-po), idx_shortdist)
idx_under = np.logical_and(dist_hypa_k[:,1] < np.log(pu), idx_shortdist)


# In[ ]:


plt.figure(figsize=(16,9), dpi=200)
plt.hist((dist_hypa_k[idx_under,0], dist_hypa_k[idx_over,0]), bins=30, density=False, label=('Under', "Over"))
plt.xlabel("Total distance [km]")
plt.ylabel("Frequency")
plt.legend(title='HYPA({})'.format(k))
plt.tight_layout()


# In[ ]:


distance_sort = sorted(hy.hypa_net.edges.items(), key=lambda kv: kv[1]['dist_total'], reverse=False)
filtered_ports = list(filter(lambda kv: (kv[1]['pval'] > np.log(1-po) and kv[1]['dist_total'] < 1000), distance_sort))
#filtered_ports = list(filter(lambda kv: (kv[1]['pval'] < np.log(pu) and kv[1]['dist_total'] < 1000), distance_sort))


# In[ ]:


coords = pd.read_csv('../data/ports_2015.csv', sep=',')
port_coord = {row['port']: (row['lng'], row['lat']) for idx, row in coords.iterrows()}
G = nx.DiGraph()

edges = dict()
for edge_data in filtered_ports:
    edge, edge_dict = edge_data
    path = edge[0].split(',')[0], edge[0].split(',')[1], edge[1].split(',')[1]
    for i in range(1, len(path)):
        source = path[i-1]
        target = path[i]
        if source not in G.nodes():
            G.add_node(source, pos=port_coord[source])
        if target not in G.nodes():
            G.add_node(target, pos=port_coord[target])
        edges.setdefault((source, target), {'weight':0.0})
        #edges[(source, target)]['weight'] += float(edge_dict['weight'])
        edges[(source, target)]['weight'] = 1

edge_tups = [(u,v,d['weight']) for (u,v),d in edges.items()]
G.add_weighted_edges_from(edge_tups, weight='weight')
print(nx.info(G))
edges = G.edges()
weights_normed = np.array([G[u][v]['weight'] for u,v in edges])
#a = 1 
#b = 10.0 
#weights_normed = ((b-a) * (weights_normed-weights_normed.min())) / (weights_normed.max() - weights_normed.min()) + a 
plt.figure(figsize=(20,20))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
ax.stock_img()
nx.draw(G, nx.get_node_attributes(G, 'pos'), edges=edges, width=weights_normed,         with_labels=False, font_size=5, node_size=5, arrowsize=1, edge_color='blue')


# In[ ]:





# In[ ]:





# In[ ]:


## Constuct the hypergeometric ensemble
k=1
hy = hypa.Hypa(paths)
hy.construct_hypa_network(k=k, verbose=False)


# In[ ]:


## Idea: find the 3 top weighted ports and show them in a 3 layer sankey diagram
coords = pd.read_csv('../data/ports_2015.csv', sep=',')
port_coord = {row['port']: (row['lng'], row['lat']) for idx, row in coords.iterrows()}
G = nx.DiGraph()
edges = dict()
for edge_data in hy.network.edges.items():
    edge, edge_dict = edge_data
    source = edge[0]
    target = edge[1]
    if source not in G.nodes():
        G.add_node(source, pos=port_coord[source])
    if target not in G.nodes():
        G.add_node(target, pos=port_coord[target])
    edges.setdefault((source, target), {'weight':0.0})
    edges[(source, target)]['weight'] = float(edge_dict['weight'])

edge_tups = [(u,v,d['weight']) for (u,v),d in edges.items()]
G.add_weighted_edges_from(edge_tups, weight='weight')
print(nx.info(G))


# In[ ]:


all_strengths = {node:sum([G[node][ne]['weight'] for ne in G[node].keys()]) for node in G.nodes()}


# In[ ]:


top_strengths = sorted(all_strengths.items(), key= lambda kv: kv[1], reverse=False)[0:20]


# In[ ]:


top_strengths


# In[ ]:


top_strengths.reverse()


# In[ ]:


link = {'source':list(), 'target':list(), 'value':list()}
labels = list()
idx=0
mapping = dict()
## for the top nodes
for node, weight in top_strengths:
    if node not in labels:
        labels.append(node)
        mapping[node] = idx
        idx += 1

    ## get all of the _in_ neighbors
    for ne in G.predecessors(node):
        if str(ne + '-src') not in labels:
            labels.append((ne+ '-src'))
            mapping[(ne+ '-src')] = idx
            idx += 1
        weight = G[ne][node]['weight']
        
        link['source'].append(mapping[(ne + '-src')])
        link['target'].append(mapping[node])
        link['value'].append(weight)
        
    ## get all of the _in_ neighbors
    for ne in G.successors(node):
        if (ne+ '-trgt') not in labels:
            labels.append((ne + '-trgt'))
            mapping[(ne+ '-trgt')] = idx
            idx += 1
        weight = G[node][ne]['weight']
        
        link['source'].append(mapping[node])
        link['target'].append(mapping[(ne+ '-trgt')])
        link['value'].append(weight)
        


# In[ ]:


import plotly.graph_objects as go
fig = go.Figure(data=[go.Sankey(
    node = dict(
            pad = 25,
            thickness=40,
      line = dict(color = "black", width = 0.5),
      label = labels,
      color = "blue"
    ),
    link = link)])

#fig.write_image('test.pdf')
fig.show(renderer='browser')


# In[ ]:




