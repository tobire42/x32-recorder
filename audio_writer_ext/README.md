# Audio Writer C Extension

This directory contains the C extension module for high-performance audio processing.

## Contents

- **`audio_writer.c`** - C source code for the extension module
- This extension is built separately from the main project

## Building

From the project root directory:

**Windows:**
```batch
build_extension.bat
```

**Linux/macOS:**
```bash
./build_extension.sh
```

Or manually:
```bash
python setup.py build_ext --inplace
```

## Output

The build creates a platform-specific binary in the project root:
- **Linux**: `audio_writer.cpython-*.so`
- **macOS**: `audio_writer.cpython-*.so`
- **Windows**: `audio_writer.cp*.pyd`

This binary can then be imported from anywhere in the project:
```python
import audio_writer
```

## Why Separate Directory?

The C extension is kept in its own directory to:
1. Avoid conflicts with the main `pyproject.toml` build system
2. Keep C code organized separately from Python code
3. Make it clear this is an optional performance enhancement
4. Allow independent building and testing

## Documentation

See [C_EXTENSION.md](../C_EXTENSION.md) for complete documentation.
