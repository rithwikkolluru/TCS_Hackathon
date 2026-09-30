#!/bin/bash
# Move to the project root directory regardless of where this script is called from
cd "$(dirname "$0")"

echo "=================================================="
echo " Starting Intelligent Branch Optimizer Backend"
echo " Directory: $(pwd)"
echo " Docs:      http://localhost:8000/docs"
echo " Health:    http://localhost:8000/health"
echo "=================================================="

# Use miniconda Python where all ML, FastAPI, and Uvicorn packages are installed
if [ -f "/Users/krithvik/miniconda3/bin/python3" ]; then
    /Users/krithvik/miniconda3/bin/python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
else
    python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
fi
