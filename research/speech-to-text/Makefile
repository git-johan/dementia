# Norwegian Speech-to-Text API - Quick Commands

.PHONY: help setup run clean test health transcribe

help:  ## Show this help
	@echo "Norwegian Speech-to-Text API - Available Commands:"
	@echo "================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup:  ## Set up the project (install dependencies, create venv)
	@echo "🎙️  Setting up Norwegian Speech-to-Text API..."
	@chmod +x setup.sh
	@./setup.sh

run:  ## Start the speech-to-text API server
	@echo "🚀 Starting Speech-to-Text API Server..."
	@chmod +x run.sh
	@./run.sh

clean:  ## Clean up virtual environment
	@echo "🧹 Cleaning up..."
	@rm -rf venv
	@rm -rf __pycache__ app/__pycache__ app/**/__pycache__
	@echo "✅ Cleaned up virtual environment and cache"

test:  ## Test the server (after it's running)
	@echo "🧪 Testing Speech-to-Text API Server..."
	@echo "Health check:"
	@curl -s http://localhost:8000/health || echo "❌ Server not running"
	@echo "\nAvailable models:"
	@curl -s http://localhost:8000/api/models | head -c 200 || echo "❌ Server not running"
	@echo "..."

health:  ## Check server health and model status
	@curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "❌ Server not running"

models:  ## List available NB-Whisper models
	@echo "📋 Available NB-Whisper models:"
	@curl -s http://localhost:8000/api/models | python3 -m json.tool 2>/dev/null || echo "❌ Server not running"

transcribe:  ## Test transcription with example audio (requires test file)
	@echo "🎵 Testing transcription..."
	@if [[ -f "test_audio.txt" ]]; then \
		curl -X POST http://localhost:8000/api/transcribe \
			-H "Content-Type: multipart/form-data" \
			-F "file=@test_audio.txt" \
			-F "model_size=medium" | python3 -m json.tool; \
	else \
		echo "❌ test_audio.txt not found. Place an audio file for testing."; \
	fi

# Quick development commands
dev: setup run  ## Setup and run in one command

# Installation verification
verify:  ## Verify installation works
	@echo "🔍 Verifying installation..."
	@if [[ -d "venv" ]]; then \
		echo "✅ Virtual environment exists"; \
	else \
		echo "❌ Virtual environment missing - run 'make setup'"; \
	fi
	@source venv/bin/activate && python3 -c "from app.main import app; print('✅ Imports work')" 2>/dev/null || echo "❌ Import test failed"

# GPU check
gpu:  ## Check GPU acceleration availability
	@echo "🧠 Checking GPU acceleration..."
	@source venv/bin/activate && python3 -c "\
	import torch; \
	print('✅ Apple Silicon (MPS):', torch.backends.mps.is_available()); \
	print('✅ NVIDIA CUDA:', torch.cuda.is_available()); \
	print('Current device:', 'MPS' if torch.backends.mps.is_available() else 'CUDA' if torch.cuda.is_available() else 'CPU')"