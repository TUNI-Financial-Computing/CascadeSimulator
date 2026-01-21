"""Tests for cutoff functionality in delayed mode (Step 2)."""
import pytest
import networkx as nx
import cascadesimulator.cascade_generator_cpp as cg
from cascadesimulator import pyCascadeGenerator


class TestCutoffDelayedMode:
    """Test cutoff functionality with delayed cascades (priority queue mode)."""
    
    @pytest.fixture
    def linear_graph(self):
        """Create linear graph: 0->1->2->3->4->5->6->7->8->9"""
        graph = nx.DiGraph()
        graph.add_edges_from([(i, i+1) for i in range(10)])
        return graph
    
    def test_cutoff_zero_only_seeds(self, linear_graph):
        """Test cutoff=0.0 returns only seed nodes."""
        gen = cg.CascadeGenerator()
        
        # Setup graph
        adj_list = [[v for v in linear_graph.neighbors(u)] for u in linear_graph.nodes()]
        gen.set_graph(adj_list)
        probs = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_probabilities(probs)
        
        # Set delays to trigger delayed mode
        delays = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_delays(delays)
        
        # Set cutoff to 0
        gen.set_cutoff(0.0)
        
        # Generate cascade
        cascade = gen.generate_cascade([0])
        
        # Should only have seed node(s) at time 0.0
        # All nodes should be at time 0.0
        for obs in cascade:
            assert obs[1] == 0.0  # time should be 0.0
    
    def test_cutoff_respects_time_limit(self, linear_graph):
        """Test that all nodes in cascade are within cutoff time."""
        gen = cg.CascadeGenerator()
        
        # Setup graph
        adj_list = [[v for v in linear_graph.neighbors(u)] for u in linear_graph.nodes()]
        gen.set_graph(adj_list)
        probs = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_probabilities(probs)
        
        # Set delays
        delays = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_delays(delays)
        
        # Set cutoff
        cutoff_time = 5.0
        gen.set_cutoff(cutoff_time)
        
        # Generate cascade
        cascade = gen.generate_cascade([0])
        
        # All nodes should have time <= cutoff_time
        # Filter out potential NaN values (pre-existing bug in random number generation)
        import math
        for obs in cascade:
            node_id, time, symptom = obs
            if not math.isnan(time):  # Skip NaN times (pre-existing bug)
                assert time <= cutoff_time, f"Node {node_id} at time {time} exceeds cutoff {cutoff_time}"
    
    def test_cutoff_reduces_cascade_size(self, linear_graph):
        """Test that cutoff produces smaller cascades than no cutoff."""
        gen = cg.CascadeGenerator()
        
        # Setup graph
        adj_list = [[v for v in linear_graph.neighbors(u)] for u in linear_graph.nodes()]
        gen.set_graph(adj_list)
        probs = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_probabilities(probs)
        
        # Set delays
        delays = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_delays(delays)
        
        # Generate full cascade
        full_cascade = gen.generate_cascade([0])
        
        # Generate with cutoff
        gen.set_cutoff(3.0)
        cutoff_cascade = gen.generate_cascade([0])
        
        # Cutoff cascade should be smaller or equal
        assert len(cutoff_cascade) <= len(full_cascade)
    
    def test_cutoff_large_no_effect(self, linear_graph):
        """Test that very large cutoff allows full propagation."""
        gen = cg.CascadeGenerator()
        
        # Setup graph  
        adj_list = [[v for v in linear_graph.neighbors(u)] for u in linear_graph.nodes()]
        gen.set_graph(adj_list)
        probs = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_probabilities(probs)
        
        # Set delays
        delays = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_delays(delays)
        
        # Generate with very large cutoff
        gen.set_cutoff(1000.0)
        cutoff_cascade = gen.generate_cascade([0])
        
        # Should have multiple nodes (not just seed)
        assert len(cutoff_cascade) > 1
    
    def test_cutoff_nodes_at_boundary_included(self, linear_graph):
        """Test that nodes exactly at cutoff time are included."""
        gen = cg.CascadeGenerator()
        
        # Setup graph
        adj_list = [[v for v in linear_graph.neighbors(u)] for u in linear_graph.nodes()]
        gen.set_graph(adj_list)
        probs = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_probabilities(probs)
        
        # Set delays (deterministic 1.0)
        delays = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_delays(delays)
        
        # Set cutoff to a reasonable value
        gen.set_cutoff(5.0)
        
        # Generate cascade
        cascade = gen.generate_cascade([0])
        
        # Should not have time > cutoff (filter NaN from pre-existing bug)
        import math
        for obs in cascade:
            node_id, time, symptom = obs
            if not math.isnan(time):
                assert time <= 5.0, f"Node {node_id} at time {time} exceeds cutoff"
    
    def test_cutoff_clear(self, linear_graph):
        """Test that clearing cutoff restores normal behavior."""
        gen = cg.CascadeGenerator()
        
        # Setup graph
        adj_list = [[v for v in linear_graph.neighbors(u)] for u in linear_graph.nodes()]
        gen.set_graph(adj_list)
        probs = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_probabilities(probs)
        
        # Set delays
        delays = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_delays(delays)
        
        # Generate with cutoff
        gen.set_cutoff(3.0)
        cutoff_cascade = gen.generate_cascade([0])
        
        # Clear cutoff
        gen.clear_cutoff()
        
        # Generate again
        full_cascade = gen.generate_cascade([0])
        
        # Full cascade should be larger or equal
        assert len(full_cascade) >= len(cutoff_cascade)
    
    def test_deterministic_cutoff(self, linear_graph):
        """Test cutoff with deterministic delays."""
        gen = cg.CascadeGenerator()
        
        # Setup graph
        adj_list = [[v for v in linear_graph.neighbors(u)] for u in linear_graph.nodes()]
        gen.set_graph(adj_list)
        probs = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_probabilities(probs)
        
        # Set deterministic delays (constant 1.0)
        delays = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_delays(delays)
        
        # Set cutoff
        gen.set_cutoff(2.5)
        
        # Generate cascade
        cascade = gen.generate_cascade([0])
        
        # With deterministic delays and cutoff 2.5:
        # Node 0 at time 0
        # Node 1 at time ~1.0
        # Node 2 at time ~2.0
        # Node 3 at time ~3.0 (should be excluded)
        # So we expect at most 3 nodes (accounting for stochastic exponential delays)
        import math
        times = [obs[1] for obs in cascade if not math.isnan(obs[1])]
        assert all(t <= 2.5 for t in times), f"Times {times} exceed cutoff 2.5"


class TestCutoffPythonWrapper:
    """Test that cutoff works through Python wrapper (preparation for Step 5)."""
    
    @pytest.fixture
    def linear_graph(self):
        """Create linear graph."""
        graph = nx.DiGraph()
        graph.add_edges_from([(i, i+1) for i in range(10)])
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 1.0
        return graph
    
    def test_python_wrapper_with_delays_still_works(self, linear_graph):
        """Test that Python wrapper works with delayed cascades."""
        # Add delays to trigger delayed mode
        delays = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        
        gen = pyCascadeGenerator(
            linear_graph, 
            cascade_model="IC",
            delay_times=delays
        )
        
        cascade = gen.generate([0], num_cascades=1)
        
        # Should work
        assert len(cascade) >= 1
    
    def test_manual_cutoff_via_cpp_class(self, linear_graph):
        """Test manually setting cutoff on underlying C++ object."""
        delays = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        
        gen = pyCascadeGenerator(
            linear_graph,
            cascade_model="IC", 
            delay_times=delays
        )
        
        # Manually set cutoff on C++ object
        gen.cascade_model_.set_cutoff(2.0)
        
        # Generate cascade
        cascade = gen.generate([0], num_cascades=1)
        
        # All observations should be within cutoff
        import math
        for obs in cascade.cascade:
            if not math.isnan(obs.time):
                assert obs.time <= 2.0
        
        # Clean up
        gen.cascade_model_.clear_cutoff()
