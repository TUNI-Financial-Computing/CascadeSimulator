
# CascadeSimulator

## Overview

CascadeSimulator is a Python package for simulating cascades in networks using various cascade models. It utilizes networkx for graph creation and implements an Independent Cascade model (IC) for simulating the spread of information or influence through networks.

## Installation

### Prerequisites

Before installing, ensure you have the following dependencies:

- Python (>= 3.8)
- pip
- conda (optional, for environment management)

### Using pip

To install CascadeSimulator directly from the GitHub repository, you can use the following command:

```bash
pip install git+https://github.com/TUNI-Financial-Computing/CascadeSimulator.git
```

To install from a specific branch (e.g., `dev` branch):

```bash
pip install git+https://github.com/TUNI-Financial-Computing/CascadeSimulator.git@dev
```

### Using Conda (recommended)

1. Create a new Conda environment (optional but recommended):

   ```bash
   conda create -n cascadesimulator
   conda activate cascadesimulator
   ```

2. Install CascadeSimulator:

   ```bash
   pip install git+https://github.com/TUNI-Financial-Computing/CascadeSimulator.git
   ```

### Building from Source

If you want to build CascadeSimulator from source (e.g., for development or to use the latest changes):

#### Prerequisites for Building

- **Python**: 3.8 or higher
- **C++ Compiler**: 
  - macOS: Xcode Command Line Tools or clang
  - Linux: gcc/g++ 5.0+ or clang 3.4+
  - Windows: MSVC 2017+ or MinGW-w64
- **CMake**: 3.15 or higher (installed automatically if needed)
- **pybind11**: Installed automatically during build

#### Build Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/TUNI-Financial-Computing/CascadeSimulator.git
   cd CascadeSimulator
   ```

2. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:

   ```bash
   pip install -e .
   ```

   This will compile the C++ extensions and install the package in editable mode.

4. For development with additional tools (formatters, linters, type checkers):

   ```bash
   pip install -e ".[dev,test]"
   ```

5. Verify the installation:

   ```bash
   python -c "from cascadesimulator import pyCascadeGenerator; print('Build successful!')"
   ```

#### Rebuilding After Changes

If you modify the C++ source code (`src/main.cpp`), rebuild with:

```bash
pip install --no-build-isolation --editable .
```

#### Troubleshooting Build Issues

**Compiler not found:**
- macOS: Install Xcode Command Line Tools: `xcode-select --install`
- Linux: Install build essentials: `sudo apt-get install build-essential` (Ubuntu/Debian) or `sudo yum install gcc-c++` (RHEL/CentOS)
- Windows: Install Visual Studio with C++ build tools

**CMake errors:**
- Ensure CMake ≥ 3.15: `cmake --version`
- Update pip: `pip install --upgrade pip setuptools wheel`

**pybind11 issues:**
- Install manually: `pip install pybind11`
- Clear build cache: `rm -rf build/ *.egg-info` and retry

For detailed contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Usage

Here’s an example of how to use the `CascadeSimulator` package to generate cascades in a network:

```python
from random import random
import networkx as nx
from cascadesimulator import pyCascadeGenerator

# Create a random graph using the Erdős-Rényi model
graph = nx.erdos_renyi_graph(100, 0.1)

# Assign random weights to the edges
for edge in graph.edges():
    graph[edge[0]][edge[1]]['weight'] = 0.1 + 0.2 * random()

# Define symptom probabilities for nodes
q = [0.5 + 0.5 * random() for _ in graph.nodes()]

# Initialize the cascade generator
cascade_generator = pyCascadeGenerator(
    graph=graph,
    cascade_model="IC",
    q=q
)

# Define a seed set and the number of cascades to generate
seed = [0]
num_cascades = 10

# Generate the cascades
cascades = cascade_generator.generate(seed, num_cascades)

# Use the generated cascades
for cascade in cascades:
    print(cascade)

# Access a specific cascade
cascade = cascades[0]
print(cascade)

# Get the length of the cascade
print(len(cascade))

# Access an observation in the cascade
print(cascade[76])  # Outputs: Observation(node_id=..., time=..., symptom=...)
```
## Time Cutoff Feature

The cutoff feature allows you to limit cascade generation to a specific time window, significantly improving performance for early-stage cascade analysis.

### Basic Usage

```python
from cascadesimulator import pyCascadeGenerator
import networkx as nx

# Create a graph
graph = nx.erdos_renyi_graph(1000, 0.01, directed=True)
for edge in graph.edges():
    graph[edge[0]][edge[1]]['weight'] = 0.3

# Initialize generator
gen = pyCascadeGenerator(graph, cascade_model='IC')

# Generate cascade with 5.0 time unit cutoff
cascades = gen.generate(seeds=[0], num_cascades=100, cutoff=5.0)

# Only nodes activated within time [0, 5.0] are included
```

### Performance Benefits

The cutoff feature provides early termination of cascade generation, avoiding unnecessary computation:

- **15.24x speedup** at 25% cutoff (stopping at 25% of average cascade depth)
- **4.16x speedup** at 50% cutoff
- **6.93x average speedup** compared to post-filtering (generating full cascade then filtering)

Performance varies by graph topology:
- **Grid graphs**: 8.58x speedup (long propagation paths benefit most)
- **Random graphs (Erdős-Rényi)**: 2.96x speedup
- **Community structures (SBM)**: 2.38x speedup
- **Scale-free (Barabási-Albert)**: 1.20x speedup (hubs create very successful cascades)

### When to Use Cutoff

Use the cutoff parameter when:
- **Early detection**: You only care about initial cascade spread (e.g., first 24 hours of news diffusion)
- **Real-time analysis**: Processing cascades as they develop with time constraints
- **Large-scale simulations**: Reducing computation time for extensive parameter sweeps
- **Comparative studies**: Analyzing cascade growth at specific time points across different networks

### Examples

**Multiple Seeds with Cutoff:**
```python
# Generate cascades from multiple seed nodes
seeds = [0, 10, 20]
cascades = gen.generate(seeds=seeds, num_cascades=50, cutoff=10.0)
```

**Delayed Cascade Model:**
```python
# Works with delayed cascades (exponential transmission times)
gen = pyCascadeGenerator(graph, cascade_model='IC', delay=True, scale=2.0)
cascades = gen.generate(seeds=[0], num_cascades=100, cutoff=15.0)
```

**Manual Cutoff Control:**
```python
# Set cutoff once, generate multiple times
gen.cascade_model_.set_cutoff(5.0)
cascades1 = gen.generate(seeds=[0], num_cascades=100)
cascades2 = gen.generate(seeds=[5], num_cascades=100)

# Clear cutoff to generate full cascades again
gen.cascade_model_.clear_cutoff()
full_cascades = gen.generate(seeds=[0], num_cascades=100)
```

**Backward Compatibility:**
```python
# Omitting cutoff parameter generates full cascades (same as before)
full_cascades = gen.generate(seeds=[0], num_cascades=100)
```

## Troubleshooting

### Installation Issues

#### ImportError: No module named 'cascadesimulator'

**Problem:** Package not installed or wrong environment activated.

**Solution:**
```bash
# Verify you're in the correct environment
which python

# Install or reinstall the package
pip install git+https://github.com/TUNI-Financial-Computing/CascadeSimulator.git

# Or if building from source
pip install -e .
```

#### Compilation Failed / C++ Extension Build Errors

**Problem:** Missing compiler or incompatible version.

**Solutions:**

**macOS:**
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Verify installation
clang --version
```

**Linux (Ubuntu/Debian):**
```bash
# Install build essentials
sudo apt-get update
sudo apt-get install build-essential cmake

# Verify installation
gcc --version
cmake --version
```

**Linux (RHEL/CentOS):**
```bash
sudo yum install gcc-c++ cmake
```

**Windows:**
- Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/) with C++ support
- Or install [MinGW-w64](https://www.mingw-w64.org/)

**Additional steps:**
```bash
# Upgrade build tools
pip install --upgrade pip setuptools wheel

# Clear previous build artifacts
rm -rf build/ *.egg-info

# Retry installation
pip install -e . --no-cache-dir
```

#### CMake Error: Could not find pybind11

**Solution:**
```bash
pip install pybind11
pip install -e .
```

### Runtime Issues

#### ValueError: Seed node X not in graph

**Problem:** Trying to start cascade from non-existent node.

**Solution:**
```python
# Verify seed nodes are in the graph
seed = [0, 5, 10]
valid_seeds = [s for s in seed if s in graph.nodes()]
cascades = gen.generate(seeds=valid_seeds, num_cascades=100)

# Or check before generation
if all(s in graph.nodes() for s in seed):
    cascades = gen.generate(seeds=seed, num_cascades=100)
```

#### ValueError: Edge probabilities must be between 0 and 1

**Problem:** Graph edge weights outside valid range.

**Solution:**
```python
# Check edge weights
for u, v, data in graph.edges(data=True):
    weight = data.get('weight', 0)
    if not (0 <= weight <= 1):
        print(f"Invalid weight: {u}->{v}: {weight}")

# Fix by clamping or normalizing
for u, v in graph.edges():
    graph[u][v]['weight'] = max(0.0, min(1.0, graph[u][v]['weight']))
```

#### Empty Cascades Generated

**Problem:** Seed nodes have no outgoing edges or very low probabilities.

**Solution:**
```python
# Check seed node connectivity
for seed_node in seed:
    out_degree = graph.out_degree(seed_node)
    print(f"Node {seed_node} out-degree: {out_degree}")

# Try different seeds with higher connectivity
# Or increase edge probabilities
for edge in graph.edges():
    graph[edge[0]][edge[1]]['weight'] = 0.5  # Higher activation probability
```

### Performance Issues

#### Cascade Generation Too Slow

**Solutions:**

1. **Use cutoff parameter** for early-stage analysis:
```python
# Only generate first 10 time units
cascades = gen.generate(seeds=[0], num_cascades=1000, cutoff=10.0)
```

2. **Reduce edge probabilities** to create smaller cascades:
```python
for edge in graph.edges():
    graph[edge[0]][edge[1]]['weight'] *= 0.5  # Halve probabilities
```

3. **Use C++ batch generation** instead of Python loops:
```python
# Good: Single call for multiple cascades
cascades = gen.generate(seeds=[0], num_cascades=1000)

# Avoid: Multiple separate calls
# cascades = [gen.generate(seeds=[0], num_cascades=1) for _ in range(1000)]
```

#### High Memory Usage

**Problem:** Generating very large cascades or many cascades at once.

**Solution:**
```python
# Generate in smaller batches
all_cascades = []
batch_size = 100
for i in range(0, total_cascades, batch_size):
    batch = gen.generate(seeds=[0], num_cascades=batch_size)
    all_cascades.extend(batch)
    # Process or save batch before continuing
```

### Graph Issues

#### NetworkX Graph Not Directed

**Problem:** Some cascade models require directed graphs.

**Solution:**
```python
# Convert undirected to directed
if not graph.is_directed():
    graph = graph.to_directed()

# Or create directed graph from start
graph = nx.DiGraph()
# ... add nodes and edges
```

#### Missing Edge Weights

**Problem:** Edges need 'weight' attribute for probabilities.

**Solution:**
```python
# Add default weights to all edges
for edge in graph.edges():
    if 'weight' not in graph[edge[0]][edge[1]]:
        graph[edge[0]][edge[1]]['weight'] = 0.3  # Default probability
```

### Getting Help

If you encounter issues not covered here:

1. **Check existing issues**: [GitHub Issues](https://github.com/TUNI-Financial-Computing/CascadeSimulator/issues)
2. **Enable verbose output**: Run with `-v` flag or add debug prints
3. **Minimal example**: Create smallest code that reproduces the problem
4. **System info**: Include Python version, OS, and package version
5. **Open an issue**: Provide minimal example and full error traceback

For development and contribution questions, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Citation

If you use CascadeSimulator in your research, please cite:

```bibtex
@software{hansen_baltakys_2026_cascadesimulator,
  author  = {Henri Hansen and Kęstutis Baltakys},
  title   = {CascadeSimulator},
  year    = {2026},
  version = {0.1.0},
  url     = {https://github.com/TUNI-Financial-Computing/CascadeSimulator}
}
```

**Academic Use:**
- Include the above citation in your references
- Mention CascadeSimulator in your acknowledgments
- Consider citing relevant cascade model papers depending on which model you use

**Key Features to Mention:**
- High-performance C++ backend with Python bindings
- Time cutoff optimization (up to 15x speedup)
- Support for delayed and non-delayed cascade models
- Comprehensive validation and error handling

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Setting up development environment
- Code style and testing requirements
- Submitting pull requests
- Reporting issues

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

## Contact

For questions, suggestions, or collaborations:
- Open an issue on [GitHub](https://github.com/TUNI-Financial-Computing/CascadeSimulator/issues)
- Check the documentation and examples in the repository
