@echo off
title Pelican Harvester
cd /d "%~dp0"

:: Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.10+ from python.org
    echo Make sure "Add Python to PATH" is checked during install.
    pause
    exit /b 1
)

:: Auto-install dependencies if missing
python -c "import webview" >nul 2>&1
if errorlevel 1 (
    echo First launch — installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo Dependency install failed. Try manually:
        echo   pip install pywebview requests feedparser
        pause
        exit /b 1
    )
    echo Done.
)

:: Launch
python main.py
