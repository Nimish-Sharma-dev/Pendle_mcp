#!/bin/bash

# --- 1. Check Python ---
echo "Checking Python version..."
python3 --version || python --version

# --- 2. Create Virtual Environment ---
echo "Creating virtual environment..."
python3 -m venv .venv || python -m venv .venv

# --- 3. Activate Virtual Environment ---
echo "Activating virtual environment..."
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

# --- 4. Upgrade pip ---
echo "Upgrading pip..."
pip install --upgrade pip

# --- 5. Install Dependencies ---
echo "Installing dependencies..."
pip install -r requirements.txt

# --- 6. Start the Pendle MCP Server ---
echo "Starting Pendle MCP Server on http://127.0.0.1:8000 ..."
uvicorn server:app --reload --port 8000