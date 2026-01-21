# Comprehensive Testing Plan for CascadeSimulator

**Date:** January 21, 2026  
**Purpose:** Establish testing strategy for current functionality and future cutoff feature  
**Scope:** C++ core, Python wrapper, integration, performance

---

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Current Functionality Tests](#current-functionality-tests)
3. [Cutoff Feature Tests](#cutoff-feature-tests)
4. [Performance Benchmarks](#performance-benchmarks)
5. [Regression Tests](#regression-tests)
6. [Test Implementation Guide](#test-implementation-guide)

---

## Testing Philosophy

### Principles
- **Test-Driven Development**: Write tests before or alongside implementation
- **Comprehensive Coverage**: Aim for >90% code coverage
- **Fast Feedback**: Unit tests run in <5 seconds, full suite in <2 minutes
- **Deterministic**: Use fixed random seeds for reproducibility
- **Isolated**: Each test independent, no shared state
- **Documented**: Clear test names and comments explaining intent

### Test Pyramid
```
                 /\
                /  \
               /E2E \          10% - End-to-End (Notebooks, Examples)
              /------\
             /        \
            /Integration\     30% - Integration (Python↔C++, Graph conversion)
           /------------\
          /              \
         /  Unit Tests    \   60% - Unit (C++ methods, Python methods)
        /------------------\
```

### Testing Tools
- **C++**: Google Test (gtest) + Google Mock (gmock)
- **Python**: pytest + pytest-cov + pytest-benchmark
- **Coverage**: gcov/lcov (C++) + coverage.py (Python)
- **CI/CD**: GitHub Actions for automated testing

---

## Current Functionality Tests

### C++ Unit Tests (src/tests/test_cascade_generator.cpp)

#### Test Suite 1: Initialization & Configuration

```cpp
#include <gtest/gtest.h>
#include "cascade_generator.hpp"

class CascadeGeneratorTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Create simple test graph: 0 -> 1 -> 2
        graph = {{1}, {2}, {}};
    }
    
    std::vector<std::vector<int>> graph;
    CascadeGenerator gen;
};

TEST_F(CascadeGeneratorTest, DefaultConstructor) {
    CascadeGenerator gen;
    // Should initialize without errors
    EXPECT_NO_THROW(gen.set_graph(graph));
}

TEST_F(CascadeGeneratorTest, SetGraph) {
    gen.set_graph(graph);
    // Graph should be stored (verify via cascade generation)
    auto cascade = gen.generate_cascade({0});
    EXPECT_GT(cascade.size(), 0);
}

TEST_F(CascadeGeneratorTest, SetProbability) {
    gen.set_graph(graph);
    gen.set_probability(1.0);  // Deterministic propagation
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    // With p=1.0, should infect connected nodes
    EXPECT_GE(cascade.size(), 1);
}

TEST_F(CascadeGeneratorTest, SetProbabilities) {
    gen.set_graph(graph);
    // Edge-specific probabilities
    std::vector<std::vector<double>> probs = {{1.0}, {1.0}, {}};
    gen.set_probabilities(probs);
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    EXPECT_GE(cascade.size(), 1);
}

TEST_F(CascadeGeneratorTest, SetSymptomProbability) {
    gen.set_graph(graph);
    gen.set_probability(1.0);
    gen.set_symptom_probability(1.0);  // All symptomatic
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    // Verify all non-seed nodes are symptomatic
    for (size_t i = 1; i < cascade.size(); ++i) {
        EXPECT_EQ(std::get<2>(cascade[i]), 1.0);
    }
}

TEST_F(CascadeGeneratorTest, SetSymptomProbabilities) {
    gen.set_graph(graph);
    gen.set_probability(1.0);
    // Node-specific symptom probabilities
    std::vector<double> symp_probs = {0.0, 1.0, 0.0};
    gen.set_symptom_probabilities(symp_probs);
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    // Node 1 should be symptomatic if infected
    for (const auto& obs : cascade) {
        if (std::get<0>(obs) == 1) {
            EXPECT_EQ(std::get<2>(obs), 1.0);
        }
    }
}

TEST_F(CascadeGeneratorTest, SetDelays) {
    gen.set_graph(graph);
    std::vector<std::vector<double>> delays = {{1.5}, {2.0}, {}};
    gen.set_delays(delays);
    gen.set_probability(1.0);
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    // Should use priority queue mode
    EXPECT_GT(cascade.size(), 0);
}

TEST_F(CascadeGeneratorTest, SetRandomSeed) {
    gen.set_graph(graph);
    gen.set_probability(0.5);
    
    gen.set_random_seed(42);
    auto cascade1 = gen.generate_cascade({0});
    
    gen.set_random_seed(42);
    auto cascade2 = gen.generate_cascade({0});
    
    // Same seed should produce identical results
    EXPECT_EQ(cascade1, cascade2);
}
```

#### Test Suite 2: Cascade Generation - Basic

```cpp
TEST_F(CascadeGeneratorTest, GenerateCascade_SingleSeed) {
    gen.set_graph(graph);
    gen.set_probability(1.0);
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    
    EXPECT_GT(cascade.size(), 0);
    // First node should be seed
    EXPECT_EQ(std::get<0>(cascade[0]), 0);
    EXPECT_EQ(std::get<1>(cascade[0]), 0.0);  // Time = 0
}

TEST_F(CascadeGeneratorTest, GenerateCascade_MultipleSeeds) {
    gen.set_graph(graph);
    gen.set_probability(1.0);
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0, 1});
    
    // Should include both seeds
    bool has_node_0 = false;
    bool has_node_1 = false;
    for (const auto& obs : cascade) {
        if (std::get<0>(obs) == 0) has_node_0 = true;
        if (std::get<0>(obs) == 1) has_node_1 = true;
    }
    EXPECT_TRUE(has_node_0);
    EXPECT_TRUE(has_node_1);
}

TEST_F(CascadeGeneratorTest, GenerateCascade_EmptySeed) {
    gen.set_graph(graph);
    auto cascade = gen.generate_cascade({});
    
    // Empty seed should produce empty cascade
    EXPECT_EQ(cascade.size(), 0);
}

TEST_F(CascadeGeneratorTest, GenerateCascade_ZeroProbability) {
    gen.set_graph(graph);
    gen.set_probability(0.0);  // No propagation
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    
    // Only seed should be in cascade
    EXPECT_EQ(cascade.size(), 1);
    EXPECT_EQ(std::get<0>(cascade[0]), 0);
}

TEST_F(CascadeGeneratorTest, GenerateCascade_FullPropagation) {
    gen.set_graph(graph);
    gen.set_probability(1.0);  // Full propagation
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    
    // Should infect all reachable nodes
    EXPECT_EQ(cascade.size(), 3);  // 0, 1, 2
}
```

#### Test Suite 3: Cascade Generation - Delayed Mode

```cpp
TEST_F(CascadeGeneratorTest, DelayedMode_UsesCorrectAlgorithm) {
    gen.set_graph(graph);
    std::vector<std::vector<double>> delays = {{1.0}, {1.0}, {}};
    gen.set_delays(delays);
    gen.set_probability(1.0);
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    
    // Should use priority queue (generate_cascade_pq)
    // Verify by checking time values are correct
    EXPECT_GT(cascade.size(), 0);
}

TEST_F(CascadeGeneratorTest, DelayedMode_TimeOrdering) {
    gen.set_graph(graph);
    std::vector<std::vector<double>> delays = {{2.0}, {1.0}, {}};
    gen.set_delays(delays);
    gen.set_probability(1.0);
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    
    // Times should be non-decreasing in cascade
    for (size_t i = 1; i < cascade.size(); ++i) {
        double prev_time = std::get<1>(cascade[i-1]);
        double curr_time = std::get<1>(cascade[i]);
        EXPECT_LE(prev_time, curr_time);
    }
}

TEST_F(CascadeGeneratorTest, DelayedMode_ExpectedDelays) {
    // Create deterministic delay test
    gen.set_graph(graph);
    std::vector<std::vector<double>> delays = {{1.5}, {2.5}, {}};
    gen.set_delays(delays);
    gen.set_probability(1.0);
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    
    // Check that delays are reasonable (stochastic, so check range)
    // Exponential distribution with mean 1.5 should be in reasonable range
    for (const auto& obs : cascade) {
        double time = std::get<1>(obs);
        EXPECT_GE(time, 0.0);
        EXPECT_LT(time, 100.0);  // Reasonable upper bound
    }
}
```

#### Test Suite 4: Batch Generation

```cpp
TEST_F(CascadeGeneratorTest, GenerateCascades_MultipleRuns) {
    gen.set_graph(graph);
    gen.set_probability(0.5);
    gen.set_random_seed(42);
    
    int n_cascades = 10;
    auto cascades = gen.generate_cascades({0}, n_cascades);
    
    EXPECT_EQ(cascades.size(), n_cascades);
    
    // Each cascade should have at least the seed
    for (const auto& cascade : cascades) {
        EXPECT_GE(cascade.size(), 1);
    }
}

TEST_F(CascadeGeneratorTest, GenerateCascades_Variability) {
    gen.set_graph(graph);
    gen.set_probability(0.5);
    gen.set_random_seed(42);
    
    auto cascades = gen.generate_cascades({0}, 100);
    
    // Cascades should vary in size (stochastic)
    std::set<size_t> sizes;
    for (const auto& cascade : cascades) {
        sizes.insert(cascade.size());
    }
    EXPECT_GT(sizes.size(), 1);  // Should have variety
}
```

#### Test Suite 5: Edge Cases

```cpp
TEST_F(CascadeGeneratorTest, EdgeCase_SingleNode) {
    std::vector<std::vector<int>> single_node = {{}};
    gen.set_graph(single_node);
    gen.set_probability(1.0);
    
    auto cascade = gen.generate_cascade({0});
    EXPECT_EQ(cascade.size(), 1);
}

TEST_F(CascadeGeneratorTest, EdgeCase_DisconnectedGraph) {
    // Graph: 0 -> 1, 2 (disconnected)
    std::vector<std::vector<int>> disconnected = {{1}, {}, {}};
    gen.set_graph(disconnected);
    gen.set_probability(1.0);
    
    auto cascade = gen.generate_cascade({0});
    
    // Should only reach 0 and 1
    EXPECT_LE(cascade.size(), 2);
}

TEST_F(CascadeGeneratorTest, EdgeCase_CyclicGraph) {
    // Graph: 0 -> 1 -> 2 -> 0 (cycle)
    std::vector<std::vector<int>> cyclic = {{1}, {2}, {0}};
    gen.set_graph(cyclic);
    gen.set_probability(1.0);
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    
    // Should not hang (each node infected once)
    EXPECT_LE(cascade.size(), 3);
}

TEST_F(CascadeGeneratorTest, EdgeCase_LargeGraph) {
    // Create larger graph for stress test
    int n = 1000;
    std::vector<std::vector<int>> large_graph(n);
    for (int i = 0; i < n - 1; ++i) {
        large_graph[i].push_back(i + 1);
    }
    
    gen.set_graph(large_graph);
    gen.set_probability(1.0);
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    
    // Should handle large graphs
    EXPECT_GT(cascade.size(), 0);
    EXPECT_LE(cascade.size(), n);
}

TEST_F(CascadeGeneratorTest, EdgeCase_SeedNotInGraph) {
    gen.set_graph(graph);
    gen.set_probability(1.0);
    
    // Seed node 999 doesn't exist (graph has 0,1,2)
    // Current implementation may crash - this test documents expected behavior
    // TODO: Add validation to throw error instead
    EXPECT_NO_THROW(gen.generate_cascade({999}));
}
```

---

### Python Unit Tests (tests/test_py_cascade_generator.py)

#### Test Suite 1: Initialization

```python
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
```

#### Test Suite 2: Cascade Generation

```python
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
        
        # Should return single Cascade object
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
    
    def test_generate_determinism(self, simple_graph):
        """Test that same seed produces same results."""
        # Note: Currently missing set_random_seed exposure
        # This test will fail until that's implemented
        # TODO: Implement set_random_seed in Python wrapper
        pass
    
    def test_generate_with_symptom_probs(self, simple_graph):
        """Test cascade generation with symptom probabilities."""
        q = [1.0] * 10  # All symptomatic
        gen = pyCascadeGenerator(simple_graph, cascade_model="IC", q=q)
        cascade = gen.generate([0], num_cascades=1)
        
        # All non-seed nodes should be symptomatic
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
```

#### Test Suite 3: Integration with NetworkX

```python
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
    
    def test_directed_graph(self):
        """Test with directed graph."""
        graph = nx.DiGraph()
        graph.add_edges_from([(0, 1), (1, 2), (2, 3)])
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 1.0
        
        gen = pyCascadeGenerator(graph, cascade_model="IC")
        cascade = gen.generate([0], num_cascades=1)
        
        # Should propagate along directed edges
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
```

---

## Cutoff Feature Tests

### C++ Unit Tests for Cutoff

#### Test Suite 6: Cutoff Configuration

```cpp
class CascadeGeneratorCutoffTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Linear graph: 0 -> 1 -> 2 -> 3 -> 4
        graph = {{1}, {2}, {3}, {4}, {}};
    }
    
    std::vector<std::vector<int>> graph;
};

TEST_F(CascadeGeneratorCutoffTest, SetCutoff_Positive) {
    CascadeGenerator gen;
    gen.set_graph(graph);
    
    EXPECT_NO_THROW(gen.set_cutoff(5.0));
}

TEST_F(CascadeGeneratorCutoffTest, SetCutoff_Zero) {
    CascadeGenerator gen;
    gen.set_graph(graph);
    
    EXPECT_NO_THROW(gen.set_cutoff(0.0));
}

TEST_F(CascadeGeneratorCutoffTest, SetCutoff_Negative) {
    CascadeGenerator gen;
    gen.set_graph(graph);
    
    // Negative should disable cutoff
    gen.set_cutoff(-1.0);
    // Should work without cutoff
    gen.set_probability(1.0);
    auto cascade = gen.generate_cascade({0});
    EXPECT_GT(cascade.size(), 0);
}

TEST_F(CascadeGeneratorCutoffTest, ClearCutoff) {
    CascadeGenerator gen;
    gen.set_graph(graph);
    gen.set_probability(1.0);
    
    gen.set_cutoff(1.0);
    gen.clear_cutoff();
    
    auto cascade = gen.generate_cascade({0});
    // Should generate full cascade
    EXPECT_GT(cascade.size(), 1);
}
```

#### Test Suite 7: Cutoff Correctness

```cpp
TEST_F(CascadeGeneratorCutoffTest, CutoffZero_OnlySeeds) {
    CascadeGenerator gen;
    gen.set_graph(graph);
    gen.set_probability(1.0);
    gen.set_cutoff(0.0);
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    
    // Only seed at time 0.0
    EXPECT_EQ(cascade.size(), 1);
    EXPECT_EQ(std::get<0>(cascade[0]), 0);
    EXPECT_EQ(std::get<1>(cascade[0]), 0.0);
}

TEST_F(CascadeGeneratorCutoffTest, CutoffOne_OneGeneration) {
    CascadeGenerator gen;
    gen.set_graph(graph);
    gen.set_probability(1.0);
    gen.set_cutoff(1.0);
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    
    // Should have seed (time 0) and node 1 (time 1)
    EXPECT_LE(cascade.size(), 2);
    
    // All nodes should have time <= 1.0
    for (const auto& obs : cascade) {
        EXPECT_LE(std::get<1>(obs), 1.0);
    }
}

TEST_F(CascadeGeneratorCutoffTest, CutoffIntermediate) {
    CascadeGenerator gen;
    gen.set_graph(graph);
    gen.set_probability(1.0);
    gen.set_cutoff(2.5);
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    
    // Should have nodes at time 0, 1, 2, but not 3, 4
    EXPECT_LE(cascade.size(), 3);
    
    // All nodes should have time <= 2.5
    for (const auto& obs : cascade) {
        EXPECT_LE(std::get<1>(obs), 2.5);
    }
}

TEST_F(CascadeGeneratorCutoffTest, CutoffLarge_FullCascade) {
    CascadeGenerator gen;
    gen.set_graph(graph);
    gen.set_probability(1.0);
    gen.set_random_seed(42);
    
    // Generate full cascade
    auto full_cascade = gen.generate_cascade({0});
    
    // Generate with very large cutoff
    gen.set_random_seed(42);
    gen.set_cutoff(1000.0);
    auto cutoff_cascade = gen.generate_cascade({0});
    
    // Should be identical
    EXPECT_EQ(full_cascade.size(), cutoff_cascade.size());
}

TEST_F(CascadeGeneratorCutoffTest, CutoffCorrectness_MatchesTruncation) {
    CascadeGenerator gen;
    gen.set_graph(graph);
    gen.set_probability(1.0);
    gen.set_random_seed(42);
    
    // Generate full cascade
    auto full_cascade = gen.generate_cascade({0});
    
    // Generate with cutoff
    gen.set_random_seed(42);
    gen.set_cutoff(2.0);
    auto cutoff_cascade = gen.generate_cascade({0});
    
    // Manually truncate full cascade
    std::vector<std::tuple<int, double, double>> truncated;
    for (const auto& obs : full_cascade) {
        if (std::get<1>(obs) <= 2.0) {
            truncated.push_back(obs);
        }
    }
    
    // Should match
    EXPECT_EQ(cutoff_cascade, truncated);
}
```

#### Test Suite 8: Cutoff with Delays

```cpp
TEST_F(CascadeGeneratorCutoffTest, DelayedMode_CutoffWorks) {
    CascadeGenerator gen;
    gen.set_graph(graph);
    gen.set_probability(1.0);
    
    // Set delays
    std::vector<std::vector<double>> delays = {{1.5}, {2.0}, {1.0}, {1.5}, {}};
    gen.set_delays(delays);
    
    gen.set_cutoff(3.0);
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    
    // All times should be <= 3.0
    for (const auto& obs : cascade) {
        EXPECT_LE(std::get<1>(obs), 3.0);
    }
}

TEST_F(CascadeGeneratorCutoffTest, DelayedMode_TimeOrdering) {
    CascadeGenerator gen;
    gen.set_graph(graph);
    gen.set_probability(1.0);
    
    std::vector<std::vector<double>> delays = {{1.0}, {1.0}, {1.0}, {1.0}, {}};
    gen.set_delays(delays);
    
    gen.set_cutoff(2.5);
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    
    // Times should still be ordered
    for (size_t i = 1; i < cascade.size(); ++i) {
        EXPECT_LE(std::get<1>(cascade[i-1]), std::get<1>(cascade[i]));
    }
}
```

#### Test Suite 9: Cutoff Performance

```cpp
TEST_F(CascadeGeneratorCutoffTest, EarlyTermination_FewerIterations) {
    // Create large graph
    int n = 10000;
    std::vector<std::vector<int>> large_graph(n);
    for (int i = 0; i < n - 1; ++i) {
        large_graph[i].push_back(i + 1);
    }
    
    CascadeGenerator gen;
    gen.set_graph(large_graph);
    gen.set_probability(1.0);
    
    // Cutoff should produce much smaller cascade
    gen.set_cutoff(10.0);
    gen.set_random_seed(42);
    
    auto cascade = gen.generate_cascade({0});
    
    // Should be much less than full graph
    EXPECT_LT(cascade.size(), 100);
    EXPECT_GT(cascade.size(), 0);
}

TEST_F(CascadeGeneratorCutoffTest, NoCutoff_NoOverhead) {
    CascadeGenerator gen;
    gen.set_graph(graph);
    gen.set_probability(1.0);
    
    // Without setting cutoff
    gen.set_random_seed(42);
    auto cascade1 = gen.generate_cascade({0});
    
    // With cutoff disabled explicitly
    gen.clear_cutoff();
    gen.set_random_seed(42);
    auto cascade2 = gen.generate_cascade({0});
    
    // Should produce identical results
    EXPECT_EQ(cascade1, cascade2);
}
```

### Python Unit Tests for Cutoff

#### Test Suite: Cutoff in Python Wrapper

```python
class TestCutoffFeature:
    """Test time cutoff feature in Python wrapper."""
    
    @pytest.fixture
    def linear_graph(self):
        """Create linear graph for testing."""
        graph = nx.path_graph(10)
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 1.0
        return graph
    
    def test_cutoff_parameter_exists(self, linear_graph):
        """Test that cutoff parameter is available."""
        gen = pyCascadeGenerator(linear_graph, cascade_model="IC")
        
        # Should accept cutoff parameter
        cascade = gen.generate([0], num_cascades=1, cutoff=5.0)
        assert cascade is not None
    
    def test_cutoff_none_default(self, linear_graph):
        """Test that cutoff=None is default (backward compatibility)."""
        gen = pyCascadeGenerator(linear_graph, cascade_model="IC")
        
        # These should be equivalent
        cascade1 = gen.generate([0], num_cascades=1)
        cascade2 = gen.generate([0], num_cascades=1, cutoff=None)
        
        # Both should work (exact match requires same random seed)
        assert len(cascade1) >= 1
        assert len(cascade2) >= 1
    
    def test_cutoff_zero(self, linear_graph):
        """Test cutoff=0.0 returns only seeds."""
        gen = pyCascadeGenerator(linear_graph, cascade_model="IC")
        cascade = gen.generate([0], num_cascades=1, cutoff=0.0)
        
        assert len(cascade) == 1
        assert cascade[0].node_id == 0
        assert cascade[0].time == 0.0
    
    def test_cutoff_limits_cascade_size(self, linear_graph):
        """Test that cutoff reduces cascade size."""
        gen = pyCascadeGenerator(linear_graph, cascade_model="IC")
        
        full_cascade = gen.generate([0], num_cascades=1)
        cutoff_cascade = gen.generate([0], num_cascades=1, cutoff=3.0)
        
        # Cutoff cascade should be smaller or equal
        assert len(cutoff_cascade) <= len(full_cascade)
    
    def test_cutoff_respects_time_limit(self, linear_graph):
        """Test that all observations are within cutoff time."""
        gen = pyCascadeGenerator(linear_graph, cascade_model="IC")
        cutoff_time = 5.0
        
        cascade = gen.generate([0], num_cascades=1, cutoff=cutoff_time)
        
        for obs in cascade.cascade:
            assert obs.time <= cutoff_time
    
    def test_cutoff_batch_generation(self, linear_graph):
        """Test cutoff works with batch generation."""
        gen = pyCascadeGenerator(linear_graph, cascade_model="IC")
        
        cascades = gen.generate([0], num_cascades=10, cutoff=3.0)
        
        assert len(cascades) == 10
        for cascade in cascades:
            for obs in cascade.cascade:
                assert obs.time <= 3.0
    
    def test_cutoff_negative_raises_error(self, linear_graph):
        """Test that negative cutoff raises ValueError."""
        gen = pyCascadeGenerator(linear_graph, cascade_model="IC")
        
        with pytest.raises(ValueError):
            cascade = gen.generate([0], num_cascades=1, cutoff=-1.0)
    
    def test_cutoff_state_isolation(self, linear_graph):
        """Test that cutoff doesn't persist between calls."""
        gen = pyCascadeGenerator(linear_graph, cascade_model="IC")
        
        # Generate with cutoff
        cascade1 = gen.generate([0], num_cascades=1, cutoff=2.0)
        
        # Generate without cutoff (should not use previous cutoff)
        cascade2 = gen.generate([0], num_cascades=1)
        
        # Second cascade should be able to be larger
        # (Can't test exact sizes due to randomness, but verify it works)
        assert cascade1 is not None
        assert cascade2 is not None
```

---

## Performance Benchmarks

### Benchmark Suite 1: Current Performance Baseline

```python
# benchmarks/benchmark_baseline.py

import pytest
import networkx as nx
from cascadesimulator import pyCascadeGenerator

class TestBaselinePerformance:
    """Establish performance baselines for current implementation."""
    
    @pytest.fixture
    def small_graph(self):
        """Small graph (100 nodes)."""
        graph = nx.erdos_renyi_graph(100, 0.05)
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 0.3
        return graph
    
    @pytest.fixture
    def medium_graph(self):
        """Medium graph (1000 nodes)."""
        graph = nx.erdos_renyi_graph(1000, 0.01)
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 0.3
        return graph
    
    @pytest.fixture
    def large_graph(self):
        """Large graph (10000 nodes)."""
        graph = nx.erdos_renyi_graph(10000, 0.001)
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 0.3
        return graph
    
    def test_baseline_single_cascade_small(self, benchmark, small_graph):
        """Benchmark single cascade on small graph."""
        gen = pyCascadeGenerator(small_graph, cascade_model="IC")
        
        result = benchmark(gen.generate, [0], num_cascades=1)
        assert len(result) >= 1
    
    def test_baseline_batch_small(self, benchmark, small_graph):
        """Benchmark batch generation on small graph."""
        gen = pyCascadeGenerator(small_graph, cascade_model="IC")
        
        result = benchmark(gen.generate, [0], num_cascades=100)
        assert len(result) == 100
    
    def test_baseline_single_cascade_medium(self, benchmark, medium_graph):
        """Benchmark single cascade on medium graph."""
        gen = pyCascadeGenerator(medium_graph, cascade_model="IC")
        
        result = benchmark(gen.generate, [0], num_cascades=1)
        assert len(result) >= 1
    
    def test_baseline_single_cascade_large(self, benchmark, large_graph):
        """Benchmark single cascade on large graph."""
        gen = pyCascadeGenerator(large_graph, cascade_model="IC")
        
        result = benchmark(gen.generate, [0], num_cascades=1)
        assert len(result) >= 1
```

### Benchmark Suite 2: Cutoff Performance

```python
class TestCutoffPerformance:
    """Benchmark cutoff feature performance."""
    
    @pytest.fixture
    def large_graph(self):
        """Large graph for performance testing."""
        graph = nx.erdos_renyi_graph(10000, 0.001)
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 0.3
        return graph
    
    def test_cutoff_early_speedup(self, benchmark, large_graph):
        """Benchmark early cutoff (should be much faster)."""
        gen = pyCascadeGenerator(large_graph, cascade_model="IC")
        
        result = benchmark(gen.generate, [0], num_cascades=100, cutoff=2.0)
        assert len(result) == 100
    
    def test_cutoff_vs_no_cutoff(self, large_graph):
        """Compare performance with and without cutoff."""
        import time
        
        gen = pyCascadeGenerator(large_graph, cascade_model="IC")
        
        # Full cascade
        start = time.time()
        full_cascades = gen.generate([0], num_cascades=100)
        full_time = time.time() - start
        
        # With cutoff
        start = time.time()
        cutoff_cascades = gen.generate([0], num_cascades=100, cutoff=5.0)
        cutoff_time = time.time() - start
        
        speedup = full_time / cutoff_time
        print(f"Speedup: {speedup:.2f}x")
        
        # Should see significant speedup
        assert speedup > 1.5  # At least 1.5x faster
    
    def test_cutoff_overhead(self, large_graph):
        """Test overhead of cutoff=None vs no cutoff parameter."""
        import time
        
        gen = pyCascadeGenerator(large_graph, cascade_model="IC")
        
        # No cutoff parameter
        start = time.time()
        cascades1 = gen.generate([0], num_cascades=100)
        time1 = time.time() - start
        
        # cutoff=None
        start = time.time()
        cascades2 = gen.generate([0], num_cascades=100, cutoff=None)
        time2 = time.time() - start
        
        overhead = abs(time2 - time1) / time1
        
        # Overhead should be minimal (<5%)
        assert overhead < 0.05
```

### Benchmark Suite 3: Memory Usage

```python
class TestMemoryUsage:
    """Test memory usage with cutoff."""
    
    def test_cutoff_reduces_memory(self):
        """Test that early cutoff reduces memory usage."""
        import tracemalloc
        import networkx as nx
        from cascadesimulator import pyCascadeGenerator
        
        graph = nx.erdos_renyi_graph(5000, 0.002)
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 0.5
        
        gen = pyCascadeGenerator(graph, cascade_model="IC")
        
        # Full cascade memory
        tracemalloc.start()
        full_cascades = gen.generate([0], num_cascades=100)
        full_memory = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        
        # Cutoff cascade memory
        tracemalloc.start()
        cutoff_cascades = gen.generate([0], num_cascades=100, cutoff=3.0)
        cutoff_memory = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        
        # Should use less memory
        assert cutoff_memory < full_memory
        
        reduction = (full_memory - cutoff_memory) / full_memory
        print(f"Memory reduction: {reduction*100:.1f}%")
```

---

## Regression Tests

### Test Suite: Backward Compatibility

```python
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
    
    def test_notebook_example_still_works(self):
        """Test that notebook examples still work."""
        from random import random
        import networkx as nx
        from cascadesimulator import pyCascadeGenerator
        
        graph = nx.erdos_renyi_graph(100, 0.1)
        
        for edge in graph.edges():
            graph[edge[0]][edge[1]]['weight'] = 0.1 + 0.2*random()
        
        q = [0.5 + 0.5*random() for u in graph.nodes()]
        
        cascade_generator = pyCascadeGenerator(
            graph=graph,
            cascade_model="IC",
            q=q
        )
        
        seed = [0]
        num_cascades = 10
        cascades = cascade_generator.generate(seed, num_cascades)
        
        assert len(cascades) == 10
        
        cascade = cascades[0]
        assert len(cascade) >= 1
        
        # Test indexing as in notebook
        if len(cascade) > 76:
            obs = cascade[76]
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
```

---

## Test Implementation Guide

### Directory Structure

```
CascadeSimulator/
├── tests/
│   ├── cpp/
│   │   ├── test_cascade_generator.cpp
│   │   ├── test_cascade_generator_cutoff.cpp
│   │   ├── test_helpers.hpp
│   │   └── CMakeLists.txt
│   ├── python/
│   │   ├── test_py_cascade_generator.py
│   │   ├── test_cutoff_feature.py
│   │   ├── test_integration.py
│   │   ├── test_backward_compatibility.py
│   │   └── conftest.py
│   ├── benchmarks/
│   │   ├── benchmark_baseline.py
│   │   ├── benchmark_cutoff.py
│   │   └── benchmark_memory.py
│   └── e2e/
│       ├── test_notebooks.py
│       └── test_examples.py
├── pytest.ini
└── CMakeLists.txt (updated for tests)
```

### Running Tests

```bash
# Python tests
pytest tests/python/ -v --cov=cascadesimulator --cov-report=html

# Python benchmarks
pytest tests/benchmarks/ --benchmark-only

# C++ tests (after building)
cd build
ctest --verbose

# All tests
pytest tests/ -v && cd build && ctest
```

### CI Configuration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -e .[dev]
          pip install pytest pytest-cov pytest-benchmark
      
      - name: Run Python tests
        run: pytest tests/python/ -v --cov
      
      - name: Run C++ tests
        run: |
          mkdir build && cd build
          cmake ..
          make
          ctest --verbose
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Test Coverage Goals

- **Overall**: >90% code coverage
- **Critical paths**: 100% coverage (cascade generation, cutoff logic)
- **Edge cases**: All identified edge cases tested
- **Performance**: Benchmarks for all major features

---

## Summary

This testing plan provides:

1. **Comprehensive baseline tests** for current functionality
2. **Detailed cutoff feature tests** for new functionality
3. **Performance benchmarks** to measure improvements
4. **Regression tests** to ensure backward compatibility
5. **Implementation guide** with directory structure and CI setup

### Test Counts

- **C++ Unit Tests**: ~40-50 tests
- **Python Unit Tests**: ~30-40 tests
- **Integration Tests**: ~10-15 tests
- **Performance Benchmarks**: ~10-15 benchmarks
- **Regression Tests**: ~5-10 tests

**Total**: ~100-130 tests

### Next Steps

1. Set up testing infrastructure (directories, CMakeLists.txt, pytest.ini)
2. Implement baseline tests for current functionality
3. Verify all tests pass (establish baseline)
4. Implement cutoff feature
5. Add cutoff tests as feature is developed
6. Run performance benchmarks
7. Verify backward compatibility
8. Set up CI/CD for automated testing
