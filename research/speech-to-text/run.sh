#!/bin/bash
# Quick start script for Norwegian Speech-to-Text API

set -e

echo "🎙️  Starting Norwegian Speech-to-Text API"
echo "======================================="

# Check if virtual environment exists
if [[ ! -d "venv" ]]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first"
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "app/main.py" ]]; then
    echo "❌ Error: Run this script from the research/speech-to-text/ directory"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check for GPU acceleration
echo "🧠 Checking device acceleration..."
python3 -c "
import torch
if torch.backends.mps.is_available():
    print('✅ Apple Silicon GPU (MPS) available for acceleration')
elif torch.cuda.is_available():
    print('✅ NVIDIA GPU (CUDA) available for acceleration')
else:
    print('ℹ️  Using CPU (consider GPU for faster transcription)')
"

# Create upload directory if it doesn't exist
mkdir -p /tmp/speech_uploads

# Start the server
echo "🎯 Starting Speech-to-Text API server..."
echo "   This will take ~40 seconds to load all 5 NB-Whisper models"
echo "   Available at: http://localhost:8000/api/docs"
echo "   Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload