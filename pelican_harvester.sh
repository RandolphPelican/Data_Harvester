#!/usr/bin/env bash
# Pelican Harvester — macOS / Linux launcher
set -e
cd "$(dirname "$0")"

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found. Install Python 3.10+."
    exit 1
fi

# Auto-install deps
python3 -c "import webview" 2>/dev/null || {
    echo "First launch — installing dependencies..."
    pip3 install -r requirements.txt
}

python3 main.py "$@"
#..
