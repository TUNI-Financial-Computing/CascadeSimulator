import cascade_generator as cg

C = cg.CascadeGenerator()
graph = [[1,2], [2,3], [3,4], [4,5], [5,0], [0,1]]
C.set_graph(graph)
probs = [[1.0, 1.0], [0.3, 0.4], [0.5, 0.6], [0.7, 0.8], [0.9, 1.0], [0.11, 0.12]]
C.set_probabilities(probs)
C.set_symptom_probability(0.5)
cascade = C.generate_cascade([0])
print(cascade)
cascada = C.generate_cascades([0], 5)
print(cascada)
