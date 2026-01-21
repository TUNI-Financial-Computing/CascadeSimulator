# TODO List for CascadeSimulator Improvements

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
