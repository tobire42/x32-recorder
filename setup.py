"""
Setup script for building the audio_writer C extension module
"""
from setuptools import setup, Extension
import numpy

audio_writer_module = Extension(
    'audio_writer',
    sources=['x32recorder/audio_writer.c'],
    include_dirs=[numpy.get_include()],
    extra_compile_args=[
        '-O3',  # Maximum optimization
        '-march=native',  # Optimize for current CPU (enables SIMD if available)
        '-ffast-math',  # Fast floating point math
    ] if not __import__('sys').platform.startswith('win') else [
        '/O2',  # Maximum optimization for MSVC
        '/fp:fast',  # Fast floating point
    ],
)

setup(
    name='audio_writer',
    version='1.0',
    description='High-performance multi-channel audio writer for 24-bit WAV files',
    ext_modules=[audio_writer_module],
)
