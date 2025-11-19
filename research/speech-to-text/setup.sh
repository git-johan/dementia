#!/bin/bash
# Norwegian Speech-to-Text API Setup Script

set -e  # Exit on error

echo "🎙️  Setting up Norwegian Speech-to-Text API"
echo "=========================================="

# Check if we're in the right directory
if [[ ! -f "app/main.py" ]]; then
    echo "❌ Error: Run this script from the research/speech-to-text/ directory"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
if [[ -d "venv" ]]; then
    echo "   Virtual environment already exists, removing old one..."
    rm -rf venv
fi

python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
echo "   This may take a few minutes for ML packages..."

# Install core packages first
pip install fastapi uvicorn pydantic pydantic-settings python-dotenv

# Install ML packages for NB-Whisper
echo "🧠 Installing Norwegian AI models (transformers, torch)..."
pip install torch transformers

# Install audio processing
echo "🎵 Installing audio processing libraries..."
pip install librosa

# Install file handling for audio uploads
echo "📁 Installing file handling libraries..."
pip install aiofiles python-multipart

echo "✅ All dependencies installed successfully!"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p /tmp/speech_uploads
echo "✅ Upload directory created"

# Test import
echo "🧪 Testing imports..."
if python3 -c "from app.main import app; print('✅ All imports successful!')" 2>/dev/null; then
    echo "✅ Import test passed"
else
    echo "❌ Import test failed - check the output above"
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To run the Speech-to-Text API server:"
echo "  1. source venv/bin/activate"
echo "  2. uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "Or use the quick start script:"
echo "  ./run.sh"
echo ""
echo "API will be available at:"
echo "  - Health: http://localhost:8000/health"
echo "  - Models: http://localhost:8000/api/models"
echo "  - Transcribe: http://localhost:8000/api/transcribe"
echo "  - API Docs: http://localhost:8000/api/docs"
echo ""
echo "Note: First startup will download NB-Whisper models (~2GB total)"
echo "      This includes 5 model sizes: tiny, base, small, medium, large"
echo ""
echo "Supported audio formats: WAV, MP3, M4A, AAC, FLAC"