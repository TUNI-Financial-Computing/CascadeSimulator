# Contributing to CascadeSimulator

Thank you for your interest in contributing to CascadeSimulator! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. Please be respectful and constructive in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/CascadeSimulator.git
   cd CascadeSimulator
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/CascadeSimulator.git
   ```

## Development Setup

### Prerequisites

- **Python**: 3.8 or higher
- **C++ Compiler**: C++14 or higher support
  - macOS: Xcode Command Line Tools or clang
  - Linux: gcc/g++ 5.0+ or clang 3.4+
  - Windows: MSVC 2017+ or MinGW-w64
- **CMake**: 3.15 or higher
- **pybind11**: Installed automatically during setup

### Installation for Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install in editable mode with dev dependencies:
   ```bash
   pip install -e ".[dev,test]"
   ```

3. Verify the installation:
   ```bash
   python -c "from cascadesimulator import PyCascadeGenerator; print('Success!')"
   ```

### Building C++ Extensions

If you make changes to C++ code in `src/main.cpp`:

```bash
pip install --no-build-isolation --editable .
```

This rebuilds the C++ extension and reinstalls the package.

## Making Changes

### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions or modifications

### Workflow

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, following the code style guidelines below

3. Add tests for new functionality

4. Run the test suite to ensure everything passes

5. Commit your changes with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: brief description"
   ```

## Testing

### Running Tests

Run the full test suite:
```bash
pytest tests/python/ -v
```

Run specific test files:
```bash
pytest tests/python/test_py_cascade_generator.py -v
```

Run with coverage report:
```bash
pytest tests/python/ --cov=cascadesimulator --cov-report=html
```

Run benchmarks:
```bash
pytest tests/benchmarks/ -v
```

### Writing Tests

- Place Python tests in `tests/python/`
- Use descriptive test names: `test_<functionality>_<scenario>`
- Include both positive and negative test cases
- Test edge cases and error conditions
- Use `pytest` fixtures from `conftest.py` when appropriate

Example test structure:
```python
def test_feature_name_expected_behavior():
    """Test that feature behaves correctly under normal conditions."""
    # Arrange
    generator = PyCascadeGenerator(...)
    
    # Act
    result = generator.generate(...)
    
    # Assert
    assert len(result) > 0
    assert result[0]['node'] in expected_nodes
```

## Code Style

### Python

- **Style Guide**: PEP 8
- **Formatter**: `black` (line length 100)
- **Linter**: `ruff`
- **Type Checker**: `mypy`

Run formatters and linters:
```bash
black src/cascadesimulator tests/
ruff check src/cascadesimulator tests/
mypy src/cascadesimulator
```

### Python Best Practices

- Use type hints for all function signatures
- Write NumPy-style docstrings for public functions and classes
- Keep functions focused and single-purpose
- Use descriptive variable names
- Validate inputs and provide clear error messages

### C++

- **Standard**: C++14 or higher
- **Style**: Follow existing code patterns
- **Naming**: 
  - Classes: `PascalCase`
  - Functions: `snake_case`
  - Private members: `trailing_underscore_`
- **Memory**: Use RAII principles, avoid manual memory management
- **Comments**: Document complex algorithms and non-obvious behavior

### C++ Best Practices

- Use `std::` standard library over raw pointers where possible
- Validate all inputs and throw `std::invalid_argument` or `std::out_of_range` for errors
- Use modern random number generation (`std::mt19937`, not `std::rand()`)
- Keep functions focused on single responsibilities
- Use const correctness throughout

## Submitting Changes

### Pull Request Process

1. Update documentation if you've changed APIs or added features

2. Update CHANGELOG.md with a brief description of your changes

3. Ensure all tests pass and code follows style guidelines

4. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Open a Pull Request on GitHub with:
   - Clear title describing the change
   - Description of what changed and why
   - Reference to any related issues
   - Screenshots/examples if applicable

### PR Review Process

- Maintainers will review your PR and may request changes
- Address feedback by pushing new commits to your branch
- Once approved, maintainers will merge your PR

## Reporting Issues

### Bug Reports

Include:
- Python version (`python --version`)
- Operating system and version
- CascadeSimulator version
- Minimal code example reproducing the issue
- Full error message and traceback
- Expected vs. actual behavior

### Feature Requests

Include:
- Clear description of the proposed feature
- Use cases and examples
- Potential implementation approach (optional)
- Any relevant references or prior art

## Development Tips

### Debugging C++ Extensions

Add debug prints in `src/main.cpp`:
```cpp
std::cout << "Debug: variable value = " << value << std::endl;
```

Rebuild and test:
```bash
pip install --no-build-isolation --editable . && python your_test.py
```

### Performance Profiling

Use pytest-benchmark for performance testing:
```bash
pytest tests/benchmarks/benchmark_baseline.py -v --benchmark-only
```

Profile Python code:
```bash
python -m cProfile -o output.prof your_script.py
python -m pstats output.prof
```

### Working with Notebooks

Example notebooks are in `notebooks/`:
- `example_pyCascadeGenerator.ipynb` - Python interface examples
- `example_CascadeGenerator.ipynb` - C++ interface examples

Update these if you change the API or add new features.

## Questions?

If you have questions about contributing, feel free to:
- Open an issue with the `question` label
- Reach out to maintainers
- Check existing documentation and issues

## License

By contributing to CascadeSimulator, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to CascadeSimulator! 🎉
