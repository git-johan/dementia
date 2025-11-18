#!/bin/bash
# GDPR Research Project Setup Script

set -e  # Exit on error

echo "🧪 Setting up GDPR Research Project"
echo "=================================="

# Check if we're in the right directory
if [[ ! -f "app/main.py" ]]; then
    echo "❌ Error: Run this script from the research/gdpr-research/ directory"
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

# Install ML packages
pip install torch transformers

# Install audio processing
pip install librosa

# Install file handling
pip install aiofiles python-multipart

# Install database
pip install sqlalchemy

# Install ollama for chat
pip install ollama

# Install additional packages
pip install httpx

echo "✅ All dependencies installed successfully!"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p /tmp/dementia_uploads
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
echo "To run the GDPR research server:"
echo "  1. source venv/bin/activate"
echo "  2. uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "Or use the quick start script:"
echo "  ./run.sh"
echo ""
echo "API will be available at:"
echo "  - Health: http://localhost:8000/health"
echo "  - Capabilities: http://localhost:8000/api/processors/capabilities"
echo "  - Chat: http://localhost:8000/api/chat"
echo "  - Speech: http://localhost:8000/api/process/speech"
echo ""
echo "Note: First startup will download NB-Whisper models (~2GB total)"
echo "      and requires Ollama to be running with llama3.1:8b model"