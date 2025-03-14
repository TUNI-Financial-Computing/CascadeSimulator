import cascade_generator as cg
import networkx as nx  

## Generate a random graph of 10 000 nodes using networkx
G = nx.fast_gnp_random_graph(10000, 0.001)
## Extract the adjaceny list 
adj_list = [list(G.neighbors(node)) for node in G.nodes()]
# Set probability to 0.2
p = 0.2
q = 0.5

CG = cg.CascadeGenerator()
CG.set_graph(adj_list)
CG.set_probability(p)
CG.set_symptom_probability(q)
seed = [0]

## Measure the time it takes to generate a million cascades.
import time
start = time.time()
cascada = CG.generate_cascades(seed, 10000)
end = time.time()
print("Time to generate 10 000 cascades: ", end-start)
