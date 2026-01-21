# TODO List for CascadeSimulator Improvements

## MAJOR FEATURE: Time Cutoff Support

### Overview
Implement time-based cutoff parameter for cascade generation with full backward compatibility and optimal performance.

### Implementation Plan

#### Phase 1: Design & Architecture (Complete First)

**Step 1: API Design**
- [ ] Design C++ API for cutoff parameter
  - Add `double cutoff_time_` member variable (default: -1.0 for no cutoff)
  - Add `bool use_cutoff_` flag for performance
  - Add `void set_cutoff(double cutoff_time)` method
  - Update method signatures to accept optional cutoff
- [ ] Design Python API for cutoff parameter
  - Add `cutoff: Optional[float] = None` to `generate()` method
  - Ensure backward compatibility (existing calls work unchanged)
  - Update type hints and docstrings

**Step 2: Performance Analysis**
- [ ] Analyze cutoff check cost in tight loop
  - Profile branch prediction impact
  - Compare: check every iteration vs. priority queue early exit
  - Measure overhead of cutoff=None vs no cutoff at all
- [ ] Determine optimal implementation per mode:
  - **Delayed mode (PQ)**: Check cutoff when popping from queue
  - **Non-delayed mode**: Check generation depth OR time counter
  - **Batch mode**: Apply cutoff to all cascades efficiently

**Step 3: Algorithm Design**
- [ ] Design cutoff logic for `generate_cascade_pq()` (delayed cascades)
  ```
  Algorithm:
  1. When popping node from PQ, check if time > cutoff
  2. If yes, break loop early (don't process this node)
  3. When adding neighbors, only add if new_time <= cutoff
  4. Result: Natural early termination, no wasted work
  ```
- [ ] Design cutoff logic for `generate_cascade()` (non-delayed cascades)
  ```
  Algorithm:
  1. Track current time (increments by 1.0 each generation)
  2. When time exceeds cutoff, stop processing active queue
  3. Alternative: Track generation depth and stop at ceil(cutoff)
  4. Include all nodes at time <= cutoff
  ```
- [ ] Handle edge cases:
  - Cutoff = 0.0 (only seed nodes)
  - Cutoff between time steps (for discrete time)
  - Cutoff before any propagation
  - Very large cutoff (essentially no cutoff)

#### Phase 2: Core Implementation

**C++ Implementation - STEP 1 COMPLETED ✅**
- [x] Add cutoff support to `CascadeGenerator` class
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

- [ ] Modify `generate_cascade()` for cutoff support (Step 3)
  - [ ] Add cutoff check in main while loop
  - [ ] Track time properly in non-delayed mode
  - [ ] Optimize: could track generation depth instead of time
  - [ ] Ensure consistency with delayed mode

- [ ] Update `generate_cascades()` batch method (Step 4)
  - [ ] Pass cutoff to individual cascade generation
  - [ ] Ensure thread safety (cutoff should be read-only during generation)
  - [ ] Test: parallel execution with cutoff

**Python Implementation**
- [ ] Update `pyCascadeGenerator` class
  - [ ] Add `cutoff: Optional[float] = None` parameter to `generate()` method
  - [ ] If cutoff is not None, call `self.cascade_model_.set_cutoff(cutoff)`
  - [ ] If cutoff is None, ensure no cutoff is applied (call `clear_cutoff()` or use flag)
  - [ ] Maintain backward compatibility: existing code works without changes

- [ ] Update type stubs
  - [ ] Add cutoff parameter to method signatures in `.pyi` file
  - [ ] Document expected behavior

- [ ] Update docstrings
  - [ ] Explain cutoff parameter purpose
  - [ ] Provide examples with and without cutoff
  - [ ] Explain time semantics (discrete vs continuous)
  - [ ] Note performance benefits

#### Phase 3: Optimization

**Performance Optimizations**
- [ ] Minimize branch prediction penalties
  - [ ] Use `if constexpr` or template specialization if cutoff is known at compile time
  - [ ] Consider separate methods: `generate_cascade()` vs `generate_cascade_with_cutoff()`
  - [ ] Profile: cost of `if (use_cutoff_ && time > cutoff)` in tight loop

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

**Unit Tests**
- [ ] Test cutoff functionality
  - [ ] Test cutoff = 0.0 (only seeds)
  - [ ] Test cutoff = 1.0 (one generation)
  - [ ] Test cutoff = 2.5 (between generations)
  - [ ] Test cutoff = infinity (no cutoff)
  - [ ] Test cutoff = None (backward compatibility)
  - [ ] Test negative cutoff (should disable or error)

- [ ] Test correctness
  - [ ] Verify no nodes with time > cutoff
  - [ ] Verify all nodes with time <= cutoff are included
  - [ ] Verify statistical properties unchanged (for given time window)
  - [ ] Compare truncated cascade vs full cascade[:cutoff]

- [ ] Test edge cases
  - [ ] Empty graph
  - [ ] Single node graph
  - [ ] Disconnected graph
  - [ ] Graph with no propagation (p=0)
  - [ ] Graph with full propagation (p=1)

- [ ] Test performance
  - [ ] Measure speedup with various cutoff values
  - [ ] Verify early termination actually occurs
  - [ ] Check memory usage reduction
  - [ ] Profile overhead of cutoff=None

**Integration Tests**
- [ ] Test backward compatibility
  - [ ] Run existing examples without modification
  - [ ] Verify identical results when cutoff=None
  - [ ] Test both delayed and non-delayed modes

- [ ] Test Python wrapper
  - [ ] Test cutoff parameter in generate()
  - [ ] Test with NetworkX graphs
  - [ ] Test batch generation with cutoff
  - [ ] Test type checking passes

**Benchmark Suite**
- [ ] Create benchmark comparing:
  - [ ] Full cascade generation
  - [ ] Cascade with cutoff (various values)
  - [ ] Post-filtering vs early termination
  - [ ] Delayed vs non-delayed with cutoff

- [ ] Measure across different scenarios:
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

## CRITICAL (Fix Immediately)

### Random Number Generation - Thread Safety
- [ ] Replace `std::rand()` with `std::mt19937` or `std::mt19937_64` from `<random>`
- [ ] Replace `std::srand()` with proper seed management per thread
- [ ] Use thread-local random engines for OpenMP parallel sections
- [ ] Fix integer overflow: `std::rand() / (RAND_MAX + 1.0)` → proper casting
- [ ] Expose `set_random_seed` method in Python bindings
- [ ] Add test to verify reproducibility with same seed

**Files to modify:**
- [src/main.cpp](src/main.cpp)

### Input Validation
- [ ] Validate seed set is not empty
- [ ] Validate all seed node IDs exist in graph (0 <= id < n_nodes)
- [ ] Validate edge_probs dimensions match graph structure
- [ ] Validate node_symp_probs length equals n_nodes
- [ ] Validate edge_delays dimensions match graph structure
- [ ] Replace `assert()` with proper exception throwing
- [ ] Add Python-side validation in `pyCascadeGenerator.__init__`

**Files to modify:**
- [src/main.cpp](src/main.cpp)
- [src/cascadesimulator/_py_cascade_generator.py](src/cascadesimulator/_py_cascade_generator.py)

---

## HIGH PRIORITY

### Testing Infrastructure
- [ ] Create `tests/` directory
- [ ] Add pytest configuration in `pyproject.toml`
- [ ] Write C++ unit tests (using Catch2 or Google Test)
  - [ ] Test `generate_cascade()` with known seed
  - [ ] Test `generate_cascades()` batch generation
  - [ ] Test edge probability handling
  - [ ] Test symptom probability handling
  - [ ] Test delay handling
  - [ ] Test thread safety
- [ ] Write Python unit tests
  - [ ] Test `pyCascadeGenerator` initialization
  - [ ] Test graph conversion
  - [ ] Test cascade generation
  - [ ] Test Observation and Cascade dataclasses
  - [ ] Test error handling
- [ ] Add integration tests
- [ ] Set up test coverage reporting

**New files:**
- `tests/test_cascade_generator_cpp.cpp`
- `tests/test_py_cascade_generator.py`
- `tests/test_integration.py`
- `pytest.ini` or update `pyproject.toml`

### Code Quality - C++
- [ ] Fix typo: "CascadeSimuulator" → "CascadeSimulator" (line 8)
- [ ] Remove debug text "!22" (line 8)
- [ ] Remove duplicate pybind11 method registrations (lines 258-259)
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
