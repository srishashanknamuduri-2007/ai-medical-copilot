@echo off
title AI Medical Copilot — Server
color 0A
echo.
echo  ============================================================
echo   AI Medical Copilot — Full Stack Server
echo   Installing dependencies...
echo  ============================================================
echo.
cd /d "%~dp0"
pip install -r requirements.txt --quiet
echo.
echo  ============================================================
echo   Starting server at http://localhost:8000
echo   Press CTRL+C to stop
echo  ============================================================
echo.
python main.py
pause
