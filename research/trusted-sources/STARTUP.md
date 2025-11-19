# Trusted Sources - Norwegian Dementia Care Chat

## Quick Start

### Backend (FastAPI + GPT-5)
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```
Access: http://localhost:8000

### Frontend (Next.js + ai-chat-ui)
```bash
cd frontend
npm run dev
```
Access: http://localhost:3003

## Requirements
- Backend: Python 3.8+, OpenAI API key in `.env`
- Frontend: Node.js, npm

## Environment Setup
Create `backend/.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## What It Does
Norwegian dementia care conversations powered by GPT-5 through a clean chat interface.