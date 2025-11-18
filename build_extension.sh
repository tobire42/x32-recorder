#!/bin/bash
# Build script for audio_writer C extension

set -e

echo "Building audio_writer C extension..."
echo

# Check for Python and pip
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found"
    exit 1
fi

# Install build dependencies
echo "Installing build dependencies..."
pip install setuptools numpy

# Build the extension
echo
echo "Compiling C extension..."
python setup.py build_ext --inplace

# Check if build succeeded
if [ -f "audio_writer*.so" ] || [ -f "x32recorder/audio_writer*.so" ]; then
    echo
    echo "✅ Build successful!"
    echo
    echo "The C extension is now available and will be used automatically."
    echo "Expect 3-5x better CPU performance for audio processing."
else
    echo
    echo "❌ Build failed"
    exit 1
fi
