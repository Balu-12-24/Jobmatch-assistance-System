@echo off
echo Starting JobMatch AI Backend Server...
echo.
cd /d "%~dp0"
call venv\Scripts\activate
python start.py
