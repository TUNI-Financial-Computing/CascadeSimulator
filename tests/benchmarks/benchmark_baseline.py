"""Performance benchmarks for baseline functionality."""

import pytest
import networkx as nx
from cascadesimulator import pyCascadeGenerator


@pytest.fixture
def small_graph():
    """Small graph (100 nodes)."""
    graph = nx.erdos_renyi_graph(100, 0.05)
    for edge in graph.edges():
        graph[edge[0]][edge[1]]['weight'] = 0.3
    return graph


@pytest.fixture
def medium_graph():
    """Medium graph (1000 nodes)."""
    graph = nx.erdos_renyi_graph(1000, 0.01)
    for edge in graph.edges():
        graph[edge[0]][edge[1]]['weight'] = 0.3
    return graph


class TestBaselinePerformance:
    """Establish performance baselines for current implementation."""
    
    @pytest.mark.benchmark(group="single-cascade")
    def test_baseline_single_cascade_small(self, benchmark, small_graph):
        """Benchmark single cascade on small graph."""
        gen = pyCascadeGenerator(small_graph, cascade_model="IC")
        
        result = benchmark(gen.generate, [0], num_cascades=1)
        assert len(result) >= 1
    
    @pytest.mark.benchmark(group="batch")
    def test_baseline_batch_small(self, benchmark, small_graph):
        """Benchmark batch generation on small graph."""
        gen = pyCascadeGenerator(small_graph, cascade_model="IC")
        
        result = benchmark(gen.generate, [0], num_cascades=100)
        assert len(result) == 100
    
    @pytest.mark.benchmark(group="single-cascade")
    @pytest.mark.slow
    def test_baseline_single_cascade_medium(self, benchmark, medium_graph):
        """Benchmark single cascade on medium graph."""
        gen = pyCascadeGenerator(medium_graph, cascade_model="IC")
        
        result = benchmark(gen.generate, [0], num_cascades=1)
        assert len(result) >= 1
