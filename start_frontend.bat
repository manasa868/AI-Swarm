@echo off
title AI Swarm - React Frontend
echo =====================================================================
echo   STARTING AI SWARM: REACT + VITE + TAILWIND DASHBOARD
echo =====================================================================
echo.
cd /d "%~dp0"
set PATH=%~dp0.tools\node;%PATH%

cd frontend
echo Running Vite dev server at http://localhost:5173 ...
call npm run dev
pause
