# CascadeSimulator - TODO

**Last Updated:** February 5, 2026  
**Status:** ✅ Production Ready - All Critical Items Complete

---

## Summary

The CascadeSimulator is **production-ready** with all critical features implemented:
- ✅ Time cutoff feature (3.78x average speedup)
- ✅ Modern C++ RNG and comprehensive validation
- ✅ 70/70 tests passing
- ✅ Complete documentation and examples
- ✅ PyPI-ready package configuration

**Remaining items are optional enhancements.**

---

## Priority 1: Recommended for Release

### CI/CD & Publishing
- [x] Set up GitHub Actions for automated testing
  - Matrix test across Python 3.8-3.12
  - Matrix test across OS (Ubuntu, macOS, Windows)
  - Coverage reporting
- [x] Create CHANGELOG.md tracking version history
- [x] Create CONTRIBUTING.md for contributors
- [ ] Tag v1.0.0 release
- [ ] Publish to PyPI

### Documentation
- [x] Add "Building from Source" section to README
- [x] Add troubleshooting section to README
- [x] Add citation information (if for academic use)
- [x] Create RELEASE.md with release process documentation

---

## Priority 2: Quality Improvements

### Testing Enhancements
- [x] Test with empty graph (0 nodes)
- [x] Test with single node graph  
- [x] Test with disconnected graph
- [ ] Write C++ unit tests (Catch2 or Google Test)
- [ ] Memory leak testing

### Code Quality
- [x] Add const correctness to C++ methods (where applicable)
- [x] Replace magic numbers with named constants (INITIAL_TIME, HAS_SYMPTOM, etc.)
- [x] Add C++ standard version to CMakeLists.txt (C++14)
- [x] Enable compiler warnings (-Wall -Wextra)
- [x] Add compiler optimization flags for release builds (-O3, -march=native)

---

## Priority 3: Performance Optimizations

### Compiler & Build
- [x] Add optimization flags in CMakeLists.txt (-O3, -march=native)
- [ ] Profile code to find bottlenecks
- [x] Consider separate optimized paths for cutoff vs no-cutoff

### Algorithmic
- [x] Pre-allocate cascade vectors based on cutoff estimation
- [x] Use `std::deque` instead of `std::list` for active queue
- [x] Inline hints for hot path functions

**Results:** 
- Phase 1 (data structures): 25% faster on 1k nodes, 18% faster on 10k nodes
- Phase 2 (separate paths): **95% faster on 10k nodes vs baseline** 🚀
- Overall: 20x throughput improvement on medium graphs
- See OPTIMIZATION_RESULTS.md for detailed analysis

---

## Priority 4: New Features

### Additional Cascade Models
- [ ] Implement Linear Threshold (LT) model
- [ ] Implement Triggering model
- [ ] Implement Weighted Cascade model

### Analysis Tools
- [ ] Cascade analysis utilities (size, depth, influence metrics)
- [ ] Export cascades to DataFrame/CSV/JSON
- [ ] Visualization tools for cascades

### Extended Graph Support
- [ ] Support for igraph library
- [ ] Support for graph-tool library
- [ ] Direct adjacency matrix input

### Advanced Features
- [ ] GPU acceleration (CUDA/OpenCL)
- [ ] Distributed computing support
- [ ] Streaming cascade generation (generators)

---

## Maintenance Tasks

- [ ] Review and update dependencies quarterly
- [ ] Monitor for security vulnerabilities
- [ ] Update documentation as features are added
- [ ] Respond to issues and pull requests

---

**See `TODO_ARCHIVE.md` for completed implementation details.**

  - [x] Add private members: `double cutoff_time_`, `bool use_cutoff_`
  - [x] Add `set_cutoff(double cutoff_time)` method
  - [x] Add `clear_cutoff()` method for reuse
  - [x] Update constructor to initialize cutoff variables

- [x] Update pybind11 bindings (Step 1)
  - [x] Expose `set_cutoff()` method
  - [x] Expose `clear_cutoff()` method
  - [x] Remove duplicate method registrations (cleanup)
  - [x] Add documentation strings to bindings

- [x] Update type stubs (Step 1)
  - [x] Add `set_cutoff()` to `.pyi` file
  - [x] Add `clear_cutoff()` to `.pyi` file

- [x] Create infrastructure tests (Step 1)
  - [x] Test that methods exist and can be called
  - [x] Test positive, zero, and negative cutoff values
  - [x] Test that cascade generation still works with cutoff set
  - [x] Verify backward compatibility maintained
  - [x] All 28 tests passing (19 original + 9 new)

**Status**: Infrastructure complete, methods exposed, tests passing. ✅ Step 1 COMPLETE

- [x] Modify `generate_cascade_pq()` for cutoff support (Step 2)
  - [x] Add cutoff check for seeds: `if (!use_cutoff_ || 0.0 <= cutoff_time_)`
  - [x] Add cutoff check in main while loop: `if (use_cutoff_ && time > cutoff_time_) break;`
  - [x] Add cutoff check for neighbors: `if (use_cutoff_ && delay > cutoff_time_) continue;`
  - [x] Ensure nodes AT cutoff time are included (use <= not <)
  - [x] Create 9 tests for delayed mode cutoff
  - [x] All 37 tests passing (19 original + 9 infrastructure + 9 delayed)

**Status**: Delayed mode cutoff complete, early termination working, tests passing. ✅ Step 2 COMPLETE

- [x] Modify `generate_cascade()` for cutoff support (Step 3)
  - [x] Add cutoff check for seeds: `if (!use_cutoff_ || 0.0 <= cutoff_time_)`
  - [x] Add cutoff check in main while loop: `if (use_cutoff_ && time > cutoff_time_) break;`
  - [x] Add cutoff check for neighbors: `if (use_cutoff_ && next_time > cutoff_time_) continue;`
  - [x] Track time properly in non-delayed mode (fixed 1.0 delays)
  - [x] Ensure consistency with delayed mode
  - [x] Create 11 tests for non-delayed mode cutoff
  - [x] All 48 tests passing (19 original + 9 infrastructure + 9 delayed + 11 non-delayed)

**Status**: Non-delayed mode cutoff complete, consistent with delayed mode, all tests passing. ✅ Step 3 COMPLETE

- [x] Update `generate_cascades()` batch method (Step 4) ✅ COMPLETE
  - [x] Pass cutoff to individual cascade generation
  - [x] Ensure thread safety (cutoff should be read-only during generation)
  - [x] Batch generation works correctly with cutoff

**Status**: Batch method properly passes cutoff to individual cascade generation. Thread safety maintained since cutoff variables are read-only during parallel execution. ✅ Step 4 COMPLETE

**Python Implementation** ✅ COMPLETE
- [x] Update `pyCascadeGenerator` class ✅
  - [x] Add `cutoff: Optional[float] = None` parameter to `generate()` method ✅
  - [x] If cutoff is not None, call `self.cascade_model_.set_cutoff(cutoff)` ✅
  - [x] If cutoff is None, preserve any manually set cutoff (don't clear) ✅
  - [x] Maintain backward compatibility: existing code works without changes ✅

- [x] Update type stubs (not needed - Python wrapper uses dynamic typing)

- [x] Update docstrings ✅
  - [x] Explain cutoff parameter purpose ✅
  - [x] Document behavior when cutoff=None ✅
  - [x] Note time semantics ✅

#### Phase 3: Optimization

**Note**: Phase 2 (Core Implementation) is essentially complete with Steps 1-3 fully done and Step 4 mostly done (batch method works, but lacks explicit parallel test).

**Performance Optimizations**
- [ ] Minimize branch prediction penalties
  - [ ] Use `if constexpr` or template specialization if cutoff is known at compile time
  - [ ] Consider separate methods: `generate_cascade()` vs `generate_cascade_with_cutoff()`
  - [ ] Profile: cost of `if (use_cutoff_ && time > cutoff)` in tight loop

---

## PHASE 3: Performance Benchmarking & Documentation 🚀 **CURRENT FOCUS**

### Benchmarking Plan

**Objective**: Measure and document the actual performance benefits of the cutoff feature.

#### Benchmark 1: Speedup vs Cutoff Value ✅ COMPLETE
- [x] Create benchmark script `benchmark_cutoff_speedup.py`
- [x] Test on Erdos-Renyi graph (n=1000, p=0.01)
- [x] Measure time for cutoff at: 0%, 25%, 50%, 75%, 100% of average cascade depth
- [x] Generate 1000 cascades per configuration
- [x] Results: **15.24x speedup at 25% cutoff, 4.16x at 50%**

#### Benchmark 2: Early Termination vs Post-Filtering ✅ COMPLETE
- [x] Compare two approaches:
  - Approach A: Full cascade generation + filter results by time
  - Approach B: Cutoff-based early termination (our implementation)
- [x] Measure time and memory for both
- [x] Test on various graph sizes (100, 500, 1000, 2000 nodes)
- [x] Results: **6.93x average speedup, up to 19.70x**

#### Benchmark 4: Different Graph Topologies ✅ COMPLETE
- [x] Test cutoff performance on:
  - [x] Chain graph (linear propagation) - 1.35x speedup
  - [x] Star graph (burst propagation) - **98.23x speedup**
  - [x] Erdos-Renyi (random) - 2.82x speedup
  - [x] Barabasi-Albert (scale-free) - 1.30x speedup
  - [x] 2D grid graph - 2.93x speedup
- [x] Compare speedup across topologies
- [x] Results: **Average 21.33x speedup across all topologies**

**Benchmark Deliverables:** ✅ COMPLETE
- [x] `benchmarks/benchmark_cutoff_speedup.py` - Main speedup benchmark
- [x] `benchmarks/benchmark_early_vs_post.py` - Comparison benchmark
- [x] `benchmarks/benchmark_topologies.py` - Topology benchmark
- [x] `benchmarks/results/` - Directory with CSV results (3 files)
- [x] `BENCHMARKS.md` - Comprehensive summary document with findings

---

### Documentation Plan

#### README Updates ✅ COMPLETE
- [x] Add "Time Cutoff Feature" section
- [x] Include basic usage example
- [x] Document performance benefits (from benchmarks)
- [x] Add "When to Use Cutoff" guidelines
- [x] Multiple examples (delayed model, manual control, etc.)

#### Example Notebook ✅ COMPLETE
- [x] Create `notebooks/example_cutoff_feature.ipynb`
- [x] Demonstrate:
  - [x] Basic cutoff usage
  - [x] Comparison with/without cutoff
  - [x] Multiple seeds with cutoff
  - [x] Delayed cascades with cutoff
  - [x] Performance visualization
- [x] Include real-world use case (e.g., early cascade detection)
- [x] Manual cutoff control examples

#### API Documentation
- [x] Update docstrings in `_py_cascade_generator.py` ✅ COMPLETE
- [x] Add cutoff parameter to any external API docs (README) ✅ COMPLETE
- [x] Document edge cases and behavior ✅ COMPLETE

---

### Testing Enhancements

**Additional Edge Cases:**
- [ ] Test with empty graph (0 nodes)
- [ ] Test with single node graph
- [ ] Test with disconnected graph
- [ ] Test with cutoff=0.0 on various graph types
- [ ] Test very large cutoff values (e.g., 1e9)

**Property-Based Testing:**
- [ ] Add hypothesis tests for cutoff correctness
- [ ] Test: all returned nodes have time <= cutoff
- [ ] Test: cascade with cutoff ⊆ cascade without cutoff
- [ ] Test: determinism with same random seed

---

- [ ] Memory optimizations
  - [ ] Pre-allocate cascade vector with estimated size based on cutoff
  - [ ] For small cutoffs, use smaller initial capacity
  - [ ] Measure memory savings from early termination

- [ ] Algorithm optimizations
  - [ ] For non-delayed mode: convert cutoff to generation count at start
  - [ ] Skip cutoff check in inner loop if generation < max_generation
  - [ ] Only check cutoff when moving to next generation

- [ ] Batch processing optimizations
  - [ ] If all cascades use same cutoff, set once before batch
  - [ ] Avoid redundant set_cutoff() calls
  - [ ] Test cache locality with cutoff enabled

**Code Quality**
- [ ] Add const correctness
  - [ ] Make cutoff parameter const in methods
  - [ ] Mark cutoff-related members as const where appropriate

- [ ] Add inline hints for hot path
  - [ ] Consider `inline` or `__attribute__((always_inline))` for cutoff checks
  - [ ] Profile-guided optimization

#### Phase 4: Testing
x] Test cutoff functionality ✅ COMPLETE
  - [x] Test cutoff = 0.0 (only seeds)
  - [x] Test cutoff = 1.0 (one generation)
  - [x] Test cutoff = 2.5 (between generations)
  - [x] Test cutoff = infinity (no cutoff)
  - [x] Test cutoff = None (backward compatibility via clear_cutoff)
  - [x] Test negative cutoff (disables via set_cutoff logic)

- [x] Test correctness ✅ COMPLETE
  - [x] Verify no nodes with time > cutoff
  - [x] Verify all nodes with time <= cutoff are included
  - [x] Verify statistical properties unchanged (for given time window)
  - [x] Verify consistency between delayed and non-delayed modes

- [x] Test edge cases ✅ MOSTLY COMPLETE
  - [x] Empty seed (tested)
  - [x] Single generation propagation
  - [x] Exact boundary conditions
  - [ ] Empty graph (not tested yet)
  - [ ] Single node graph (not tested yet)
  - [ ] Disconnected graph (not tested yet)

- [ ] Test performance
  - [ ] Measure speedup with various cutoff values
  - [ ] Verify early termination actually occurs
  - [ ] Check memory usage reduction
  - [ ] Profile overhead of cutoff=None

**Integration Tests**
- [x] Test backward compatibility ✅ COMPLETE
  - [x] Run existing examples without modification (19 original tests still pass)
  - [x] Verify identical results when cutoff not set
  - [x] Test both delayed and non-delayed modes

- [x] Test Python wrapper ✅ MOSTLY COMPLETE
  - [x] Test C++ class directly (manual cutoff setting)
  - [x] Verify Python wrapper still works
  - [ ] Test cutoff parameteCOMPLETE
  - [x] Test C++ class directly (manual cutoff setting) ✅
  - [x] Verify Python wrapper still works ✅
  - [x] Test cutoff parameter in generate() ✅
  - [x] Test with NetworkX graphs (with cutoff) ✅
  - [x] Test batch generation with cutoff ✅
  - [x] Test multiple seeds with cutoff ✅
  - [x] Test with delays and cutoff ✅

**Test Summary**: 70/70 tests passing ✅
- 9 infrastructure tests ✅
- 9 delayed mode tests ✅
- 11 non-delayed mode tests ✅
- 19 original tests (backward compatibility) ✅
- 22 Python wrapper cutoff tests ✅

**Benchmark Suite** 📊 HIGH PRIORITY - NEXT STEP
- [ ] Create benchmark comparing:
  - [ ] Full cascade generation (baseline)
  - [ ] Cascade with cutoff at 25%, 50%, 75% of expected depth
  - [ ] Post-filtering vs early termination (to show actual speedup)
  - [ ] Memory usage comparison
  - [ ] Performance on different graph types (chain, star, ER, BA)
- [ ] Add benchmark results to documentos:
  - [ ] Small graphs (n=100)
  - [ ] Medium graphs (n=10,000)
  - [ ] Large graphs (n=1,000,000)
  - [ ] Various edge densities
  - [ ] Various cutoff values (early, mid, late)

#### Phase 5: Documentation

**Code Documentation**
- [ ] Add detailed comments explaining cutoff logic
- [ ] Document time semantics for delayed vs non-delayed
- [ ] Add examples in code comments
- [ ] Update docstrings with cutoff parameter

**User Documentation**
- [ ] Update README.md with cutoff examples
- [ ] Add "Time-based Analysis" section
- [ ] Explain performance benefits
- [ ] Show use cases (early cascade analysis, time windows)
- [ ] Add visualization of cutoff effect

**API Documentation**
- [ ] Document cutoff parameter in all relevant methods
- [ ] Explain time semantics clearly
- [ ] Provide migration guide (if API changes)
- [ ] Add performance characteristics

#### Phase 6: Validation

**Correctness Validation**
- [ ] Mathematical verification:
  - [ ] Prove cutoff doesn't affect cascade distribution for t <= cutoff
  - [ ] Verify independence of future events
  - [ ] Check consistency with IC model definition

- [ ] Statistical testing:
  - [ ] Compare distributions: full cascade truncated vs cutoff cascade
  - [ ] Run Kolmogorov-Smirnov test
  - [ ] Verify expected cascade size at time t

**Performance Validation**
- [ ] Profile actual speedup
  - [ ] Measure wall-clock time reduction
  - [ ] Measure CPU cycles saved
  - [ ] Verify memory reduction

- [ ] Validate optimization assumptions
  - [ ] Check branch prediction efficiency
  - [ ] Verify no cache performance degradation
  - [ ] Confirm thread safety maintained

### Implementation Notes

**Key Design Decisions**
1. **Cutoff semantics**: Include events AT cutoff time (use `<=` not `<`)
2. **Backward compatibility**: cutoff=None means no cutoff, existing code unchanged
3. **Performance**: Early termination in loop, not post-filtering
4. **Thread safety**: cutoff is set before generation, read-only during
5. **API**: Optional parameter in Python, setter method in C++

**Potential Pitfalls**
- Off-by-one errors at cutoff boundary
- Floating point comparison issues (use epsilon for equality)
- Race conditions in parallel code
- Inconsistent time semantics between delayed/non-delayed
- Performance regression when cutoff=None

**Success Criteria**
- [ ] All existing tests pass
- [ ] All existing examples work unchanged
- [ ] Cutoff provides measurable speedup (>20% for cutoff at 50% of cascade time)
- [ ] No memory leaks or crashes
- [ ] Thread-safe parallel execution
- [ ] Clear, comprehensive documentation

---

### Code Quality & Robustness Improvements ✅ COMPLETE

**Random Number Generation** ✅
- [x] Replaced `std::rand()` with `std::mt19937` (Mersenne Twister)
- [x] Added `std::uniform_real_distribution<double>` for proper random numbers
- [x] Fixed integer overflow in probability calculations
- [x] Thread-safe RNG implementation
- [x] `set_random_seed()` method exposed in Python bindings

**Input Validation** ✅
- [x] C++ validation: seeds, edge probabilities, symptom probabilities, delays
- [x] Python validation: graph structure, node IDs, edge weights, parameter dimensions
- [x] Proper exception handling with clear error messages
- [x] All validation tested and working

**Code Quality** ✅
- [x] Fixed typo: "CascadeSimuulator" → "CascadeSimulator"
- [x] Removed debug text
- [x] Complete type hints in Python code
- [x] Professional docstrings (NumPy/Google style)
- [x] Batch generation uses C++ `generate_cascades()` for efficiency

**Package Configuration** ✅
- [x] Professional description and metadata
- [x] Python >=3.8 compatibility (was >=3.11)
- [x] NetworkX >=2.5 compatibility (was >=3.4.2)
- [x] Keywords, classifiers, and URLs for PyPI
- [x] Dev and test dependencies configured

---

## FUTURE ENHANCEMENTS (Optional)

These items are nice-to-have improvements but not required for production use:
- [ ] Add const correctness to methods that don't modify state
- [ ] Replace magic numbers with named constants
  - [ ] DEFAULT_DELAY = 1.0
  - [ ] DEFAULT_PROBABILITY = 0.5
- [ ] Use `std::deque` instead of `std::list` for active queue
- [ ] Add C++ standard version to CMakeLists.txt (C++14 minimum)
- [ ] Enable compiler warnings (-Wall -Wextra)
- [ ] Add optimization flags for release builds

**Files to modify:**
- [src/main.cpp](src/main.cpp)
- [CMakeLists.txt](CMakeLists.txt)

### Code Quality - Python
- [ ] Remove `# type: ignore` and fix imports properly
- [ ] Add complete type hints for all functions
- [ ] Fix API inconsistency in `generate()`:
  - Option A: Always return `list[Cascade]`
  - Option B: Separate methods `generate_one()` and `generate_many()`
- [ ] Use C++ `generate_cascades()` method instead of Python loop
- [ ] Add proper docstrings (not comments) with numpy/google style
- [ ] Add validation in `__init__` for parameter compatibility
- [ ] Remove or move `if __name__ == "__main__"` to examples/

**Files to modify:**
- [src/cascadesimulator/_py_cascade_generator.py](src/cascadesimulator/_py_cascade_generator.py)

### Type Stubs Completion
- [ ] Complete `cascade_generator_cpp.pyi` with all methods
- [ ] Add docstrings to type stubs
- [ ] Match parameter names between .pyi and C++ implementation
- [ ] Add stubs for dataclasses if needed

**Files to modify:**
- [src/cascadesimulator/cascade_generator_cpp.pyi](src/cascadesimulator/cascade_generator_cpp.pyi)

### Documentation
- [ ] Update README.md description
- [ ] Add "Requirements" section to README (C++ compiler, CMake, etc.)
- [ ] Add "Building from Source" section
- [ ] Add troubleshooting section
- [ ] Explain what `q` parameter means (symptom probability)
- [ ] Add mathematical description of IC model
- [ ] Add advanced usage examples
- [ ] Document output format clearly
- [ ] Add performance characteristics
- [ ] Create CONTRIBUTING.md
- [ ] Create CHANGELOG.md
- [ ] Add citation information (if intended for academic use)

**Files to modify:**
- [README.md](README.md)

**New files:**
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `docs/` directory with detailed API docs

### Project Configuration
- [ ] Fix placeholder in pyproject.toml: "Add your description here"
- [ ] Add proper license field
- [ ] Add keywords for package discovery
- [ ] Add classifiers
- [ ] Add repository URL
- [ ] Add homepage/documentation URL
- [ ] Reconsider `requires-python = ">=3.11"` → try `>=3.8` or `>=3.9`
- [ ] Add test dependencies: pytest, pytest-cov
- [ ] Add dev dependencies: black, ruff/flake8, mypy
- [ ] Update .gitignore with missing patterns

**Files to modify:**
- [pyproject.toml](pyproject.toml)
- [.gitignore](.gitignore)

---

## MEDIUM PRIORITY

### CI/CD Pipeline
- [ ] Create `.github/workflows/` directory
- [ ] Add `test.yml` workflow
  - [ ] Matrix testing across Python 3.8, 3.9, 3.10, 3.11, 3.12
  - [ ] Matrix testing across OS (Ubuntu, macOS, Windows)
  - [ ] Run pytest with coverage
  - [ ] Upload coverage to codecov
- [ ] Add `lint.yml` workflow
  - [ ] Run black, ruff/flake8, mypy
  - [ ] Check formatting
- [ ] Add `build.yml` workflow
  - [ ] Build wheels for multiple platforms
  - [ ] Test installation
- [ ] Add `publish.yml` workflow
  - [ ] Publish to PyPI on release
- [ ] Add status badges to README

**New files:**
- `.github/workflows/test.yml`
- `.github/workflows/lint.yml`
- `.github/workflows/build.yml`
- `.github/workflows/publish.yml`

### Error Handling & Logging
- [ ] Add proper exception types
  - [ ] `InvalidGraphError`
  - [ ] `InvalidParameterError`
  - [ ] `CascadeGenerationError`
- [ ] Add logging support (Python `logging` module)
- [ ] Add progress bars for large batch jobs (using tqdm)
- [ ] Improve error messages to be user-friendly
- [ ] Add warnings for potential issues (e.g., disconnected graph)

**Files to modify:**
- [src/cascadesimulator/_py_cascade_generator.py](src/cascadesimulator/_py_cascade_generator.py)

**New files:**
- `src/cascadesimulator/exceptions.py`

### Performance Optimization
- [ ] Profile code to find bottlenecks
- [ ] Use C++ `generate_cascades()` from Python wrapper
- [ ] Add compiler optimization flags in CMakeLists.txt
- [ ] Consider using contiguous memory for better cache performance
- [ ] Add benchmarking suite
- [ ] Document performance characteristics
- [ ] Consider object pooling for large batch jobs
- [ ] Profile memory usage

**Files to modify:**
- [src/cascadesimulator/_py_cascade_generator.py](src/cascadesimulator/_py_cascade_generator.py)
- [CMakeLists.txt](CMakeLists.txt)

**New files:**
- `benchmarks/benchmark_cascade_generation.py`

### Additional Cascade Models
- [ ] Implement Linear Threshold (LT) model
- [ ] Implement Triggering model
- [ ] Implement Weighted Cascade model
- [ ] Add model selection via parameter
- [ ] Update documentation for new models
- [ ] Add tests for each model

**Files to modify:**
- [src/main.cpp](src/main.cpp)
- [src/cascadesimulator/_py_cascade_generator.py](src/cascadesimulator/_py_cascade_generator.py)

### Code Organization
- [ ] Separate C++ CascadeGenerator into header (.hpp) and implementation (.cpp)
- [ ] Extract QNode and CompareByTime to separate file
- [ ] Create proper C++ namespace
- [ ] Consider factory pattern for cascade models
- [ ] Add abstract base class for cascade models
- [ ] Improve separation of concerns

**Potential new files:**
- `src/cascade_generator.hpp`
- `src/cascade_generator.cpp`
- `src/models/ic_model.hpp`
- `src/utils/priority_queue.hpp`

---

## LOW PRIORITY

### Cascade Analysis Utilities
- [ ] Add method to get cascade size (number of infected nodes)
- [ ] Add method to get cascade depth (maximum time)
- [ ] Add method to compute influence spread statistics
- [ ] Add method to filter cascades by size/depth
- [ ] Add method to compute symptom statistics
- [ ] Export cascades to DataFrame
- [ ] Export cascades to JSON/CSV

**New files:**
- `src/cascadesimulator/analysis.py`

### Visualization Tools
- [ ] Add function to visualize cascade on graph
- [ ] Add function to plot cascade timeline
- [ ] Add function to create animation of cascade spread
- [ ] Integration with matplotlib
- [ ] Integration with networkx drawing
- [ ] Add example visualizations to notebooks

**New files:**
- `src/cascadesimulator/visualization.py`

### Extended Graph Support
- [ ] Support for igraph
- [ ] Support for graph-tool
- [ ] Support for direct adjacency list/matrix input
- [ ] Support for edge list format
- [ ] Automatic graph conversion utilities

**New files:**
- `src/cascadesimulator/graph_utils.py`

### Advanced Features
- [ ] GPU acceleration (CUDA/OpenCL)
- [ ] Distributed computing support
- [ ] Streaming cascade generation (generators instead of lists)
- [ ] Checkpointing for long-running jobs
- [ ] Resume capability
- [ ] Memory-mapped cascades for very large datasets

### Extensibility
- [ ] Plugin system for custom cascade models
- [ ] Callback hooks during cascade generation
- [ ] Custom node/edge attributes support
- [ ] Strategy pattern for different propagation rules
- [ ] Configuration file support (YAML/TOML)

### Developer Experience
- [ ] Add pre-commit hooks
- [ ] Add code formatting configuration (black, clang-format)
- [ ] Add linting configuration (ruff, mypy)
- [ ] Add VS Code workspace settings
- [ ] Add development container (devcontainer.json)
- [ ] Add Makefile for common tasks

**New files:**
- `.pre-commit-config.yaml`
- `pyproject.toml` (formatting config)
- `.clang-format`
- `.vscode/settings.json`
- `.devcontainer/devcontainer.json`
- `Makefile`

---

## MAINTENANCE

### Regular Tasks
- [ ] Review and update dependencies quarterly
- [ ] Monitor for security vulnerabilities
- [ ] Update documentation as features are added
- [ ] Respond to issues and pull requests
- [ ] Tag releases with semantic versioning
- [ ] Update CHANGELOG.md with each release

---

## 📊 CUTOFF FEATURE: COMPLETION SUMMARY

### ✅ COMPLETED (Phases 1-2)

**Core Implementation:** ✅
- Delayed mode cutoff (`generate_cascade_pq`) ✅
- Non-delayed mode cutoff (`generate_cascade`) ✅
- Batch method support (`generate_cascades`) ✅
- Pybind11 bindings and type stubs ✅
- Python wrapper integration (`pyCascadeGenerator.generate()`) ✅
- Comprehensive test suite (51 new tests) ✅
- Full backward compatibility maintained ✅
- Multiple seeds support ✅

**Test Coverage:**
- 9 infrastructure tests ✅
- 9 delayed mode tests ✅
- 11 non-delayed mode tests ✅
- 19 original tests (backward compatibility) ✅
- 22 Python wrapper cutoff tests ✅
- **Total: 70/70 passing ✅**

**Implementation Highlights:**
- Cutoff parameter in Python: `gen.generate(seeds=[0], cutoff=2.0)` ✅
- Backward compatible: `gen.generate(seeds=[0])` still works ✅
- Manual setting supported: `gen.cascade_model_.set_cutoff(2.0)` ✅
- Multiple seeds work correctly with cutoff ✅
- Works with both delayed and non-delayed cascades ✅

### 🚧 REMAINING WORK

**High Priority (Phase 3):**
1. **Performance Benchmarks** 📊 - Measure actual speedup with different cutoff values
2. **Documentation** 📝 - Update README with cutoff examples and usage guide
3. **Example Notebook** 📓 - Create Jupyter notebook demonstrating cutoff feature

**Medium Priority:**
4. Edge case tests (empty/single/disconnected graphs)
5. Performance optimization based on benchmark results
6. Memory usage profiling

**Low Priority:**
7. Advanced optimizations (if benchmarks show opportunities)
8. Additional graph types in benchmarks

### 🎯 Next Immediate Actions
1. **Create comprehensive benchmarks** to measure speedup and validate performance benefits
2. **Document the feature** with clear examples in README
3. **Add example notebook** showing real-world usage
**Implement Python wrapper cutoff parameter** to enable user-facing functionality. This is the last critical piece for basic feature completion.

### Future Considerations
- [ ] Consider publishing to conda-forge
- [ ] Consider creating Docker image
- [ ] Consider web API wrapper (FastAPI)
- [ ] Consider Julia bindings
- [ ] Consider R bindings
- [ ] Research latest cascade modeling techniques
- [ ] Monitor performance on real-world datasets

---

## Notes

### Quick Wins (Easy, High Impact)
1. Fix typo and debug text in hello_from_bin
2. Remove duplicate pybind11 registrations
3. Fix pyproject.toml description
4. Update .gitignore
5. Add proper docstrings
6. Fix type hints

### Weekend Project Ideas
1. Add comprehensive test suite
2. Set up CI/CD pipeline
3. Write proper documentation
4. Fix random number generation

### Research Required
- Best practices for pybind11 exception handling
- Performance comparison: Python loop vs C++ batch generation
- Other cascade models in literature
- Graph library interoperability standards
