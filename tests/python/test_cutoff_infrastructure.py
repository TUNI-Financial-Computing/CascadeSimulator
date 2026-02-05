"""Tests for cutoff feature infrastructure (Step 1)."""

import pytest
import networkx as nx
import cascadesimulator.cascade_generator_cpp as cg
from cascadesimulator import pyCascadeGenerator


class TestCutoffInfrastructure:
    """Test that cutoff methods exist and can be called."""
    
    @pytest.fixture
    def simple_graph(self):
        """Create simple test graph."""
        graph = nx.path_graph(10)
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 1.0
        return graph
    
    def test_set_cutoff_method_exists(self):
        """Test that set_cutoff method exists in C++ class."""
        gen = cg.CascadeGenerator()
        assert hasattr(gen, 'set_cutoff')
    
    def test_clear_cutoff_method_exists(self):
        """Test that clear_cutoff method exists in C++ class."""
        gen = cg.CascadeGenerator()
        assert hasattr(gen, 'clear_cutoff')
    
    def test_set_cutoff_accepts_positive_value(self):
        """Test that set_cutoff accepts positive values."""
        gen = cg.CascadeGenerator()
        # Should not raise an error
        gen.set_cutoff(5.0)
    
    def test_set_cutoff_accepts_zero(self):
        """Test that set_cutoff accepts zero."""
        gen = cg.CascadeGenerator()
        # Should not raise an error
        gen.set_cutoff(0.0)
    
    def test_set_cutoff_accepts_negative(self):
        """Test that set_cutoff accepts negative (disables cutoff)."""
        gen = cg.CascadeGenerator()
        # Should not raise an error
        gen.set_cutoff(-1.0)
    
    def test_clear_cutoff_works(self):
        """Test that clear_cutoff can be called."""
        gen = cg.CascadeGenerator()
        gen.set_cutoff(5.0)
        # Should not raise an error
        gen.clear_cutoff()
    
    def test_cascade_generation_still_works_with_cutoff_set(self, simple_graph):
        """Test that cascade generation works after setting cutoff (even if not implemented yet)."""
        # Create generator
        gen = cg.CascadeGenerator()
        
        # Setup graph
        adj_list = [[v for v in simple_graph.neighbors(u)] for u in simple_graph.nodes()]
        gen.set_graph(adj_list)
        probs = [[simple_graph[u][v]['weight'] for v in simple_graph.neighbors(u)] for u in simple_graph.nodes()]
        gen.set_probabilities(probs)
        
        # Set cutoff (should not break existing functionality)
        gen.set_cutoff(5.0)
        
        # Generate cascade
        cascade = gen.generate_cascade([0])
        print(f"\n  [Infrastructure] Cascade with cutoff=5.0: {len(cascade)} events")
        
        # Should still work (may or may not respect cutoff yet)
        assert len(cascade) > 0
    
    def test_cascade_generation_still_works_after_clear_cutoff(self, simple_graph):
        """Test that cascade generation works after clearing cutoff."""
        # Create generator
        gen = cg.CascadeGenerator()
        
        # Setup graph
        adj_list = [[v for v in simple_graph.neighbors(u)] for u in simple_graph.nodes()]
        gen.set_graph(adj_list)
        probs = [[simple_graph[u][v]['weight'] for v in simple_graph.neighbors(u)] for u in simple_graph.nodes()]
        gen.set_probabilities(probs)
        
        # Set and clear cutoff
        gen.set_cutoff(5.0)
        gen.clear_cutoff()
        
        # Generate cascade
        cascade = gen.generate_cascade([0])
        print(f"\n  [Infrastructure] Cascade after clear_cutoff: {len(cascade)} events")
        
        # Should still work
        assert len(cascade) > 0
    
    def test_python_wrapper_still_works(self, simple_graph):
        """Test that Python wrapper still works after C++ changes."""
        gen = pyCascadeGenerator(simple_graph, cascade_model="IC")
        cascade = gen.generate([0], num_cascades=1)
        
        # Should still work
        assert len(cascade) >= 1
