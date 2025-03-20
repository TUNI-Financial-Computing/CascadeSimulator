import cascade_generator as cg
import networkx as nx  

## Make a python wrapper class for the c++ cascade generator
class CascadeGenerator:
    def __init__(
      self, 
      graph: nx.Graph = None, 
      cascade_model: str = "IC",
      symptom_rates: list[float] = None,
      delay_times: list = None,
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
    def Generate(self, seed: list[int], num_samples: int):
      return self.cascade_model_.generate_cascades(seed, num_samples)

## Example usage:
if __name__ == "__main__":
    from random import random
    graph = nx.erdos_renyi_graph(100, 0.1)
    symptom_probabilities = [0.5 + 0.5*random() for u in graph.nodes()]
    for edge in graph.edges():
        graph[edge[0]][edge[1]]['weight'] = 0.1 + 0.2*random()
    cascade_generator = CascadeGenerator(
       graph=graph,
       cascade_model="IC",
       symptom_rates=symptom_probabilities
    )
    seed = [0]
    num_samples = 10
    cascades = cascade_generator.Generate(seed, num_samples)
    print(cascades)