"""Unit tests for pyCascadeGenerator class."""

import pytest
import networkx as nx
from cascadesimulator import pyCascadeGenerator


class TestPyCascadeGeneratorInit:
    """Test initialization and configuration."""
    
    def test_init_basic(self):
        """Test basic initialization with NetworkX graph."""
        graph = nx.erdos_renyi_graph(100, 0.1)
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 0.5
        
        gen = pyCascadeGenerator(
            graph=graph,
            cascade_model="IC"
        )
        
        assert gen is not None
    
    def test_init_with_symptom_probs(self):
        """Test initialization with symptom probabilities."""
        graph = nx.erdos_renyi_graph(100, 0.1)
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 0.5
        
        q = [0.5] * 100
        gen = pyCascadeGenerator(
            graph=graph,
            cascade_model="IC",
            q=q
        )
        
        assert gen is not None
    
    def test_init_with_delays(self):
        """Test initialization with delay times."""
        graph = nx.erdos_renyi_graph(10, 0.3)
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 0.5
        
        delays = [[1.0] * len(list(graph.neighbors(u))) for u in graph.nodes()]
        
        gen = pyCascadeGenerator(
            graph=graph,
            cascade_model="IC",
            delay_times=delays
        )
        
        assert gen is not None
    
    def test_init_unsupported_model(self):
        """Test that unsupported cascade models raise error."""
        graph = nx.erdos_renyi_graph(10, 0.1)
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 0.5
        
        with pytest.raises(NotImplementedError):
            gen = pyCascadeGenerator(
                graph=graph,
                cascade_model="LT"  # Linear Threshold not implemented
            )
    
    def test_init_invalid_node_ids(self):
        """Test that non-sequential node IDs raise error."""
        graph = nx.Graph()
        graph.add_edges_from([(0, 2), (2, 5)])  # Missing 1, 3, 4
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 0.5
        
        # Should fail assertion in __init__
        with pytest.raises(AssertionError):
            gen = pyCascadeGenerator(graph=graph, cascade_model="IC")


class TestPyCascadeGeneratorGenerate:
    """Test cascade generation methods."""
    
    @pytest.fixture
    def simple_graph(self):
        """Create simple test graph."""
        graph = nx.path_graph(10)  # 0-1-2-3-4-5-6-7-8-9
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 1.0  # Full propagation
        return graph
    
    def test_generate_single_cascade(self, simple_graph):
        """Test generating a single cascade."""
        gen = pyCascadeGenerator(simple_graph, cascade_model="IC")
        cascade = gen.generate([0], num_cascades=1)
        
        # Should return single Cascade object (not list)
        assert hasattr(cascade, 'cascade')
        assert len(cascade) >= 1  # At least seed
    
    def test_generate_multiple_cascades(self, simple_graph):
        """Test generating multiple cascades."""
        gen = pyCascadeGenerator(simple_graph, cascade_model="IC")
        cascades = gen.generate([0], num_cascades=10)
        
        # Should return list of Cascade objects
        assert isinstance(cascades, list)
        assert len(cascades) == 10
        for cascade in cascades:
            assert len(cascade) >= 1
    
    def test_cascade_contains_seed(self, simple_graph):
        """Test that generated cascade contains seed nodes."""
        gen = pyCascadeGenerator(simple_graph, cascade_model="IC")
        cascade = gen.generate([0, 5], num_cascades=1)
        
        node_ids = [obs.node_id for obs in cascade.cascade]
        assert 0 in node_ids
        assert 5 in node_ids
    
    def test_cascade_observation_structure(self, simple_graph):
        """Test that Observation objects have correct structure."""
        gen = pyCascadeGenerator(simple_graph, cascade_model="IC")
        cascade = gen.generate([0], num_cascades=1)
        
        obs = cascade[0]
        assert hasattr(obs, 'node_id')
        assert hasattr(obs, 'time')
        assert hasattr(obs, 'symptom')
        assert isinstance(obs.node_id, int)
        assert isinstance(obs.time, float)
        assert isinstance(obs.symptom, float)
    
    def test_cascade_indexing(self, simple_graph):
        """Test that Cascade objects support indexing."""
        gen = pyCascadeGenerator(simple_graph, cascade_model="IC")
        cascade = gen.generate([0], num_cascades=1)
        
        # Should support indexing
        first_obs = cascade[0]
        assert first_obs is not None
        
        # Should support len()
        size = len(cascade)
        assert size >= 1
    
    def test_generate_with_symptom_probs(self, simple_graph):
        """Test cascade generation with symptom probabilities."""
        q = [1.0] * 10  # All symptomatic
        gen = pyCascadeGenerator(simple_graph, cascade_model="IC", q=q)
        cascade = gen.generate([0], num_cascades=1)
        
        # All non-seed nodes should be symptomatic (symptom=1.0)
        # Note: Seeds have symptom=0.0 by default
        for i in range(1, len(cascade)):
            obs = cascade[i]
            assert obs.symptom == 1.0
    
    def test_generate_zero_probability(self):
        """Test that zero edge weights produce seed-only cascades."""
        graph = nx.path_graph(10)
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 0.0  # No propagation
        
        gen = pyCascadeGenerator(graph, cascade_model="IC")
        cascade = gen.generate([0], num_cascades=1)
        
        # Only seed should be in cascade
        assert len(cascade) == 1
        assert cascade[0].node_id == 0
    
    def test_generate_empty_seed(self, simple_graph):
        """Test that empty seed produces empty cascade."""
        gen = pyCascadeGenerator(simple_graph, cascade_model="IC")
        cascade = gen.generate([], num_cascades=1)
        
        # Empty seed should produce empty cascade
        assert len(cascade) == 0


class TestNetworkXIntegration:
    """Test integration with various NetworkX graph types."""
    
    def test_erdos_renyi_graph(self):
        """Test with Erdős-Rényi random graph."""
        graph = nx.erdos_renyi_graph(100, 0.05)
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 0.3
        
        gen = pyCascadeGenerator(graph, cascade_model="IC")
        cascade = gen.generate([0], num_cascades=1)
        
        assert len(cascade) >= 1
    
    def test_barabasi_albert_graph(self):
        """Test with Barabási-Albert preferential attachment graph."""
        graph = nx.barabasi_albert_graph(100, 3)
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 0.3
        
        gen = pyCascadeGenerator(graph, cascade_model="IC")
        cascade = gen.generate([0], num_cascades=1)
        
        assert len(cascade) >= 1
    
    def test_complete_graph(self):
        """Test with complete graph."""
        graph = nx.complete_graph(20)
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 1.0
        
        gen = pyCascadeGenerator(graph, cascade_model="IC")
        cascade = gen.generate([0], num_cascades=1)
        
        # With p=1.0, should infect all nodes
        assert len(cascade) == 20
    
    def test_empty_graph(self):
        """Test with empty graph (single node)."""
        graph = nx.Graph()
        graph.add_node(0)
        
        gen = pyCascadeGenerator(graph, cascade_model="IC")
        cascade = gen.generate([0], num_cascades=1)
        
        # Only seed
        assert len(cascade) == 1


class TestBackwardCompatibility:
    """Ensure all existing code continues to work."""
    
    def test_readme_example_works(self):
        """Test that README example still works."""
        from random import random
        import networkx as nx
        from cascadesimulator import pyCascadeGenerator
        
        # Exact code from README
        graph = nx.erdos_renyi_graph(100, 0.1)
        
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 0.1 + 0.2 * random()
        
        q = [0.5 + 0.5 * random() for _ in graph.nodes()]
        
        cascade_generator = pyCascadeGenerator(
            graph=graph,
            cascade_model="IC",
            q=q
        )
        
        seed = [0]
        num_cascades = 10
        
        cascades = cascade_generator.generate(seed, num_cascades)
        
        # Should work without errors
        assert len(cascades) == 10
        
        # Access methods from README
        cascade = cascades[0]
        assert len(cascade) >= 1
        
        # Access observation
        obs = cascade[0]
        assert obs is not None
    
    def test_existing_api_unchanged(self):
        """Test that existing API signatures work."""
        import networkx as nx
        from cascadesimulator import pyCascadeGenerator
        
        graph = nx.erdos_renyi_graph(50, 0.1)
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 0.5
        
        # All these should work
        gen1 = pyCascadeGenerator(graph, "IC")
        gen2 = pyCascadeGenerator(graph=graph, cascade_model="IC")
        gen3 = pyCascadeGenerator(graph, "IC", q=[0.5]*50)
        
        # All generate methods should work
        c1 = gen1.generate([0])
        c2 = gen2.generate([0], 1)
        c3 = gen3.generate([0], num_cascades=5)
        
        assert c1 is not None
        assert c2 is not None
        assert len(c3) == 5
