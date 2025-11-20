# Project: Trusted Sources

## Core Question
How do we make sure the AI-assistant references only trusted sources when patients ask questions that require safe and trusted sources?

## Project Structure

This project consists of two services:
- **Backend**: FastAPI application providing chat API with OpenAI integration
- **Frontend**: Next.js application with chat interface for dementia care

## Quick Start

### Local Development
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Add your OpenAI API key
uvicorn app.main:app --reload

# Frontend (in new terminal)
cd frontend
npm install
npm run dev
```

### Railway Deployment
This project is configured for Railway deployment with automatic branch deployments.

1. **Test Branch**: `research/railway-setup-20241120` contains Railway-ready configuration
2. **Setup Guide**: See [RAILWAY-SETUP.md](RAILWAY-SETUP.md) for detailed deployment instructions
3. **Environment Variables**: See `.env.example` files for required variables

## Key Features
- Norwegian-focused dementia care conversations
- Integration with trusted health sources
- Environment-based configuration for local/Railway deployment
- CORS support for cross-origin requests
- Health check endpoints for monitoring

## Metadata
* Status: In progress - Railway deployment ready
* Linear project: https://linear.app/johanjosok/project/rag-research-trusted-sources-af2d8de41fb3/overview
* Railway branch: `research/railway-setup-20241120`
