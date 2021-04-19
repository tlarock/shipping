library(tnet)

#### OBSERVATION FREQUENCY WEIGHTS ####
input_filename = "~/git/shipping/data/international_routes_2015_edgelist.txt"
input_filename = "~/git/shipping/notebooks/tmp_edgelist.txt"
graph = read.table(input_filename, sep=',', header=FALSE)
as.tnet(graph)

output_path = "~/git/shipping/results/rich_club/"
output_path  = "~/git/shipping/notebooks/"
nbins=25

rc_coeff_k_links = weighted_richclub_w(graph, rich="k", reshuffle="links", NR=1000, nbins=nbins, seed=NULL, directed=NULL)
plot(rc_coeff_k_links$x, rc_coeff_k_links$y, log="x")
write.table(rc_coeff_k_links, file = paste(output_path, "rc_coeff_k_links.txt",sep=''), sep = ',', quote=FALSE)

rc_coeff_s_links = weighted_richclub_w(graph, rich="s", reshuffle="links", NR=1000, nbins=nbins, seed=NULL, directed=NULL)
plot(rc_coeff_s_links$x, rc_coeff_s_links$y, log="x")
write.table(rc_coeff_s_links, file = paste(output_path, "/rc_coeff_s_links.txt", sep=''), sep = ',', quote=FALSE)

rc_coeff_local_degree = weighted_richclub_w(graph,  rich="k", reshuffle="weights.local", NR=1000, nbins=nbins, seed=NULL, directed=NULL)
plot(rc_coeff_local_degree$x, rc_coeff_local_degree$y, log="x")
write.table(rc_coeff_local_degree, file = paste(output_path, "rc_coeff_local_degree.txt", sep=''), sep = ',', quote=FALSE)

rc_coeff_local_strength = weighted_richclub_w(graph, rich="s", reshuffle="weights.local", NR=1000, nbins=nbins, seed=NULL, directed=NULL)
plot(rc_coeff_local_strength$x, rc_coeff_local_strength$y, log="x")
write.table(rc_coeff_local_strength, file = paste(output_path, "rc_coeff_local_strength.txt", sep=''), sep = ',', quote=FALSE)

#### TEU WEIGHTS ####
input_filename = "~/git/shipping/data/international_routes_2015_TEU_edgelist.txt"
graph = read.table(input_filename, sep=',', header=FALSE)
as.tnet(graph)

rc_coeff_k_links = weighted_richclub_w(graph, rich="k", reshuffle="links", NR=1000, nbins=nbins, seed=NULL, directed=NULL)
plot(rc_coeff_k_links$x, rc_coeff_k_links$y, log="x")
write.table(rc_coeff_k_links, file = paste(output_path, "rc_coeff_k_links_TEU.txt", sep=''), sep = ',', quote=FALSE)

rc_coeff_s_links = weighted_richclub_w(graph, rich="s", reshuffle="links", NR=1000, nbins=nbins, seed=NULL, directed=NULL)
plot(rc_coeff_s_links$x, rc_coeff_s_links$y, log="x")
write.table(rc_coeff_s_links, file = paste(output_path, "rc_coeff_s_links_TEU.txt", sep=''), sep = ',', quote=FALSE)

rc_coeff_local_degree = weighted_richclub_w(graph,  rich="k", reshuffle="weights.local", NR=1000, nbins=nbins, seed=NULL, directed=NULL)
plot(rc_coeff_local_degree$x, rc_coeff_local_degree$y, log="x")
write.table(rc_coeff_local_degree, file = paste(output_path, "rc_coeff_local_degree_TEU.txt", sep=''), sep = ',', quote=FALSE)

rc_coeff_local_strength = weighted_richclub_w(graph, rich="s", reshuffle="weights.local", NR=1000, nbins=nbins, seed=NULL, directed=NULL)
plot(rc_coeff_local_strength$x, rc_coeff_local_strength$y, log="x")
write.table(rc_coeff_local_strength, file = paste(output_path, "rc_coeff_local_strength_TEU.txt", sep=''), sep = ',', quote=FALSE)
