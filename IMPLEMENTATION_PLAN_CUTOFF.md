# Implementation Plan: Time Cutoff Feature

**Date:** January 21, 2026  
**Feature:** Time-based cutoff for cascade generation  
**Goal:** Maximum efficiency with full backward compatibility

---

## Executive Summary

This document details the implementation strategy for adding time-based cutoff support to CascadeSimulator. The feature will allow users to stop cascade generation at a specified time, providing significant performance improvements for early-stage cascade analysis while maintaining full backward compatibility.

### Key Metrics
- **Performance Target**: 2-5x speedup for cutoff at 50% of full cascade time
- **Memory Target**: 50-80% reduction for early cutoffs
- **Compatibility**: 100% backward compatible (zero breaking changes)
- **Overhead**: <2% performance impact when cutoff=None

---

## Algorithm Analysis

### Current Implementation Review

#### Delayed Cascades (Priority Queue Mode)
```cpp
// Current: generate_cascade_pq()
while (!active.empty()) {
    QNode qnode = active.top();
    active.pop();
    int node = qnode.node;
    double time = qnode.arrival_time;
    
    // Process node, infect neighbors
    for (neighbor in neighbors) {
        double delay = time + get_delay(node, neighbor);
        // Add to cascade
        active.push(QNode(neighbor, delay));
    }
}
```

**Optimization Strategy for Cutoff:**
- ✅ Priority queue naturally ordered by time
- ✅ Can break early when `time > cutoff`
- ✅ Don't add neighbors if `delay > cutoff`
- ✅ Minimal overhead (single comparison per iteration)

#### Non-Delayed Cascades (BFS Mode)
```cpp
// Current: generate_cascade()
std::list<std::pair<int,double>> active;
while (!active.empty()) {
    auto current = active.front();
    active.pop_front();
    int node = current.first;
    double time = current.second;
    
    // Process node (all neighbors same time)
    for (neighbor in neighbors) {
        active.push_back(make_pair(neighbor, time + 1.0));
    }
}
```

**Optimization Strategy for Cutoff:**
- ✅ Time increases in discrete steps (1.0 per generation)
- ✅ Can convert cutoff to max_generation count
- ✅ Check generation only, not time in inner loop
- ✅ Break when current generation > max_generation

---

## Detailed Implementation Design

### Phase 1: C++ Core Implementation

#### Step 1.1: Add Class Members
```cpp
class CascadeGenerator {
private:
    // Existing members...
    
    // NEW: Cutoff support
    double cutoff_time_;      // Cutoff time (-1.0 = no cutoff)
    bool use_cutoff_;         // Flag for fast check
    
public:
    // Constructor initialization
    CascadeGenerator() 
        : /* existing... */
          cutoff_time_(-1.0),
          use_cutoff_(false) {}
};
```

**Rationale:**
- `cutoff_time_` stores the actual cutoff value
- `use_cutoff_` flag avoids checking `cutoff_time_ >= 0` in tight loops
- Default: no cutoff (backward compatible)

#### Step 1.2: Add Setter Methods
```cpp
void set_cutoff(double cutoff_time) {
    if (cutoff_time >= 0.0) {
        cutoff_time_ = cutoff_time;
        use_cutoff_ = true;
    } else {
        clear_cutoff();
    }
}

void clear_cutoff() {
    cutoff_time_ = -1.0;
    use_cutoff_ = false;
}
```

**Rationale:**
- Negative cutoff disables feature
- Explicit flag avoids comparison in hot path
- Clear method for reusing generator

#### Step 1.3: Modify generate_cascade_pq() - DELAYED MODE

```cpp
std::vector<std::tuple<int, double, double>> 
generate_cascade_pq(const std::vector<int>& seed) {
    std::vector<std::tuple<int, double, double>> cascade;
    std::priority_queue<QNode, std::vector<QNode>, CompareByTime> active;
    std::vector<bool> infected(n_nodes_, false);
    std::vector<bool> is_active(n_nodes_, false);
    
    // Initialize with seed
    for (int node : seed) {
        // Only include seed nodes if they're within cutoff
        if (use_cutoff_ && 0.0 > cutoff_time_) continue;
        active.push(QNode(node, 0.0));
        infected[node] = true;
        is_active[node] = true;
        cascade.push_back(std::make_tuple(node, 0.0, 0.0));
    }
    
    while (!active.empty()) {
        QNode qnode = active.top();
        active.pop();
        
        int node = qnode.node;
        double time = qnode.arrival_time;
        
        // OPTIMIZATION 1: Early termination
        // If this node exceeds cutoff, all remaining nodes also exceed it
        if (use_cutoff_ && time > cutoff_time_) {
            break;  // Early exit - saves all remaining iterations
        }
        
        if (!is_active[node]) continue;
        is_active[node] = false;
        
        // Process neighbors
        for (int j = 0; j < graph_[node].size(); ++j) {
            int neighbor = graph_[node][j];
            if (infected[neighbor]) continue;
            
            double p = edge_probabilities_ ? edge_probs_[node][j] : probability_;
            double q = symptomatic_ ? node_symp_probs_[neighbor] : symptom_probability_;
            double delay = time + (delayed_ ? get_delay(node, neighbor) : 1.0);
            
            // OPTIMIZATION 2: Don't add nodes beyond cutoff
            // Saves queue insertions and future processing
            if (use_cutoff_ && delay > cutoff_time_) {
                continue;  // Skip this neighbor
            }
            
            if (std::rand() / (RAND_MAX + 1.0) > p) continue;
            
            // Add to cascade
            if (std::rand() / (RAND_MAX + 1.0) < q) {
                cascade.push_back(std::make_tuple(neighbor, delay, 1.0));
            } else {
                cascade.push_back(std::make_tuple(neighbor, delay, 0.0));
            }
            
            active.push(QNode(neighbor, delay));
            infected[neighbor] = true;
            is_active[neighbor] = true;
        }
    }
    
    return cascade;
}
```

**Performance Analysis:**
- **Early termination** (Optimization 1): Saves O(k) iterations where k = nodes after cutoff
- **Preventive filtering** (Optimization 2): Saves O(k) queue operations
- **Branch cost**: 1-2 CPU cycles per comparison
- **Net benefit**: For 50% cutoff, saves ~50% of work with <1% overhead

#### Step 1.4: Modify generate_cascade() - NON-DELAYED MODE

```cpp
std::vector<std::tuple<int, double, double>> 
generate_cascade(const std::vector<int>& seed) {
    if (delayed_) {
        return generate_cascade_pq(seed);
    }
    
    std::vector<std::tuple<int, double, double>> cascade;
    std::list<std::pair<int, double>> active;
    std::vector<bool> infected(n_nodes_, false);
    
    // OPTIMIZATION: Convert cutoff to generation count
    // Time increases by 1.0 each generation
    int max_generation = use_cutoff_ ? 
        static_cast<int>(std::floor(cutoff_time_)) : 
        std::numeric_limits<int>::max();
    
    // Initialize with seed (generation 0)
    for (int node : seed) {
        if (use_cutoff_ && 0.0 > cutoff_time_) continue;
        active.push_back(std::make_pair(node, 0.0));
        infected[node] = true;
        cascade.push_back(std::make_tuple(node, 0.0, 0.0));
    }
    
    int current_generation = 0;
    
    while (!active.empty()) {
        auto current = active.front();
        active.pop_front();
        
        int node = current.first;
        double time = current.second;
        int generation = static_cast<int>(time);
        
        // Track generation change
        if (generation > current_generation) {
            current_generation = generation;
            
            // OPTIMIZATION: Check cutoff only once per generation
            if (current_generation > max_generation) {
                break;  // All remaining nodes are beyond cutoff
            }
        }
        
        // Process neighbors (next generation)
        for (int j = 0; j < graph_[node].size(); ++j) {
            int neighbor = graph_[node][j];
            if (infected[neighbor]) continue;
            
            double p = edge_probabilities_ ? edge_probs_[node][j] : probability_;
            double q = symptomatic_ ? node_symp_probs_[neighbor] : symptom_probability_;
            double next_time = time + 1.0;
            
            // OPTIMIZATION: Check if next generation exceeds cutoff
            if (use_cutoff_ && next_time > cutoff_time_) {
                continue;  // Don't add neighbors beyond cutoff
            }
            
            if (std::rand() / (RAND_MAX + 1.0) > p) continue;
            
            // Add to cascade
            if (std::rand() / (RAND_MAX + 1.0) < q) {
                cascade.push_back(std::make_tuple(neighbor, next_time, 1.0));
            } else {
                cascade.push_back(std::make_tuple(neighbor, next_time, 0.0));
            }
            
            active.push_back(std::make_pair(neighbor, next_time));
            infected[neighbor] = true;
        }
    }
    
    return cascade;
}
```

**Performance Analysis:**
- **Generation tracking**: Amortized O(1) cost
- **Early break**: Saves all nodes in generations > cutoff
- **Minimal overhead**: Cutoff check only once per generation, not per node
- **Net benefit**: For cutoff=5 on 20-generation cascade, saves 75% of work

#### Step 1.5: Update Batch Generation

```cpp
std::vector<std::vector<std::tuple<int,double,double>>> 
generate_cascades(const std::vector<int>& seed, int n_cascades) {
    std::vector<std::vector<std::tuple<int,double,double>>> cascades(n_cascades);
    
    // Cutoff is already set via set_cutoff(), shared across all threads
    #pragma omp parallel for shared(cascades)
    for (int i = 0; i < n_cascades; ++i) {
        auto cascade = generate_cascade(seed);
        cascades[i] = std::move(cascade);
    }
    
    return cascades;
}
```

**Thread Safety Analysis:**
- `cutoff_time_` and `use_cutoff_` are **read-only** during parallel execution
- Set before calling `generate_cascades()`
- No race conditions (no writes in parallel section)
- OpenMP safe (shared read-only data)

### Phase 2: Python Wrapper Implementation

#### Step 2.1: Update pyCascadeGenerator

```python
class pyCascadeGenerator:
    def __init__(
        self,
        graph: nx.Graph,
        cascade_model: str = "IC",
        q: Optional[list[float]] = None,
        delay_times: Optional[list[float]] = None,
    ):
        # Existing initialization code...
        self.cascade_model_ = cg.CascadeGenerator()
        # ... rest of init
        
    def generate(
        self, 
        seeds: list[int], 
        num_cascades: int = 1,
        cutoff: Optional[float] = None  # NEW PARAMETER
    ) -> Cascade | list[Cascade]:
        """Generate cascades with optional time cutoff.
        
        Args:
            seeds: List of seed node IDs
            num_cascades: Number of cascades to generate
            cutoff: Optional time cutoff. If specified, only returns
                   events that occur at time <= cutoff. Provides
                   significant performance improvement for early-stage
                   cascade analysis. Default: None (no cutoff).
        
        Returns:
            Single Cascade if num_cascades=1, otherwise list of Cascades
            
        Examples:
            # Full cascade
            cascade = gen.generate([0], num_cascades=1)
            
            # Early cascade (first 5 time steps only)
            cascade = gen.generate([0], num_cascades=1, cutoff=5.0)
            
            # Batch with cutoff
            cascades = gen.generate([0], num_cascades=100, cutoff=10.0)
        """
        # Set cutoff if provided
        if cutoff is not None:
            if cutoff < 0:
                raise ValueError("cutoff must be non-negative")
            self.cascade_model_.set_cutoff(cutoff)
        else:
            self.cascade_model_.clear_cutoff()
        
        # Generate cascades
        cascades = []
        for _ in range(num_cascades):
            cascade = self.cascade_model_.generate_cascade(seeds)
            cascade = [Observation(*args) for args in cascade]
            cascades.append(Cascade(cascade))
        
        # Clear cutoff for next call (avoid state contamination)
        self.cascade_model_.clear_cutoff()
        
        if num_cascades == 1:
            return cascades[0]
        return cascades
```

**Design Decisions:**
- ✅ Optional parameter: backward compatible
- ✅ Validation: raise ValueError for invalid cutoff
- ✅ State management: clear cutoff after use
- ✅ Documentation: clear explanation and examples

#### Step 2.2: Alternative API Design (More Efficient)

For better performance with batch generation:

```python
def generate(
    self, 
    seeds: list[int], 
    num_cascades: int = 1,
    cutoff: Optional[float] = None
) -> Cascade | list[Cascade]:
    """Generate cascades with optional time cutoff."""
    
    # Validate inputs
    if cutoff is not None and cutoff < 0:
        raise ValueError("cutoff must be non-negative")
    
    # OPTIMIZATION: Use C++ batch method for multiple cascades
    if num_cascades > 1:
        # Set cutoff once for all cascades
        if cutoff is not None:
            self.cascade_model_.set_cutoff(cutoff)
        else:
            self.cascade_model_.clear_cutoff()
        
        # Generate all cascades in C++ (parallel)
        raw_cascades = self.cascade_model_.generate_cascades(seeds, num_cascades)
        
        # Convert to Cascade objects
        cascades = [
            Cascade([Observation(*args) for args in raw_cascade])
            for raw_cascade in raw_cascades
        ]
        
        self.cascade_model_.clear_cutoff()
        return cascades
    
    else:
        # Single cascade - use existing logic
        if cutoff is not None:
            self.cascade_model_.set_cutoff(cutoff)
        else:
            self.cascade_model_.clear_cutoff()
        
        cascade = self.cascade_model_.generate_cascade(seeds)
        cascade = Cascade([Observation(*args) for args in cascade])
        
        self.cascade_model_.clear_cutoff()
        return cascade
```

**Benefits:**
- Uses C++ parallel `generate_cascades()` for better performance
- Single cutoff set for all cascades in batch
- Reduced Python<->C++ boundary crossings

---

## Performance Optimization Strategies

### Strategy 1: Branch Prediction Optimization

**Problem:** `if (use_cutoff_ && time > cutoff_time_)` in tight loop

**Solutions:**

1. **Template Specialization** (Best performance, more code)
```cpp
template<bool UseCutoff>
std::vector<std::tuple<int, double, double>> 
generate_cascade_pq_impl(const std::vector<int>& seed) {
    // ...
    while (!active.empty()) {
        // ...
        if constexpr (UseCutoff) {
            if (time > cutoff_time_) break;
        }
        // ...
    }
}

// Wrapper
std::vector<std::tuple<int, double, double>> 
generate_cascade_pq(const std::vector<int>& seed) {
    if (use_cutoff_) {
        return generate_cascade_pq_impl<true>(seed);
    } else {
        return generate_cascade_pq_impl<false>(seed);
    }
}
```

**Pros:** Zero overhead when cutoff disabled, perfect branch prediction  
**Cons:** Code duplication, more complex maintenance

2. **Likely/Unlikely Hints** (Good balance)
```cpp
if (__builtin_expect(use_cutoff_, false)) {
    if (time > cutoff_time_) break;
}
```

**Pros:** Helps branch predictor, no code duplication  
**Cons:** Compiler-specific, moderate improvement

3. **Simple Flag** (Current approach, acceptable)
```cpp
if (use_cutoff_ && time > cutoff_time_) {
    break;
}
```

**Pros:** Clean code, portable, good-enough performance  
**Cons:** 1-2 cycle penalty per iteration

**Recommendation:** Start with Strategy 3, profile, upgrade to Strategy 1 if needed

### Strategy 2: Memory Pre-allocation

```cpp
std::vector<std::tuple<int, double, double>> 
generate_cascade_pq(const std::vector<int>& seed) {
    std::vector<std::tuple<int, double, double>> cascade;
    
    // OPTIMIZATION: Pre-allocate based on cutoff
    if (use_cutoff_) {
        // Estimate: cutoff time correlates with cascade size
        // Heuristic: reserve 10% of graph size per time unit
        size_t estimate = static_cast<size_t>(
            std::min(n_nodes_, 
                     seed.size() * std::pow(10, cutoff_time_))
        );
        cascade.reserve(estimate);
    } else {
        // Default: assume moderate cascade
        cascade.reserve(n_nodes_ / 10);
    }
    
    // ... rest of code
}
```

**Benefits:**
- Reduces vector reallocations
- Better cache locality
- 5-10% speedup for large cascades

### Strategy 3: Early Exit Optimization

```cpp
// For non-delayed mode: process by generation
while (!active.empty()) {
    // Drain entire current generation
    size_t generation_size = active.size();
    
    for (size_t i = 0; i < generation_size; ++i) {
        auto current = active.front();
        active.pop_front();
        
        // Process node...
        // Add neighbors to end of queue
    }
    
    // Check cutoff once per generation (not per node)
    current_generation++;
    if (use_cutoff_ && current_generation > max_generation) {
        break;  // Clean exit, no partial generation
    }
}
```

**Benefits:**
- Cutoff check only once per generation
- Cleaner semantics (complete generations)
- Better branch prediction

---

## Testing Strategy

### Unit Tests

```cpp
// Test 1: Cutoff at time 0 (seeds only)
TEST(CascadeGenerator, CutoffZero) {
    CascadeGenerator gen;
    // Setup graph...
    gen.set_cutoff(0.0);
    auto cascade = gen.generate_cascade({0});
    EXPECT_EQ(cascade.size(), 1);  // Only seed
    EXPECT_EQ(std::get<0>(cascade[0]), 0);
}

// Test 2: Cutoff at time 1 (one generation)
TEST(CascadeGenerator, CutoffOneGeneration) {
    CascadeGenerator gen;
    // Setup graph with deterministic propagation...
    gen.set_cutoff(1.0);
    auto cascade = gen.generate_cascade({0});
    
    // Verify all nodes have time <= 1.0
    for (const auto& obs : cascade) {
        EXPECT_LE(std::get<1>(obs), 1.0);
    }
}

// Test 3: Cutoff = None (backward compatibility)
TEST(CascadeGenerator, NoCutoff) {
    CascadeGenerator gen;
    // Don't set cutoff
    auto cascade1 = gen.generate_cascade({0});
    
    gen.set_cutoff(-1.0);  // Explicit disable
    auto cascade2 = gen.generate_cascade({0});
    
    // Should be statistically similar
}

// Test 4: Correctness - compare truncated vs cutoff
TEST(CascadeGenerator, CutoffCorrectness) {
    CascadeGenerator gen;
    set_random_seed(42);
    
    auto full_cascade = gen.generate_cascade({0});
    
    set_random_seed(42);
    gen.set_cutoff(5.0);
    auto cutoff_cascade = gen.generate_cascade({0});
    
    // Cutoff cascade should match full cascade truncated at 5.0
    auto truncated = filter(full_cascade, [](auto obs) {
        return std::get<1>(obs) <= 5.0;
    });
    
    EXPECT_EQ(cutoff_cascade, truncated);
}
```

### Performance Benchmarks

```python
import time
import networkx as nx
from cascadesimulator import pyCascadeGenerator

# Create test graph
graph = nx.erdos_renyi_graph(10000, 0.001)
for edge in graph.edges():
    graph[edge[0]][edge[1]]['weight'] = 0.1

gen = pyCascadeGenerator(graph, cascade_model="IC")

# Benchmark 1: Full cascade
start = time.time()
full_cascade = gen.generate([0], num_cascades=100)
full_time = time.time() - start

# Benchmark 2: Cutoff at 50% of average time
avg_time = sum(len(c) for c in full_cascade) / len(full_cascade)
cutoff_time = avg_time * 0.5

start = time.time()
cutoff_cascade = gen.generate([0], num_cascades=100, cutoff=cutoff_time)
cutoff_time_elapsed = time.time() - start

speedup = full_time / cutoff_time_elapsed
print(f"Speedup: {speedup:.2f}x")
# Target: 2-3x speedup
```

---

## Migration Guide

### For Existing Users

**No changes required!** All existing code works as-is:

```python
# This still works exactly the same
cascade = gen.generate([0], num_cascades=10)
```

### Using the New Feature

```python
# Early-stage cascade (first 5 time steps)
early_cascade = gen.generate([0], cutoff=5.0)

# Batch generation with cutoff
cascades = gen.generate([0], num_cascades=1000, cutoff=10.0)

# Time-windowed analysis
for t in [1, 2, 5, 10, 20]:
    cascade = gen.generate([0], cutoff=t)
    print(f"Cascade size at t={t}: {len(cascade)}")
```

---

## Success Criteria Checklist

- [ ] Backward compatibility: All existing code works unchanged
- [ ] Performance: 2-5x speedup for cutoff at 50% of cascade time
- [ ] Memory: 50-80% reduction for early cutoffs
- [ ] Overhead: <2% when cutoff=None
- [ ] Correctness: Cutoff cascades match truncated full cascades
- [ ] Thread safety: No race conditions in parallel execution
- [ ] Documentation: Clear examples and API documentation
- [ ] Testing: >95% code coverage for cutoff logic

---

## Timeline Estimate

- **Phase 1 (C++ Core)**: 2-3 days
- **Phase 2 (Python Wrapper)**: 1 day
- **Phase 3 (Optimization)**: 2-3 days
- **Phase 4 (Testing)**: 2-3 days
- **Phase 5 (Documentation)**: 1-2 days
- **Phase 6 (Validation)**: 1-2 days

**Total: 9-14 days** (depending on optimization depth)

---

## Next Steps

1. Review and approve this implementation plan
2. Create feature branch from dev: `git checkout -b feature/time-cutoff`
3. Implement Phase 1: C++ core changes
4. Write unit tests as you implement
5. Implement Phase 2: Python wrapper
6. Benchmark and optimize (Phase 3)
7. Complete testing suite (Phase 4)
8. Write documentation (Phase 5)
9. Final validation and merge to dev
