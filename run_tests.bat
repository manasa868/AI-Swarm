@echo off
title AI Swarm - Test Suite Runner
echo =====================================================================
echo   RUNNING AI SWARM PYTEST TEST SUITE
echo =====================================================================
echo.
cd /d "%~dp0"
if exist backend\venv\Scripts\python.exe (
    backend\venv\Scripts\python.exe -m pytest backend/tests -v
) else (
    python -m pytest backend/tests -v
)
echo.
echo =====================================================================
pause
