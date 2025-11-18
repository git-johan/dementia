# GDPR Research Project - Quick Commands

.PHONY: help setup run clean test install-ollama health

help:  ## Show this help
	@echo "GDPR Research Project - Available Commands:"
	@echo "=========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup:  ## Set up the project (install dependencies, create venv)
	@echo "🧪 Setting up GDPR Research Project..."
	@chmod +x setup.sh
	@./setup.sh

run:  ## Start the research server
	@echo "🚀 Starting GDPR Research Server..."
	@chmod +x run.sh
	@./run.sh

clean:  ## Clean up virtual environment
	@echo "🧹 Cleaning up..."
	@rm -rf venv
	@rm -rf __pycache__ app/__pycache__ app/**/__pycache__
	@echo "✅ Cleaned up virtual environment and cache"

test:  ## Test the server (after it's running)
	@echo "🧪 Testing GDPR Research Server..."
	@echo "Health check:"
	@curl -s http://localhost:8000/health || echo "❌ Server not running"
	@echo "\nCapabilities:"
	@curl -s http://localhost:8000/api/processors/capabilities | head -c 200 || echo "❌ Server not running"
	@echo "..."

install-ollama:  ## Install Ollama and required model
	@echo "🤖 Installing Ollama and Norwegian model..."
	@if ! command -v ollama >/dev/null 2>&1; then \
		echo "Installing Ollama..."; \
		curl -fsSL https://ollama.ai/install.sh | sh; \
	else \
		echo "Ollama already installed"; \
	fi
	@echo "Pulling llama3.1:8b model..."
	@ollama pull llama3.1:8b
	@echo "✅ Ollama setup complete"

health:  ## Check server health
	@curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "❌ Server not running"

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