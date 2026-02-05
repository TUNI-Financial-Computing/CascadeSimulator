"""Python wrapper for C++ cascade generator.

This module provides a Pythonic interface to the high-performance C++ cascade
generation backend, with support for NetworkX graphs and convenient data structures.
"""

from dataclasses import dataclass
from typing import Optional, Union
import cascadesimulator.cascade_generator_cpp as cg
import networkx as nx


@dataclass
class Observation:
    """Single observation in a cascade.
    
    Attributes:
        node_id: The ID of the node that was activated
        time: The time at which the node was activated
        symptom: Binary indicator (1.0 or 0.0) whether the node shows symptoms
    """
    node_id: int
    time: float
    symptom: float


@dataclass
class Cascade:
    """A cascade representing the spread of information/influence through a network.
    
    Attributes:
        cascade: List of observations in chronological order
    """
    cascade: list[Observation]

    def __getitem__(self, index: int) -> Observation:
        """Allows direct indexing into the Cascade."""
        return self.cascade[index]

    def __len__(self) -> int:
        """Returns the number of observations in the cascade."""
        return len(self.cascade)


class pyCascadeGenerator:
    """Python wrapper for the C++ Independent Cascade (IC) model generator.
    
    This class provides an interface to generate cascades on NetworkX graphs using
    a high-performance C++ backend. It supports edge-specific transmission probabilities,
    symptom probabilities, and time-delayed cascades.
    
    Args:
        graph: NetworkX graph with 'weight' attribute on edges representing
               transmission probabilities. Nodes must be integers from 0 to n-1.
        cascade_model: Cascade model to use. Currently only "IC" (Independent Cascade)
                      is supported.
        q: Optional list of symptom probabilities for each node. If None, symptoms
           are not tracked.
        delay_times: Optional matrix of edge-specific delay times. If None, uses
                    unit delays (non-delayed IC model).
    
    Raises:
        NotImplementedError: If cascade_model is not "IC"
        AssertionError: If graph nodes are not integers from 0 to n-1
        KeyError: If graph edges are missing 'weight' attribute
    
    Example:
        >>> import networkx as nx
        >>> graph = nx.erdos_renyi_graph(100, 0.1, directed=True)
        >>> for u, v in graph.edges():
        ...     graph[u][v]['weight'] = 0.3
        >>> gen = pyCascadeGenerator(graph, cascade_model='IC')
        >>> cascades = gen.generate(seeds=[0], num_cascades=10)
    """
    
    def __init__(
        self,
        graph: nx.Graph,
        cascade_model: str = "IC",
        q: Optional[list[float]] = None,
        delay_times: Optional[list[list[float]]] = None,
    ) -> None:
        # Validate cascade model
        if cascade_model != "IC":
            raise NotImplementedError("Only IC model is supported for now")
        
        # Validate graph nodes are consecutive integers starting from 0
        nodes = set(graph.nodes())
        expected_nodes = set(range(len(graph.nodes())))
        if nodes != expected_nodes:
            raise ValueError(
                f"Graph nodes must be integers from 0 to {len(graph.nodes())-1}. "
                f"Got: {sorted(nodes)}"
            )
        
        # Store graph reference
        self.graph_ = graph
        n_nodes = len(graph.nodes())
        
        # Initialize C++ generator
        self.cascade_model_ = cg.CascadeGenerator()
        
        # Convert graph to adjacency list
        self.adj_list_ = [[v for v in graph.neighbors(u)] for u in graph.nodes()]
        self.cascade_model_.set_graph(self.adj_list_)
        
        # Extract edge probabilities
        try:
            self.probs = [[graph[u][v]['weight'] for v in graph.neighbors(u)] for u in graph.nodes()]
        except KeyError as e:
            raise KeyError(
                "All edges must have a 'weight' attribute representing transmission probability. "
                f"Missing weight for edge: {e}"
            )
        self.cascade_model_.set_probabilities(self.probs)
        
        # Set delays if provided
        if delay_times is not None:
            if len(delay_times) != n_nodes:
                raise ValueError(
                    f"delay_times must have {n_nodes} rows (one per node), got {len(delay_times)}"
                )
            self.cascade_model_.set_delays(delay_times)
        
        # Set symptom probabilities if provided
        if q is not None:
            if len(q) != n_nodes:
                raise ValueError(
                    f"q (symptom probabilities) must have {n_nodes} entries (one per node), got {len(q)}"
                )
            self.cascade_model_.set_symptom_probabilities(q)

    def generate(
        self, 
        seeds: list[int], 
        num_cascades: int = 1, 
        cutoff: Optional[float] = None
    ) -> Union[Cascade, list[Cascade]]:
        """Generate cascades from seed nodes.
        
        Args:
            seeds: List of seed node IDs from which cascades originate
            num_cascades: Number of independent cascades to generate
            cutoff: Optional time cutoff for cascade generation. Nodes activated
                   after this time are not included. If None, uses any previously
                   set cutoff value, or generates full cascades if no cutoff is set.
        
        Returns:
            If num_cascades == 1: Single Cascade object
            Otherwise: List of Cascade objects
            
        Raises:
            ValueError: If seeds is empty or contains invalid node IDs
        
        Example:
            >>> gen = pyCascadeGenerator(graph, 'IC')
            >>> # Generate single cascade
            >>> cascade = gen.generate(seeds=[0])
            >>> # Generate multiple cascades with time cutoff
            >>> cascades = gen.generate(seeds=[0, 5], num_cascades=100, cutoff=5.0)
        """
        # Validate seeds
        if not seeds:
            raise ValueError("seeds cannot be empty")
        
        n_nodes = len(self.graph_.nodes())
        for seed in seeds:
            if not isinstance(seed, int) or seed < 0 or seed >= n_nodes:
                raise ValueError(
                    f"Invalid seed node {seed}. Must be integer in range [0, {n_nodes})"
                )
        
        # Only modify cutoff if explicitly provided
        if cutoff is not None:
            self.cascade_model_.set_cutoff(cutoff)
        
        # Use C++ batch generation for efficiency
        if num_cascades > 1:
            cpp_cascades = self.cascade_model_.generate_cascades(seeds, num_cascades)
            cascades = [
                Cascade([Observation(*args) for args in cascade])
                for cascade in cpp_cascades
            ]
            return cascades
        else:
            # Single cascade
            cascade = self.cascade_model_.generate_cascade(seeds)
            return Cascade([Observation(*args) for args in cascade])

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
        q=symptom_probabilities
    )
    seed = [0]
    num_samples = 10
    cascades = cascade_generator.generate(seed, num_samples)
    print(cascades)