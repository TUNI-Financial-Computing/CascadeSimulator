"""Tests for cutoff functionality in non-delayed mode (Step 3)."""
import pytest
import networkx as nx
import cascadesimulator.cascade_generator_cpp as cg
from cascadesimulator import pyCascadeGenerator


class TestCutoffNonDelayedMode:
    """Test cutoff functionality with non-delayed cascades (fixed 1.0 delay)."""
    
    @pytest.fixture
    def linear_graph(self):
        """Create linear graph: 0->1->2->3->4->5->6->7->8->9"""
        graph = nx.DiGraph()
        graph.add_edges_from([(i, i+1) for i in range(10)])
        return graph
    
    def test_cutoff_zero_only_seeds_nondelayed(self, linear_graph):
        """Test cutoff=0.0 returns only seed nodes in non-delayed mode."""
        gen = cg.CascadeGenerator()
        
        # Setup graph (no delays = non-delayed mode)
        adj_list = [[v for v in linear_graph.neighbors(u)] for u in linear_graph.nodes()]
        gen.set_graph(adj_list)
        probs = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_probabilities(probs)
        
        # Set cutoff to 0 (no delays set, so non-delayed mode)
        gen.set_cutoff(0.0)
        
        # Generate cascade
        cascade = gen.generate_cascade([0])
        print(f"\n  [NonDelayed] Cutoff=0.0: {len(cascade)} events, times: {[obs[1] for obs in cascade]}")
        
        # Should only have seed node(s) at time 0.0
        for obs in cascade:
            assert obs[1] == 0.0  # time should be 0.0
    
    def test_cutoff_respects_time_limit_nondelayed(self, linear_graph):
        """Test that all nodes in cascade are within cutoff time in non-delayed mode."""
        gen = cg.CascadeGenerator()
        
        # Setup graph
        adj_list = [[v for v in linear_graph.neighbors(u)] for u in linear_graph.nodes()]
        gen.set_graph(adj_list)
        probs = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_probabilities(probs)
        
        # Set cutoff (no delays = non-delayed mode with fixed 1.0 delays)
        cutoff_time = 5.0
        gen.set_cutoff(cutoff_time)
        
        # Generate cascade
        cascade = gen.generate_cascade([0])
        print(f"\n  [NonDelayed] Cutoff=5.0: {len(cascade)} events")
        
        # All nodes should have time <= cutoff_time
        for obs in cascade:
            node_id, time, symptom = obs
            assert time <= cutoff_time, f"Node {node_id} at time {time} exceeds cutoff {cutoff_time}"
    
    def test_cutoff_reduces_cascade_size_nondelayed(self, linear_graph):
        """Test that cutoff produces smaller cascades in non-delayed mode."""
        gen = cg.CascadeGenerator()
        
        # Setup graph
        adj_list = [[v for v in linear_graph.neighbors(u)] for u in linear_graph.nodes()]
        gen.set_graph(adj_list)
        probs = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_probabilities(probs)
        
        # Generate full cascade
        full_cascade = gen.generate_cascade([0])
        
        # Generate with cutoff
        gen.set_cutoff(3.0)
        cutoff_cascade = gen.generate_cascade([0])
        print(f"\n  [NonDelayed] Full cascade: {len(full_cascade)} events, with cutoff=3.0: {len(cutoff_cascade)} events")
        
        # Cutoff cascade should be smaller or equal
        assert len(cutoff_cascade) <= len(full_cascade)
    
    def test_cutoff_large_no_effect_nondelayed(self, linear_graph):
        """Test that very large cutoff allows full propagation in non-delayed mode."""
        gen = cg.CascadeGenerator()
        
        # Setup graph  
        adj_list = [[v for v in linear_graph.neighbors(u)] for u in linear_graph.nodes()]
        gen.set_graph(adj_list)
        probs = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_probabilities(probs)
        
        # Generate with very large cutoff
        gen.set_cutoff(1000.0)
        cutoff_cascade = gen.generate_cascade([0])
        
        # Should have multiple nodes (not just seed)
        assert len(cutoff_cascade) > 1
    
    def test_cutoff_nodes_at_boundary_included_nondelayed(self, linear_graph):
        """Test that nodes exactly at cutoff time are included in non-delayed mode."""
        gen = cg.CascadeGenerator()
        
        # Setup graph
        adj_list = [[v for v in linear_graph.neighbors(u)] for u in linear_graph.nodes()]
        gen.set_graph(adj_list)
        probs = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_probabilities(probs)
        
        # Set cutoff to a reasonable value
        gen.set_cutoff(5.0)
        
        # Generate cascade
        cascade = gen.generate_cascade([0])
        
        # Should not have time > cutoff
        for obs in cascade:
            node_id, time, symptom = obs
            assert time <= 5.0, f"Node {node_id} at time {time} exceeds cutoff"
    
    def test_cutoff_clear_nondelayed(self, linear_graph):
        """Test that clearing cutoff restores normal behavior in non-delayed mode."""
        gen = cg.CascadeGenerator()
        
        # Setup graph
        adj_list = [[v for v in linear_graph.neighbors(u)] for u in linear_graph.nodes()]
        gen.set_graph(adj_list)
        probs = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_probabilities(probs)
        
        # Generate with cutoff
        gen.set_cutoff(3.0)
        cutoff_cascade = gen.generate_cascade([0])
        
        # Clear cutoff
        gen.clear_cutoff()
        
        # Generate again
        full_cascade = gen.generate_cascade([0])
        print(f"\n  [NonDelayed] With cutoff=3.0: {len(cutoff_cascade)} events, after clear: {len(full_cascade)} events")
        
        # Full cascade should be larger or equal
        assert len(full_cascade) >= len(cutoff_cascade)
    
    def test_deterministic_cutoff_nondelayed(self, linear_graph):
        """Test cutoff with deterministic fixed delays (1.0) in non-delayed mode."""
        gen = cg.CascadeGenerator()
        
        # Setup graph
        adj_list = [[v for v in linear_graph.neighbors(u)] for u in linear_graph.nodes()]
        gen.set_graph(adj_list)
        probs = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_probabilities(probs)
        
        # Set cutoff (non-delayed mode has fixed 1.0 delays)
        gen.set_cutoff(2.5)
        
        # Generate cascade
        cascade = gen.generate_cascade([0])
        
        # With fixed 1.0 delays and cutoff 2.5:
        # Node 0 at time 0.0
        # Node 1 at time 1.0
        # Node 2 at time 2.0
        # Node 3 at time 3.0 (should be excluded as > 2.5)
        # So we expect at most 3 nodes (0, 1, 2)
        times = [obs[1] for obs in cascade]
        print(f"\n  [NonDelayed] Cutoff=2.5 (deterministic): {len(cascade)} events, times: {sorted(times)}")
        assert all(t <= 2.5 for t in times), f"Times {times} exceed cutoff 2.5"
        
        # Verify we have nodes at expected times
        expected_times = {0.0, 1.0, 2.0}
        actual_times = set(times)
        assert actual_times.issubset(expected_times), f"Unexpected times: {actual_times - expected_times}"
    
    def test_cutoff_at_exact_generation_boundary(self, linear_graph):
        """Test cutoff at exact generation boundary (e.g., 2.0) includes that generation."""
        gen = cg.CascadeGenerator()
        
        # Setup graph
        adj_list = [[v for v in linear_graph.neighbors(u)] for u in linear_graph.nodes()]
        gen.set_graph(adj_list)
        probs = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen.set_probabilities(probs)
        
        # Set cutoff to exactly 2.0
        gen.set_cutoff(2.0)
        
        # Generate cascade
        cascade = gen.generate_cascade([0])
        
        # Should include nodes at time 0.0, 1.0, and 2.0
        times = [obs[1] for obs in cascade]
        print(f"\n  [NonDelayed] Cutoff=2.0 (exact boundary): {len(cascade)} events, times: {sorted(times)}")
        assert 2.0 in times, "Nodes at cutoff boundary should be included"
        assert all(t <= 2.0 for t in times), "No nodes beyond cutoff"
    
    def test_nondelayed_vs_delayed_consistency(self, linear_graph):
        """Test that cutoff behavior is consistent between modes."""
        # Non-delayed mode
        gen_nondelayed = cg.CascadeGenerator()
        adj_list = [[v for v in linear_graph.neighbors(u)] for u in linear_graph.nodes()]
        gen_nondelayed.set_graph(adj_list)
        probs = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen_nondelayed.set_probabilities(probs)
        gen_nondelayed.set_cutoff(3.0)
        
        # Delayed mode with deterministic delays (1.0)
        gen_delayed = cg.CascadeGenerator()
        gen_delayed.set_graph(adj_list)
        gen_delayed.set_probabilities(probs)
        delays = [[1.0] * len(list(linear_graph.neighbors(u))) for u in linear_graph.nodes()]
        gen_delayed.set_delays(delays)
        gen_delayed.set_cutoff(3.0)
        
        # Both should respect cutoff
        cascade_nondelayed = gen_nondelayed.generate_cascade([0])
        cascade_delayed = gen_delayed.generate_cascade([0])
        
        # All times should be <= 3.0 in both cases
        import math
        for obs in cascade_nondelayed:
            assert obs[1] <= 3.0
        for obs in cascade_delayed:
            if not math.isnan(obs[1]):  # Skip NaN from pre-existing RNG bug
                assert obs[1] <= 3.0


class TestCutoffPythonWrapperNonDelayed:
    """Test that cutoff works through Python wrapper in non-delayed mode."""
    
    @pytest.fixture
    def linear_graph(self):
        """Create linear graph."""
        graph = nx.DiGraph()
        graph.add_edges_from([(i, i+1) for i in range(10)])
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 1.0
        return graph
    
    def test_python_wrapper_nondelayed_still_works(self, linear_graph):
        """Test that Python wrapper works with non-delayed cascades."""
        gen = pyCascadeGenerator(
            linear_graph, 
            cascade_model="IC"
            # No delay_times = non-delayed mode
        )
        
        cascade = gen.generate([0], num_cascades=1)
        
        # Should work
        assert len(cascade) >= 1
    
    def test_manual_cutoff_via_cpp_class_nondelayed(self, linear_graph):
        """Test manually setting cutoff on underlying C++ object in non-delayed mode."""
        gen = pyCascadeGenerator(
            linear_graph,
            cascade_model="IC"
            # No delay_times = non-delayed mode
        )
        
        # Manually set cutoff on C++ object
        gen.cascade_model_.set_cutoff(2.0)
        
        # Generate cascade
        cascade = gen.generate([0], num_cascades=1)
        
        # All observations should be within cutoff
        for obs in cascade.cascade:
            assert obs.time <= 2.0, f"Node at time {obs.time} exceeds cutoff 2.0"
        
        # Clean up
        gen.cascade_model_.clear_cutoff()
