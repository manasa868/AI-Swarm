@echo off
title AI Swarm - FastAPI Backend
echo =====================================================================
echo   STARTING AI SWARM: FASTAPI BACKEND & ORCHESTRATION ENGINE
echo =====================================================================
echo.
cd /d "%~dp0"
if exist backend\venv\Scripts\python.exe (
    set PYTHON=backend\venv\Scripts\python.exe
) else (
    set PYTHON=python
)

echo Using Python: %PYTHON%
echo Swagger API Documentation: http://127.0.0.1:8000/docs
echo Web Dashboard (Unified)  : http://127.0.0.1:8000
echo.
%PYTHON% backend\run.py
pause
