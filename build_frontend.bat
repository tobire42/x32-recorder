@echo off
REM Build script for X32 Recorder on Windows
REM Builds the frontend and prepares it for Django to serve

echo.
echo ===============================================================
echo            X32 Recorder - Build Frontend
echo ===============================================================
echo.

cd /d "%~dp0"

REM Check if frontend directory exists
if not exist "frontend" (
    echo [ERROR] Frontend directory not found!
    exit /b 1
)

REM Step 1: Install frontend dependencies
echo.
echo [Step 1/3] Installing frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    exit /b %errorlevel%
)

REM Step 2: Build frontend
echo.
echo [Step 2/3] Building frontend...
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build frontend
    exit /b %errorlevel%
)

cd ..

REM Step 3: Verify build output
echo.
echo [Step 3/3] Verifying build output...
if not exist "x32recorder\frontend_build\index.html" (
    echo [ERROR] Build output not found!
    exit /b 1
)

echo.
echo ===============================================================
echo                    Build Complete!
echo ===============================================================
echo.
echo The frontend has been built and is ready to be served by Django.
echo.
echo To start the server:
echo   cd x32recorder
echo   python manage.py runserver
echo.
echo Then visit: http://localhost:8000
echo.
echo ===============================================================
