@echo off
title AI Swarm - Platform Launcher
echo =====================================================================
echo   AI SWARM: FROM INDIVIDUAL TO INTELLIGENT TEAMS
echo   Launching Backend and Frontend concurrently...
echo =====================================================================
echo.
cd /d "%~dp0"
set PATH=%~dp0.tools\node;%PATH%

start "AI Swarm Backend" cmd /k "start_backend.bat"
timeout /t 3 /nobreak >nul
start "AI Swarm Frontend" cmd /k "start_frontend.bat"

echo.
echo Both services are starting in separate windows.
echo - Frontend Dashboard: http://localhost:5173
echo - Backend API Docs  : http://127.0.0.1:8000/docs
echo.
pause
