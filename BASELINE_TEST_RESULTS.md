# Baseline Test Results

**Date:** January 21, 2026  
**Branch:** dev  
**Commit:** e6e73d2

---

## Summary

✅ **All tests passing**: 19/19 unit tests (100%)  
✅ **No code changes**: Tests run against unmodified codebase  
✅ **Baseline established**: Ready for cutoff feature implementation

---

## Test Results

### Unit Tests

```
pytest tests/python/ -v
```

**Results:**
- **Total tests**: 19
- **Passed**: 19 (100%)
- **Failed**: 0
- **Duration**: 1.28 seconds

#### Test Breakdown

**TestPyCascadeGeneratorInit** (5 tests)
- ✅ test_init_basic
- ✅ test_init_with_symptom_probs
- ✅ test_init_with_delays
- ✅ test_init_unsupported_model
- ✅ test_init_invalid_node_ids

**TestPyCascadeGeneratorGenerate** (8 tests)
- ✅ test_generate_single_cascade
- ✅ test_generate_multiple_cascades
- ✅ test_cascade_contains_seed
- ✅ test_cascade_observation_structure
- ✅ test_cascade_indexing
- ✅ test_generate_with_symptom_probs
- ✅ test_generate_zero_probability
- ✅ test_generate_empty_seed

**TestNetworkXIntegration** (4 tests)
- ✅ test_erdos_renyi_graph
- ✅ test_barabasi_albert_graph
- ✅ test_complete_graph
- ✅ test_empty_graph

**TestBackwardCompatibility** (2 tests)
- ✅ test_readme_example_works
- ✅ test_existing_api_unchanged

---

## Performance Benchmarks

```
pytest tests/benchmarks/benchmark_baseline.py -v
```

**Results:**

### Single Cascade - Small Graph (100 nodes, 5% edge density)
- **Mean**: 4.12 μs
- **Median**: 0.87 μs
- **Min**: 0.58 μs
- **Max**: 26.79 μs
- **StdDev**: 4.85 μs

### Batch 100 Cascades - Small Graph
- **Mean**: 431.80 μs
- **Median**: 368.67 μs
- **Min**: 196.29 μs
- **Max**: 6,914.62 μs
- **StdDev**: 540.53 μs
- **Throughput**: ~2,316 cascades/second

### Single Cascade - Medium Graph (1000 nodes, 1% edge density)
- **Mean**: 226.52 μs
- **Median**: 219.29 μs
- **Min**: 0.75 μs
- **Max**: 6,525.21 μs
- **StdDev**: 366.52 μs

---

## Test Coverage

### Current Coverage

**Python Code Tested:**
- ✅ pyCascadeGenerator.__init__()
- ✅ pyCascadeGenerator.generate() - single cascade
- ✅ pyCascadeGenerator.generate() - batch mode
- ✅ Cascade dataclass
- ✅ Observation dataclass
- ✅ Graph conversion (NetworkX to adjacency list)
- ✅ Edge weight handling
- ✅ Symptom probability handling
- ✅ Delay time handling

**Test Scenarios:**
- ✅ Various graph types (Erdős-Rényi, Barabási-Albert, complete, path, empty)
- ✅ Different propagation probabilities (0.0, 0.5, 1.0)
- ✅ Symptom probabilities (all symptomatic, all asymptomatic, mixed)
- ✅ Empty seed sets
- ✅ Single and multiple seed nodes
- ✅ Error conditions (invalid models, invalid node IDs)

**Not Yet Tested (C++ level):**
- ⚠️ C++ CascadeGenerator class directly
- ⚠️ generate_cascade_pq() with delays
- ⚠️ Thread safety in parallel execution
- ⚠️ Random seed reproducibility
- ⚠️ Edge cases in C++ code

---

## Key Findings

### ✅ Strengths
1. **API works as documented**: README examples run without errors
2. **Type safety**: Observation and Cascade dataclasses work correctly
3. **Graph compatibility**: Works with various NetworkX graph types
4. **Performance**: Fast cascade generation (microsecond scale)
5. **Backward compatibility**: All existing API signatures work

### ⚠️ Areas for Improvement (to address in future)
1. **No determinism tests**: Cannot verify reproducibility (set_random_seed not exposed)
2. **Limited C++ testing**: Only tested through Python wrapper
3. **No parallel execution tests**: Thread safety not verified
4. **No edge case stress tests**: Very large graphs, extreme probabilities
5. **No memory profiling**: Memory usage not measured

### 📊 Performance Baselines Established
- Small graphs (100 nodes): ~4 μs per cascade
- Medium graphs (1000 nodes): ~227 μs per cascade
- Batch processing: ~2,300 cascades/second

These baselines will be used to measure:
- Performance improvements from cutoff feature
- Overhead of cutoff=None (should be <2%)
- Speedup with early cutoffs (target: 2-5x)

---

## Next Steps

1. ✅ Baseline tests implemented and passing
2. ✅ Performance baselines established
3. ⏭️ **Ready to implement cutoff feature**

### Implementation Order
1. Add cutoff tests (that will initially fail)
2. Implement C++ cutoff functionality
3. Update Python wrapper for cutoff
4. Run tests to verify correctness
5. Run benchmarks to verify performance improvements
6. Add C++ unit tests (optional but recommended)

---

## Test Execution Commands

```bash
# Run all unit tests
pytest tests/python/ -v

# Run with coverage
pytest tests/python/ -v --cov=cascadesimulator --cov-report=term-missing

# Run benchmarks
pytest tests/benchmarks/ -v

# Run specific test class
pytest tests/python/test_py_cascade_generator.py::TestPyCascadeGeneratorInit -v

# Run fast tests only (skip slow)
pytest tests/python/ -v -m "not slow"
```

---

## Environment

- **Python**: 3.11.5
- **pytest**: 9.0.2
- **pytest-benchmark**: 5.2.3
- **networkx**: 3.6.1
- **Platform**: macOS (darwin)
- **Architecture**: ARM64

---

## Conclusion

The baseline testing infrastructure is in place and all tests are passing. The codebase is stable and ready for the cutoff feature implementation. Performance benchmarks provide clear targets for measuring the impact of the new feature.
