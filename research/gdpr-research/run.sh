#!/bin/bash
# Quick start script for GDPR Research Project

set -e

echo "🚀 Starting GDPR Research Server"
echo "================================"

# Check if virtual environment exists
if [[ ! -d "venv" ]]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first"
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "app/main.py" ]]; then
    echo "❌ Error: Run this script from the research/gdpr-research/ directory"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if Ollama is running
echo "🤖 Checking Ollama service..."
if ! curl -s http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "⚠️  Ollama not running or llama3.1:8b not installed"
    echo "   To install: ollama pull llama3.1:8b"
    echo "   To start: ollama serve"
    echo ""
    echo "   Continuing anyway (speech processing will still work)..."
fi

# Create upload directory if it doesn't exist
mkdir -p /tmp/dementia_uploads

# Start the server
echo "🎯 Starting FastAPI server..."
echo "   This will take ~40 seconds to load all NB-Whisper models"
echo "   Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload