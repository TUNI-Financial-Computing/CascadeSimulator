#!/usr/bin/env bash

echo "=== Checking for Homebrew ==="
if ! command -v brew &> /dev/null
then
    echo "Homebrew not found. Please install Homebrew from https://brew.sh/ and rerun this script."
    exit 1
fi

echo "=== Updating Homebrew & installing LLVM + libomp ==="
brew update
brew install llvm libomp

# Homebrew installs LLVM either under /usr/local/opt (Intel Macs) or /opt/homebrew/opt (Apple Silicon).
# Detect which location exists:
if [ -d "/usr/local/opt/llvm" ]; then
    LLVM_DIR="/usr/local/opt/llvm"
elif [ -d "/opt/homebrew/opt/llvm" ]; then
    LLVM_DIR="/opt/homebrew/opt/llvm"
else
    echo "Could not find Homebrew LLVM installation under /usr/local/opt/llvm or /opt/homebrew/opt/llvm."
    echo "Please locate your LLVM installation and update LLVM_DIR in this script accordingly."
    exit 1
fi

echo "=== Setting environment variables for Homebrew LLVM ==="
export PATH="$LLVM_DIR/bin:$PATH"
export CPATH="$LLVM_DIR/include:$CPATH"
export LIBRARY_PATH="$LLVM_DIR/lib:$LIBRARY_PATH"
export LD_LIBRARY_PATH="$LLVM_DIR/lib:$LD_LIBRARY_PATH"
export DYLD_LIBRARY_PATH="$LLVM_DIR/lib:$DYLD_LIBRARY_PATH"

echo
echo "Environment variables set for this shell session:"
echo "  PATH=$PATH"
echo "  CPATH=$CPATH"
echo "  LIBRARY_PATH=$LIBRARY_PATH"
echo "  LD_LIBRARY_PATH=$LD_LIBRARY_PATH"
echo "  DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH"
echo
echo "=== Checking Clang version ==="
clang++ --version || echo "Could not run clang++ from PATH."

echo
echo "If you want these variables set for every new shell session, add the following lines"
echo "to your shell startup file (e.g., ~/.bashrc or ~/.zshrc):"
echo
echo "    export PATH=\"$LLVM_DIR/bin:\$PATH\""
echo "    export CPATH=\"$LLVM_DIR/include:\$CPATH\""
echo "    export LIBRARY_PATH=\"$LLVM_DIR/lib:\$LIBRARY_PATH\""
echo "    export LD_LIBRARY_PATH=\"$LLVM_DIR/lib:\$LD_LIBRARY_PATH\""
echo "    export DYLD_LIBRARY_PATH=\"$LLVM_DIR/lib:\$DYLD_LIBRARY_PATH\""
echo
echo "=== Done! ==="
echo "Now try compiling your code with:"
echo "  clang++ -fopenmp -std=c++20 cascade_generator.cpp -shared -o cascade_generator.so"
echo
