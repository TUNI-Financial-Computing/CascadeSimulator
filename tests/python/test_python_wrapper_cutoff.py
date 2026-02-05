"""Test cases for cutoff parameter in pyCascadeGenerator.

This test module verifies that the Python wrapper properly exposes and handles
the cutoff parameter for time-based cascade truncation.
"""

import pytest
import networkx as nx
from cascadesimulator import pyCascadeGenerator


@pytest.fixture
def simple_chain_graph():
    """Create a simple chain graph: 0->1->2->3->4."""
    graph = nx.DiGraph()
    graph.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4)])
    for edge in graph.edges():
        graph[edge[0]][edge[1]]['weight'] = 1.0  # 100% propagation
    return graph


@pytest.fixture
def simple_star_graph():
    """Create a star graph with center node 0 connected to 1,2,3,4."""
    graph = nx.DiGraph()
    graph.add_edges_from([(0, 1), (0, 2), (0, 3), (0, 4)])
    for edge in graph.edges():
        graph[edge[0]][edge[1]]['weight'] = 1.0  # 100% propagation
    return graph


class TestPythonWrapperCutoffBasics:
    """Test basic cutoff functionality in Python wrapper."""
    
    def test_cutoff_parameter_exists(self, simple_chain_graph):
        """Test that generate() method accepts cutoff parameter."""
        gen = pyCascadeGenerator(graph=simple_chain_graph, cascade_model="IC")
        
        # Should not raise an error
        try:
            cascade = gen.generate(seeds=[0], num_cascades=1, cutoff=2.0)
            assert True, "cutoff parameter accepted"
        except TypeError as e:
            pytest.fail(f"cutoff parameter not accepted: {e}")
    
    def test_cutoff_none_default(self, simple_chain_graph):
        """Test that cutoff=None works (default behavior)."""
        gen = pyCascadeGenerator(graph=simple_chain_graph, cascade_model="IC")
        
        cascade = gen.generate(seeds=[0], num_cascades=1, cutoff=None)
        assert cascade is not None
        assert len(cascade) >= 1  # At least the seed
    
    def test_cutoff_backwards_compatibility(self, simple_chain_graph):
        """Test that omitting cutoff parameter works (backward compatibility)."""
        gen = pyCascadeGenerator(graph=simple_chain_graph, cascade_model="IC")
        
        # Should work without cutoff parameter
        cascade = gen.generate(seeds=[0], num_cascades=1)
        assert cascade is not None


class TestPythonWrapperCutoffNonDelayed:
    """Test cutoff with non-delayed cascades."""
    
    def test_cutoff_zero_only_seeds(self, simple_chain_graph):
        """Test cutoff=0.0 returns only seed nodes."""
        gen = pyCascadeGenerator(graph=simple_chain_graph, cascade_model="IC")
        gen.cascade_model_.set_random_seed(42)
        
        cascade = gen.generate(seeds=[0], num_cascades=1, cutoff=0.0)
        
        assert len(cascade) == 1, "Only seed should be in cascade"
        assert cascade[0].node_id == 0
        assert cascade[0].time == 0.0
    
    def test_cutoff_one_generation(self, simple_chain_graph):
        """Test cutoff=1.0 includes nodes up to time 1.0."""
        gen = pyCascadeGenerator(graph=simple_chain_graph, cascade_model="IC")
        gen.cascade_model_.set_random_seed(42)
        
        cascade = gen.generate(seeds=[0], num_cascades=1, cutoff=1.0)
        
        # Should have seed (time 0) and first generation (time 1)
        node_ids = [obs.node_id for obs in cascade]
        times = [obs.time for obs in cascade]
        
        assert 0 in node_ids, "Seed should be present"
        assert 1 in node_ids, "First neighbor should propagate"
        assert all(t <= 1.0 for t in times), "All times should be <= cutoff"
        assert max(times) == 1.0, "Should reach time 1.0"
    
    def test_cutoff_reduces_cascade_size(self, simple_chain_graph):
        """Test that cutoff actually reduces cascade size."""
        gen = pyCascadeGenerator(graph=simple_chain_graph, cascade_model="IC")
        gen.cascade_model_.set_random_seed(42)
        
        # Generate without cutoff
        cascade_full = gen.generate(seeds=[0], num_cascades=1, cutoff=None)
        
        # Generate with cutoff
        gen.cascade_model_.set_random_seed(42)
        cascade_cutoff = gen.generate(seeds=[0], num_cascades=1, cutoff=2.0)
        
        assert len(cascade_cutoff) < len(cascade_full), "Cutoff should reduce cascade size"
    
    def test_cutoff_respects_time_limit(self, simple_chain_graph):
        """Test that no nodes exceed cutoff time."""
        gen = pyCascadeGenerator(graph=simple_chain_graph, cascade_model="IC")
        gen.cascade_model_.set_random_seed(42)
        
        cutoff = 2.5
        cascade = gen.generate(seeds=[0], num_cascades=1, cutoff=cutoff)
        
        for obs in cascade:
            assert obs.time <= cutoff, f"Node {obs.node_id} at time {obs.time} exceeds cutoff {cutoff}"
    
    def test_cutoff_star_graph_all_same_time(self, simple_star_graph):
        """Test cutoff with star graph where all neighbors are at same time."""
        gen = pyCascadeGenerator(graph=simple_star_graph, cascade_model="IC")
        gen.cascade_model_.set_random_seed(42)
        
        cascade = gen.generate(seeds=[0], num_cascades=1, cutoff=1.0)
        
        node_ids = [obs.node_id for obs in cascade]
        
        # Should have seed and all first-generation neighbors
        assert 0 in node_ids, "Seed should be present"
        assert set(node_ids) == {0, 1, 2, 3, 4}, "All neighbors should propagate at time 1.0"


class TestPythonWrapperCutoffDelayed:
    """Test cutoff with delayed cascades."""
    
    def test_cutoff_with_delays(self, simple_chain_graph):
        """Test cutoff works with delay times."""
        # Chain graph: 0->1->2->3->4 (node 4 has no outgoing edges)
        delays = [[1.5], [1.5], [1.5], [1.5], []]  # Only nodes 0-3 have edges
        
        gen = pyCascadeGenerator(
            graph=simple_chain_graph,
            cascade_model="IC",
            delay_times=delays
        )
        gen.cascade_model_.set_random_seed(42)
        
        cascade = gen.generate(seeds=[0], num_cascades=1, cutoff=2.0)
        
        # All nodes should be within cutoff
        for obs in cascade:
            assert obs.time <= 2.0, f"Node {obs.node_id} at time {obs.time} exceeds cutoff"
    
    def test_cutoff_zero_with_delays(self, simple_chain_graph):
        """Test cutoff=0.0 with delays returns seeds and possibly nodes with near-zero delay."""
        # Chain graph: 0->1->2->3->4 (node 4 has no outgoing edges)
        delays = [[1.0], [1.0], [1.0], [1.0], []]
        
        gen = pyCascadeGenerator(
            graph=simple_chain_graph,
            cascade_model="IC",
            delay_times=delays
        )
        gen.cascade_model_.set_random_seed(42)
        
        cascade = gen.generate(seeds=[0], num_cascades=1, cutoff=0.0)
        
        # With exponential delays, some neighbors may get very small delays (near 0.0)
        # So we check that all nodes are at time <= 0.0 and seed is present
        assert len(cascade) >= 1, "At least seed should be in cascade"
        
        # Check that seed is present
        seed_nodes = [obs.node_id for obs in cascade if obs.node_id == 0]
        assert len(seed_nodes) == 1, "Seed node should be present"
        
        # All nodes should be at time <= cutoff
        for obs in cascade:
            assert obs.time <= 0.0, f"Node {obs.node_id} at time {obs.time} exceeds cutoff 0.0"


class TestPythonWrapperCutoffBatch:
    """Test cutoff with batch generation (multiple cascades)."""
    
    def test_cutoff_with_multiple_cascades(self, simple_chain_graph):
        """Test cutoff applies to all cascades in batch."""
        gen = pyCascadeGenerator(graph=simple_chain_graph, cascade_model="IC")
        gen.cascade_model_.set_random_seed(42)
        
        cascades = gen.generate(seeds=[0], num_cascades=5, cutoff=2.0)
        
        assert len(cascades) == 5, "Should generate 5 cascades"
        
        for cascade in cascades:
            for obs in cascade:
                assert obs.time <= 2.0, f"Node {obs.node_id} at time {obs.time} exceeds cutoff"
    
    def test_cutoff_batch_consistency(self, simple_chain_graph):
        """Test that cutoff produces consistent results across multiple runs."""
        gen = pyCascadeGenerator(graph=simple_chain_graph, cascade_model="IC")
        
        # Run 1
        gen.cascade_model_.set_random_seed(12345)
        cascade1 = gen.generate(seeds=[0], num_cascades=1, cutoff=1.5)
        
        # Run 2 with same seed
        gen.cascade_model_.set_random_seed(12345)
        cascade2 = gen.generate(seeds=[0], num_cascades=1, cutoff=1.5)
        
        # Should be identical
        assert len(cascade1) == len(cascade2)
        for obs1, obs2 in zip(cascade1, cascade2):
            assert obs1.node_id == obs2.node_id
            assert obs1.time == obs2.time
            assert obs1.symptom == obs2.symptom


class TestPythonWrapperCutoffEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_cutoff_negative_disables(self, simple_chain_graph):
        """Test that negative cutoff disables time limiting."""
        gen = pyCascadeGenerator(graph=simple_chain_graph, cascade_model="IC")
        gen.cascade_model_.set_random_seed(42)
        
        cascade_no_cutoff = gen.generate(seeds=[0], num_cascades=1, cutoff=None)
        
        gen.cascade_model_.set_random_seed(42)
        cascade_negative = gen.generate(seeds=[0], num_cascades=1, cutoff=-1.0)
        
        # Should be equivalent
        assert len(cascade_no_cutoff) == len(cascade_negative)
    
    def test_cutoff_very_large_no_effect(self, simple_chain_graph):
        """Test that very large cutoff has no effect."""
        gen = pyCascadeGenerator(graph=simple_chain_graph, cascade_model="IC")
        gen.cascade_model_.set_random_seed(42)
        
        cascade_no_cutoff = gen.generate(seeds=[0], num_cascades=1, cutoff=None)
        
        gen.cascade_model_.set_random_seed(42)
        cascade_large = gen.generate(seeds=[0], num_cascades=1, cutoff=1000.0)
        
        # Should be equivalent
        assert len(cascade_no_cutoff) == len(cascade_large)
    
    def test_cutoff_between_generations(self, simple_chain_graph):
        """Test cutoff value between discrete time steps."""
        gen = pyCascadeGenerator(graph=simple_chain_graph, cascade_model="IC")
        gen.cascade_model_.set_random_seed(42)
        
        cascade = gen.generate(seeds=[0], num_cascades=1, cutoff=1.5)
        
        times = [obs.time for obs in cascade]
        
        # Should include generation 0 and 1, but not 2
        assert 0.0 in times, "Should have time 0.0"
        assert 1.0 in times, "Should have time 1.0"
        assert all(t <= 1.5 for t in times), "No time should exceed 1.5"
        assert 2.0 not in times, "Should not have time 2.0"
    
    def test_cutoff_with_empty_seeds(self, simple_chain_graph):
        """Test cutoff with empty seed set raises ValueError."""
        gen = pyCascadeGenerator(graph=simple_chain_graph, cascade_model="IC")
        
        # Empty seeds should raise ValueError
        with pytest.raises(ValueError, match="seeds cannot be empty"):
            cascade = gen.generate(seeds=[], num_cascades=1, cutoff=2.0)
    
    def test_cutoff_with_multiple_seeds(self, simple_chain_graph):
        """Test cutoff with multiple seed nodes."""
        gen = pyCascadeGenerator(graph=simple_chain_graph, cascade_model="IC")
        gen.cascade_model_.set_random_seed(42)
        
        cascade = gen.generate(seeds=[0, 2], num_cascades=1, cutoff=1.0)
        
        node_ids = [obs.node_id for obs in cascade]
        
        # Both seeds should be present
        assert 0 in node_ids, "Seed 0 should be present"
        assert 2 in node_ids, "Seed 2 should be present"
        
        # All times should be within cutoff
        for obs in cascade:
            assert obs.time <= 1.0


class TestPythonWrapperCutoffWithSymptoms:
    """Test cutoff interaction with symptom probabilities."""
    
    def test_cutoff_with_symptoms(self, simple_chain_graph):
        """Test that cutoff works correctly with symptom probabilities."""
        q = [0.5] * 5  # 50% symptom probability for all nodes
        
        gen = pyCascadeGenerator(
            graph=simple_chain_graph,
            cascade_model="IC",
            q=q
        )
        gen.cascade_model_.set_random_seed(42)
        
        cascade = gen.generate(seeds=[0], num_cascades=1, cutoff=2.0)
        
        # Check that all nodes are within cutoff
        for obs in cascade:
            assert obs.time <= 2.0
            # Symptom should be 0.0 or 1.0
            assert obs.symptom in [0.0, 1.0]


class TestPythonWrapperCutoffNetworkX:
    """Test cutoff with various NetworkX graph types."""
    
    def test_cutoff_erdos_renyi(self):
        """Test cutoff with Erdos-Renyi random graph."""
        graph = nx.erdos_renyi_graph(50, 0.1, directed=True)
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 0.8
        
        gen = pyCascadeGenerator(graph=graph, cascade_model="IC")
        gen.cascade_model_.set_random_seed(42)
        
        cascade = gen.generate(seeds=[0], num_cascades=1, cutoff=3.0)
        
        for obs in cascade:
            assert obs.time <= 3.0
    
    def test_cutoff_complete_graph(self):
        """Test cutoff with complete graph."""
        graph = nx.complete_graph(10, create_using=nx.DiGraph())
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 0.5
        
        gen = pyCascadeGenerator(graph=graph, cascade_model="IC")
        gen.cascade_model_.set_random_seed(42)
        
        cascade = gen.generate(seeds=[0], num_cascades=1, cutoff=1.0)
        
        # All nodes at time <= 1.0 (direct neighbors at time 1.0)
        for obs in cascade:
            assert obs.time <= 1.0
    
    def test_cutoff_path_graph(self):
        """Test cutoff with path graph."""
        graph = nx.path_graph(10, create_using=nx.DiGraph())
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 1.0
        
        gen = pyCascadeGenerator(graph=graph, cascade_model="IC")
        gen.cascade_model_.set_random_seed(42)
        
        cascade = gen.generate(seeds=[0], num_cascades=1, cutoff=5.0)
        
        # Should propagate along path up to time 5
        node_ids = [obs.node_id for obs in cascade]
        times = [obs.time for obs in cascade]
        
        assert all(t <= 5.0 for t in times)
        # With probability 1.0, should reach nodes 0-5
        assert 0 in node_ids
        assert len(node_ids) <= 6  # At most 6 nodes (0 through 5)


class TestPythonWrapperCutoffPerformance:
    """Test that cutoff actually provides performance benefits (basic checks)."""
    
    def test_cutoff_reduces_computation(self, simple_chain_graph):
        """Test that cutoff results in smaller cascades (indirect performance measure)."""
        # Create a longer chain
        graph = nx.DiGraph()
        n = 100
        graph.add_edges_from([(i, i+1) for i in range(n-1)])
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 1.0
        
        gen = pyCascadeGenerator(graph=graph, cascade_model="IC")
        gen.cascade_model_.set_random_seed(42)
        
        # Full cascade
        cascade_full = gen.generate(seeds=[0], num_cascades=1, cutoff=None)
        
        # With cutoff
        gen.cascade_model_.set_random_seed(42)
        cascade_cutoff = gen.generate(seeds=[0], num_cascades=1, cutoff=10.0)
        
        # Cutoff cascade should be much smaller
        assert len(cascade_cutoff) < len(cascade_full) / 2, "Cutoff should significantly reduce cascade size"
        assert len(cascade_cutoff) <= 11, f"Should have at most 11 nodes (0-10), got {len(cascade_cutoff)}"
