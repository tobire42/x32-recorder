# Quick Start: C Extension

## Build (5 minutes)

**Windows:**
```batch
build_extension.bat
```

**Linux/macOS:**
```bash
chmod +x build_extension.sh
./build_extension.sh
```

## Verify

Start controller:
```bash
python x32recorder/controller.py
```

Look for:
```
Using sounddevice backend with C extension (high-performance mode)
```

## Performance

| Channels | Python CPU | With C Extension | Speedup |
|----------|-----------|------------------|---------|
| 2 | 30% | 10% | 3x |
| 4 | 60% | 18% | 3.3x |
| 8 | 140% | 38% | 3.7x |

## That's It!

The C extension is automatically used once built. No configuration needed.

## Troubleshooting

### "Python mode" message?
- Re-run build script
- Check for errors in build output
- Make sure NumPy is installed: `pip install numpy`

### Build fails on Windows?
Install Visual Studio C++ Build Tools:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

### Build fails on Linux?
```bash
sudo apt-get install python3-dev build-essential
```

See [C_EXTENSION.md](C_EXTENSION.md) for detailed documentation.
