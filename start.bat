@echo off
echo ========================================
echo   StoryLens - AI Script Analysis
echo ========================================
echo.
echo Starting FastAPI backend on port 8000...
start "StoryLens API" cmd /k "cd /d %~dp0 && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo Starting Streamlit frontend on port 8501...
start "StoryLens UI" cmd /k "cd /d %~dp0 && streamlit run streamlit/app.py --server.port 8501"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   Both servers are running!
echo   API:      http://localhost:8000
echo   Frontend: http://localhost:8501
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.
start http://localhost:8501
