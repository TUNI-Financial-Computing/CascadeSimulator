# Makefile for building cascade_generator Python extension on macOS (Apple Silicon)
# using the Homebrew-installed LLVM at /opt/homebrew/opt/llvm/bin/clang++.

CXX = /opt/homebrew/opt/llvm/bin/clang++
CXXFLAGS = -std=c++20 -O3 -fPIC -fopenmp \
           -undefined dynamic_lookup  # <-- Key flag on macOS
PYBIND11_INCLUDES = $(shell python3 -m pybind11 --includes)
EXT_SUFFIX = $(shell python3-config --extension-suffix)

# Paths to Homebrew LLVM's includes and libraries (Apple Silicon).
LLVM_INCLUDE_DIR = /opt/homebrew/opt/llvm/include
LLVM_LIB_DIR = /opt/homebrew/opt/llvm/lib

# Name of the compiled Python extension
TARGET = cascade_generator$(EXT_SUFFIX)

all: $(TARGET)

$(TARGET): cascade_generator.cpp
	$(CXX) $(CXXFLAGS) \
	    $(PYBIND11_INCLUDES) \
	    -I$(LLVM_INCLUDE_DIR) \
	    -L$(LLVM_LIB_DIR) \
	    cascade_generator.cpp \
	    -shared -o $(TARGET)

clean:
	rm -f $(TARGET)
