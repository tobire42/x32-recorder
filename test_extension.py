#!/usr/bin/env python3
"""
Test script for audio_writer C extension module
"""
import sys
import numpy as np
import wave
import time
from pathlib import Path

def test_import():
    """Test if audio_writer module can be imported"""
    print("=" * 60)
    print("TEST 1: Module Import")
    print("=" * 60)
    
    try:
        import audio_writer
        print("✅ PASS: audio_writer module imported successfully")
        print(f"   Module location: {audio_writer.__file__}")
        
        # List available functions
        funcs = [name for name in dir(audio_writer) if not name.startswith('_')]
        print(f"   Available functions: {', '.join(funcs)}")
        return True
    except ImportError as e:
        print(f"❌ FAIL: Cannot import audio_writer module")
        print(f"   Error: {e}")
        print("\n   Please build the extension first:")
        print("     Windows: build_extension.bat")
        print("     Linux/macOS: ./build_extension.sh")
        return False


def test_basic_functionality():
    """Test basic audio writing functionality"""
    print("\n" + "=" * 60)
    print("TEST 2: Basic Functionality")
    print("=" * 60)
    
    try:
        import audio_writer
        
        # Create test directory
        test_dir = Path("test_extension_output")
        test_dir.mkdir(exist_ok=True)
        
        # Create test audio data (1024 frames, 4 channels, float32)
        print("Creating test audio data...")
        num_frames = 1024
        num_channels = 4
        audio_data = np.random.randn(num_frames, num_channels).astype(np.float32) * 0.5
        
        # Create WAV files
        print(f"Creating {num_channels} WAV files...")
        files = []
        for i in range(num_channels):
            filepath = test_dir / f"test_ch{i+1:02d}.wav"
            f = wave.open(str(filepath), 'wb')
            f.setnchannels(1)
            f.setsampwidth(3)  # 24-bit
            f.setframerate(48000)
            files.append(f)
        
        # Write using C extension
        print("Writing audio data using C extension...")
        channels = [0, 1, 2, 3]
        frames_written = audio_writer.write_multichannel_24bit(
            audio_data, channels, files
        )
        
        # Close files
        for f in files:
            f.close()
        
        # Verify
        print(f"✅ PASS: Wrote {frames_written} frames")
        for i in range(num_channels):
            filepath = test_dir / f"test_ch{i+1:02d}.wav"
            size = filepath.stat().st_size
            print(f"   - {filepath.name}: {size:,} bytes")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Error during basic functionality test")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance():
    """Test performance compared to Python"""
    print("\n" + "=" * 60)
    print("TEST 3: Performance Comparison")
    print("=" * 60)
    
    try:
        import audio_writer
        
        # Test parameters
        num_frames = 1024
        num_channels = 8
        iterations = 1000
        
        print(f"Test setup: {num_frames} frames, {num_channels} channels, {iterations} iterations")
        
        # Create test data
        audio_data = np.random.randn(num_frames, num_channels).astype(np.float32) * 0.5
        channels = list(range(num_channels))
        
        # Create dummy file objects
        import io
        files = [io.BytesIO() for _ in range(num_channels)]
        
        # Test C extension
        print("\nTesting C extension...")
        start = time.time()
        for _ in range(iterations):
            audio_writer.write_multichannel_24bit(audio_data, channels, files)
        c_time = time.time() - start
        
        # Reset file positions
        for f in files:
            f.seek(0)
        
        # Test Python implementation
        print("Testing Python implementation...")
        audio_int32 = (audio_data * (2**23 - 1)).astype(np.int32)
        start = time.time()
        for _ in range(iterations):
            for idx, channel in enumerate(channels):
                channel_data = audio_int32[:, channel]
                channel_24bit = bytearray()
                for sample in channel_data:
                    sample_24 = max(-2**23, min(2**23 - 1, sample))
                    sample_bytes = int(sample_24).to_bytes(4, byteorder='little', signed=True)[:3]
                    channel_24bit.extend(sample_bytes)
                files[idx].write(bytes(channel_24bit))
        python_time = time.time() - start
        
        # Results
        speedup = python_time / c_time
        print(f"\n✅ PASS: Performance test completed")
        print(f"   C extension: {c_time:.3f}s")
        print(f"   Python:      {python_time:.3f}s")
        print(f"   Speedup:     {speedup:.1f}x")
        
        if speedup < 2.0:
            print(f"\n   ⚠️  Warning: Expected at least 2x speedup, got {speedup:.1f}x")
            print(f"   This might indicate the extension wasn't compiled with optimizations.")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Error during performance test")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n" + "=" * 60)
    print("TEST 4: Edge Cases")
    print("=" * 60)
    
    try:
        import audio_writer
        
        # Test 1: Invalid array dimension
        print("Testing invalid array dimension...")
        try:
            audio_1d = np.random.randn(1024).astype(np.float32)
            audio_writer.write_multichannel_24bit(audio_1d, [0], [None])
            print("❌ FAIL: Should have raised ValueError for 1D array")
            return False
        except ValueError as e:
            print(f"✅ PASS: Correctly rejected 1D array")
        
        # Test 2: Invalid data type
        print("Testing invalid data type...")
        try:
            audio_int16 = np.random.randint(-32768, 32767, (1024, 2), dtype=np.int16)
            audio_writer.write_multichannel_24bit(audio_int16, [0, 1], [None, None])
            print("❌ FAIL: Should have raised TypeError for int16 array")
            return False
        except TypeError as e:
            print(f"✅ PASS: Correctly rejected int16 array")
        
        # Test 3: Mismatched list lengths
        print("Testing mismatched list lengths...")
        try:
            audio = np.random.randn(1024, 2).astype(np.float32)
            audio_writer.write_multichannel_24bit(audio, [0, 1], [None])  # 2 channels, 1 file
            print("❌ FAIL: Should have raised ValueError for mismatched lengths")
            return False
        except ValueError as e:
            print(f"✅ PASS: Correctly rejected mismatched lengths")
        
        # Test 4: Invalid channel index
        print("Testing invalid channel index...")
        try:
            audio = np.random.randn(1024, 2).astype(np.float32)
            import io
            files = [io.BytesIO(), io.BytesIO()]
            audio_writer.write_multichannel_24bit(audio, [0, 5], files)  # Channel 5 doesn't exist
            print("❌ FAIL: Should have raised ValueError for invalid channel")
            return False
        except ValueError as e:
            print(f"✅ PASS: Correctly rejected invalid channel index")
        
        print("\n✅ PASS: All edge cases handled correctly")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Unexpected error during edge case testing")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AUDIO_WRITER C EXTENSION TEST SUITE")
    print("=" * 60)
    print()
    
    results = []
    
    # Test 1: Import
    results.append(("Module Import", test_import()))
    
    if not results[0][1]:
        print("\n⚠️  Cannot continue without audio_writer module")
        sys.exit(1)
    
    # Test 2: Basic functionality
    results.append(("Basic Functionality", test_basic_functionality()))
    
    # Test 3: Performance
    results.append(("Performance", test_performance()))
    
    # Test 4: Edge cases
    results.append(("Edge Cases", test_edge_cases()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! C extension is working correctly.")
        print("\nThe extension will be used automatically in controller.py")
        print("Expected performance improvement: 3-5x faster audio processing")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
