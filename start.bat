@echo off
REM SLOOS Analyzer Startup Script for Windows

echo Starting SLOOS Interactive Analyzer...

REM Install dependencies using UV
echo Installing dependencies with UV...
uv sync

REM Run the application
echo Starting server on http://0.0.0.0:7251
uv run python app.py
