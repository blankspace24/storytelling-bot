#!/bin/bash
echo "========================================"
echo "  StoryLens - AI Script Analysis"
echo "========================================"
echo ""

# Start FastAPI backend
echo "Starting FastAPI backend on port 8000..."
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

sleep 3

# Start Streamlit frontend
echo "Starting Streamlit frontend on port 8501..."
streamlit run streamlit/app.py --server.port 8501 &
UI_PID=$!

echo ""
echo "========================================"
echo "  Both servers are running!"
echo "  API:      http://localhost:8000"
echo "  Frontend: http://localhost:8501"
echo "  API Docs: http://localhost:8000/docs"
echo "========================================"
echo ""

# Wait for both processes
trap "kill $API_PID $UI_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
