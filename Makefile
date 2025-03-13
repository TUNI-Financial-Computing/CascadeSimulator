# Compiler and flags
CXX = g++
CXXFLAGS = -O3 -Wall -shared -std=c++20 -fPIC

## Make sure to change the path to your python include and lib directories
PYTHON_INCLUDE = $(shell python3-config --includes)
PYBIND11_INCLUDE = -I/Users/hansen/anaconda3/envs/george/lib/python3.12/site-packages/pybind11/include
PYTHON_LIB_DIR = /Users/hansen/anaconda3/envs/george/lib
PYTHON_LIB = -L$(PYTHON_LIB_DIR) -lpython3.12

# Output shared library
TARGET = cascade_generator$(shell python3-config --extension-suffix)

# Source files
SRCS = cascade_generator.cpp
OBJS = $(SRCS:.cpp=.o)

# Build shared library with explicit Python & pybind11 linking
$(TARGET): $(SRCS)
	$(CXX) $(CXXFLAGS) $(PYTHON_INCLUDE) $(PYBIND11_INCLUDE) -o $(TARGET) $(SRCS) $(PYTHON_LIB) -undefined dynamic_lookup

# Clean build files
clean:
	rm -f $(TARGET) $(OBJS)
