import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routes.chat import chat_router

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Trusted Sources - Dementia Care API",
    description="Backend API for Norwegian dementia care conversations using GPT-5",
    version="0.1.0",
)

# Get environment-specific CORS origins
def get_cors_origins():
    """Get allowed CORS origins based on environment"""
    # Local development origins
    local_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
    ]

    # Production/Railway origins
    production_origins = []

    # Add Railway frontend URL if available
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        production_origins.append(frontend_url)

    # Add ngrok URL if available (for development)
    ngrok_url = os.getenv("NGROK_URL")
    if ngrok_url:
        local_origins.append(ngrok_url)

    # For Railway deployments, use allow_origin_regex for .railway.app domains
    # This will be handled separately below

    return local_origins + production_origins

# Configure CORS for frontend communication
cors_origins = get_cors_origins()
cors_regex = None

# For Railway deployments, use regex to allow all .railway.app domains
if os.getenv("RAILWAY_ENVIRONMENT"):
    cors_regex = r"https://.*\.railway\.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=cors_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])

@app.get("/")
async def root():
    return {
        "message": "Trusted Sources - Dementia Care API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)