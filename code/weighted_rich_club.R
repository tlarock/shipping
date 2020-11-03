library(tnet)

#### OBSERVATION FREQUENCY WEIGHTS ####
graph = read.table("~/git/shipping/data/international_routes_2015_edgelist.txt", sep=',', header=FALSE)
as.tnet(graph)

nbins=25

rc_coeff_k_links = weighted_richclub_w(graph, rich="k", reshuffle="links", NR=1000, nbins=nbins, seed=NULL, directed=NULL)
plot(rc_coeff_k_links$x, rc_coeff_k_links$y, log="x")
write.table(rc_coeff_k_links, file = "~/git/shipping/results/rich_club/rc_coeff_k_links.txt", sep = ',', quote=FALSE)

rc_coeff_s_links = weighted_richclub_w(graph, rich="s", reshuffle="links", NR=1000, nbins=nbins, seed=NULL, directed=NULL)
plot(rc_coeff_s_links$x, rc_coeff_s_links$y, log="x")
write.table(rc_coeff_s_links, file = "~/git/shipping/results/rich_club/rc_coeff_s_links.txt", sep = ',', quote=FALSE)

rc_coeff_local_degree = weighted_richclub_w(graph,  rich="k", reshuffle="weights.local", NR=1000, nbins=nbins, seed=NULL, directed=NULL)
plot(rc_coeff_local_degree$x, rc_coeff_local_degree$y, log="x")
write.table(rc_coeff_local_degree, file = "~/git/shipping/results/rich_club/rc_coeff_local_degree.txt", sep = ',', quote=FALSE)

rc_coeff_local_strength = weighted_richclub_w(graph, rich="s", reshuffle="weights.local", NR=1000, nbins=nbins, seed=NULL, directed=NULL)
plot(rc_coeff_local_strength$x, rc_coeff_local_strength$y, log="x")
write.table(rc_coeff_local_strength, file = "~/git/shipping/results/rich_club/rc_coeff_local_strength.txt", sep = ',', quote=FALSE)

#### TEU WEIGHTS ####
graph = read.table("~/git/shipping/data/international_routes_2015_TEU_edgelist.txt", sep=',', header=FALSE)
as.tnet(graph)

rc_coeff_k_links = weighted_richclub_w(graph, rich="k", reshuffle="links", NR=1000, nbins=nbins, seed=NULL, directed=NULL)
plot(rc_coeff_k_links$x, rc_coeff_k_links$y, log="x")
write.table(rc_coeff_k_links, file = "~/git/shipping/results/rich_club/rc_coeff_k_links_TEU.txt", sep = ',', quote=FALSE)

rc_coeff_s_links = weighted_richclub_w(graph, rich="s", reshuffle="links", NR=1000, nbins=nbins, seed=NULL, directed=NULL)
plot(rc_coeff_s_links$x, rc_coeff_s_links$y, log="x")
write.table(rc_coeff_s_links, file = "~/git/shipping/results/rich_club/rc_coeff_s_links_TEU.txt", sep = ',', quote=FALSE)

rc_coeff_local_degree = weighted_richclub_w(graph,  rich="k", reshuffle="weights.local", NR=1000, nbins=nbins, seed=NULL, directed=NULL)
plot(rc_coeff_local_degree$x, rc_coeff_local_degree$y, log="x")
write.table(rc_coeff_local_degree, file = "~/git/shipping/results/rich_club/rc_coeff_local_degree_TEU.txt", sep = ',', quote=FALSE)

rc_coeff_local_strength = weighted_richclub_w(graph, rich="s", reshuffle="weights.local", NR=1000, nbins=nbins, seed=NULL, directed=NULL)
plot(rc_coeff_local_strength$x, rc_coeff_local_strength$y, log="x")
write.table(rc_coeff_local_strength, file = "~/git/shipping/results/rich_club/rc_coeff_local_strength_TEU.txt", sep = ',', quote=FALSE)
