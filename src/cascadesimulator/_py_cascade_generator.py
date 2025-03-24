from typing import Optional
import cascadesimulator.cascade_generator_cpp as cg  # type: ignore
import networkx as nx

## Make a python wrapper class for the c++ cascade generator
""" The CascadeGenerator class is a wrapper class for the C++ CascadeGenerator class.
    It provides a simple interface to generate cascades on a given graph.

Initializer inputs:
    graph: a networkx graph object representing the underlying graph, weights represent probabilities
    cascade_model: a string representing the cascade model to use. For now, only "IC" is supported
    symptom_rates: a list of floats representing the probability of a node showing symptoms
    delay_times: a list of lists of floats representing the delay times for edge in the graph. If None, the delay times are set to 1, i.e., regular IC model
"""
class pyCascadeGenerator:
    def __init__(
        self,
        graph: nx.Graph,
        cascade_model: str = "IC",
        symptom_rates: Optional[list[float]] = None,
        delay_times: Optional[list[float]] = None,
    ):
        if (cascade_model != "IC"):
          raise NotImplementedError("Only IC model is supported for now")
        self.graph_ = graph
        ## assert that the graph nodes are integers from 0 to n-1:
        assert set(graph.nodes()) == set(range(len(graph.nodes())))
        self.cascade_model_ = cg.CascadeGenerator()
        self.adj_list_ = [[v for v in graph.neighbors(u)] for u in graph.nodes()]
        self.cascade_model_.set_graph(self.adj_list_)
        self.probs = [[graph[u][v]['weight'] for v in graph.neighbors(u)] for u in graph.nodes()]
        self.cascade_model_.set_probabilities(self.probs)
        if delay_times is not None:
            self.cascade_model_.set_delays(delay_times)
        if symptom_rates is not None:
            self.cascade_model_.set_symptom_probabilities(symptom_rates)

    """ The Generate() function generates num_samples cascades given a seed set of nodes.
    Args:
        seed: list of integers representing the seed set of nodes
        num_samples: integer representing the number of cascades to generate
    Returns:
        list of lists of triplets representing the cascades. Each triplet is of the form (node, time, symptom)
    """
    def generate(self, seeds: list[int], num_samples: int):
        return self.cascade_model_.generate_cascades(seeds, num_samples)

## Example usage:
if __name__ == "__main__":
    from random import random
    graph = nx.erdos_renyi_graph(100, 0.1)
    symptom_probabilities = [0.5 + 0.5*random() for u in graph.nodes()]
    for edge in graph.edges():
        graph[edge[0]][edge[1]]['weight'] = 0.1 + 0.2*random()
    cascade_generator = pyCascadeGenerator(
        graph=graph,
        cascade_model="IC",
        symptom_rates=symptom_probabilities
    )
    seed = [0]
    num_samples = 10
    cascades = cascade_generator.generate(seed, num_samples)
    print(cascades)