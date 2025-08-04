#!/bin/bash

echo "Kill all processes on port 8000"
kill $(lsof -t -i:8000)

echo "Activating virtual environment..."
source ~/Documents/environments/milo-env/bin/activate || { echo "Failed to activate venv"; exit 1; }

echo "Changing to app directory..."
cd ~/Documents/projects/buddy-milo/apis || { echo "Failed to cd to project"; exit 1; }

echo "Starting Uvicorn server and blocking sleep yo..."
exec systemd-inhibit --why="Running Uvicorn server" uvicorn main:app --host 0.0.0.0 --port 8000
