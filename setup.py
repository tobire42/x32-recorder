"""
Setup script for building the audio_writer C extension module

This setup.py is ONLY for the C extension.
Use pyproject.toml for main project dependencies.
"""
from setuptools import setup, Extension
import numpy

audio_writer_module = Extension(
    'audio_writer',
    sources=['audio_writer_ext/audio_writer.c'],
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
