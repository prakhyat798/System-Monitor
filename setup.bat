@echo off
title System Monitor Setup & Builder
echo ========================================================
echo         System Monitor Setup & Exe Builder
echo ========================================================
echo.

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH!
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo [2/3] Installing/updating required dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing dependencies.
    pause
    exit /b 1
)

echo.
echo [3/3] Building standalone executable (System Monitor.exe)...
pyinstaller --noconfirm --onedir --windowed --name "System Monitor" --add-data "LibreHardwareMonitor;LibreHardwareMonitor" status_monitor.py

if %errorlevel% eq 0 (
    echo.
    echo ========================================================
    echo SUCCESS! Standalone executable built at:
    echo %~dp0dist\System Monitor\System Monitor.exe
    echo ========================================================
) else (
    echo Build failed. Check output errors above.
)

pause
