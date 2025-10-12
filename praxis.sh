#!/bin/bash
# PRAXIS launcher script
# Launches the Streamlit UI from anywhere

# Get the directory where this script lives
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to project directory
cd "$SCRIPT_DIR" || exit 1

# Activate virtual environment and launch Streamlit
echo "🏃 Launching PRAXIS..."
source venv/bin/activate && streamlit run src/app.py
