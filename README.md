
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
pip install git+https://github.com/TUNI-Financial-Computing/CascadeSimulator.git@1-test-cascadesimulator-installation-and-functionality
```

### Using Conda (recommended)

1. Create a new Conda environment (optional but recommended):

   ```bash
   conda create -n cascadesimulator
   conda activate cascadesimulator
   ```

2. Install CascadeSimulator:

   ```bash
   pip install git+https://github.com/TUNI-Financial-Computing/CascadeSimulator.git@1-test-cascadesimulator-installation-and-functionality
   ```

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
