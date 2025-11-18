@echo off
REM Build script for audio_writer C extension (Windows)

echo Building audio_writer C extension...
echo.

REM Check for Python
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: python not found in PATH
    pause
    exit /b 1
)

REM Install build dependencies
echo Installing build dependencies...
python -m pip install setuptools numpy

REM Build the extension
echo.
echo Compiling C extension...
python setup.py build_ext --inplace

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo.
    echo Make sure you have Visual Studio C++ Build Tools installed:
    echo https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo.
    pause
    exit /b 1
)

REM Check if build succeeded
if exist "audio_writer*.pyd" (
    echo.
    echo Build successful!
    echo.
    echo The C extension is now available and will be used automatically.
    echo Expect 3-5x better CPU performance for audio processing.
) else if exist "x32recorder\audio_writer*.pyd" (
    echo.
    echo Build successful!
    echo.
    echo The C extension is now available and will be used automatically.
    echo Expect 3-5x better CPU performance for audio processing.
) else (
    echo.
    echo Build may have failed - extension file not found
)

echo.
pause
