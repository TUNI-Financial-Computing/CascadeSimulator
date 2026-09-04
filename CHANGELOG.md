# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of CascadeSimulator package
- High-performance C++ cascade generator with Python bindings
- Support for delayed and non-delayed cascade simulations
- Comprehensive input validation for all parameters
- Professional NumPy-style documentation throughout
- Support for Python 3.8+
- Example Jupyter notebooks demonstrating usage
- Comprehensive test suite (70+ tests)
- Performance benchmarks

### Features
- **Core Cascade Generation**: Simulate information cascades on directed graphs
- **Symptom Modeling**: Track symptom emergence during cascades
- **Delay Support**: Model delays in edge activation
- **Cutoff Modes**: 
  - Time-based cutoffs for simulation control
  - Delayed and non-delayed propagation modes
- **Batch Generation**: Efficient generation of multiple cascades
- **Modern C++ Backend**: Uses Mersenne Twister RNG for high-quality randomness
- **Type-Safe Python Interface**: Full type hints and runtime validation

### Technical Improvements
- Replaced `std::rand()` with `std::mt19937` for thread-safe random number generation
- Added comprehensive input validation in both C++ and Python layers
- Professional error messages with detailed parameter requirements
- Optimized batch generation using C++ `generate_cascades()` method
- PyPI-ready package configuration with proper metadata

### Documentation
- Complete API documentation with NumPy-style docstrings
- Example notebooks for C++ and Python interfaces
- Testing plan and baseline results documentation
- Codebase analysis and implementation planning documents

## [0.1.0] - 2026-09-04

Initial public release.

### Added
- Full cascade simulation functionality
- Python package with C++ extensions
- Comprehensive documentation and examples
- Production-ready test coverage

---

**Note**: This is a pre-release changelog. Version 0.1.0 will be tagged upon first PyPI publication.
