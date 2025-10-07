#!/usr/bin/env python
"""
Build script for X32 Recorder
Builds the frontend and prepares it for Django to serve
"""
import os
import sys
import subprocess
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DJANGO_DIR = PROJECT_ROOT / "x32recorder"


def run_command(cmd, cwd=None, shell=True):
    """Run a command and stream output"""
    print(f"\n{'='*60}")
    print(f"Running: {cmd}")
    print(f"In: {cwd or os.getcwd()}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(
        cmd,
        cwd=cwd,
        shell=shell,
        text=True
    )
    
    if result.returncode != 0:
        print(f"\n❌ Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    
    print(f"\n✅ Command completed successfully")
    return result


def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║           X32 Recorder - Build Frontend                  ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Check if frontend directory exists
    if not FRONTEND_DIR.exists():
        print(f"❌ Frontend directory not found: {FRONTEND_DIR}")
        sys.exit(1)
    
    # Step 1: Install frontend dependencies
    print("\n📦 Step 1: Installing frontend dependencies...")
    run_command("npm install", cwd=FRONTEND_DIR)
    
    # Step 2: Build frontend
    print("\n🔨 Step 2: Building frontend...")
    run_command("npm run build", cwd=FRONTEND_DIR)
    
    # Step 3: Verify build output
    build_output = DJANGO_DIR / "frontend_build"
    if not build_output.exists():
        print(f"❌ Build output not found: {build_output}")
        sys.exit(1)
    
    index_html = build_output / "index.html"
    if not index_html.exists():
        print(f"❌ index.html not found in build output: {index_html}")
        sys.exit(1)
    
    print(f"\n✅ Build output verified at: {build_output}")
    
    # Step 4: Collect static files (optional)
    print("\n📋 Step 4: Collecting static files...")
    try:
        # Use uv run if available, otherwise try plain python
        collect_cmd = "uv run python manage.py collectstatic --noinput"
        run_command(collect_cmd, cwd=DJANGO_DIR)
    except Exception as e:
        print(f"⚠️  Warning: collectstatic failed: {e}")
        print("This is not critical for development.")
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║                    Build Complete! ✅                     ║
╠═══════════════════════════════════════════════════════════╣
║  The frontend has been built and is ready to be served   ║
║  by Django.                                               ║
║                                                           ║
║  To start the server:                                     ║
║    cd x32recorder                                         ║
║    python manage.py runserver                             ║
║                                                           ║
║  Then visit: http://localhost:8000                        ║
╚═══════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
