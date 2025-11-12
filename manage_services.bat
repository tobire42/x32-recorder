@echo off
REM X32 Recorder Service Management Script for Windows
REM This is a wrapper that calls the Python script

python manage_services.py %*
