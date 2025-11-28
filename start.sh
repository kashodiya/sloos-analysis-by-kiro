#!/bin/bash
# SLOOS Analyzer Startup Script

echo "🚀 Starting SLOOS Interactive Analyzer..."

# Install dependencies using UV
echo "📦 Installing dependencies with UV..."
uv sync

# Run the application
echo "🌐 Starting server on http://0.0.0.0:7251"
uv run python app.py
