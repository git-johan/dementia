import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes.chat import chat_router
from routes.trusted_sources import trusted_sources_router

# Load environment variables from .env file
load_dotenv()

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Railway will capture stdout logs
    ]
)

# Get logger for this module
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Trusted Sources - Dementia Care API",
    description="Backend API for Norwegian dementia care conversations using GPT-5",
    version="0.1.0",
)

# Log startup information
logger.info("Starting Trusted Sources API...")
logger.info(f"Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'local')}")
logger.info(f"Port: {os.getenv('PORT', 'not set')}")
logger.info(f"OpenAI API key present: {bool(os.getenv('OPENAI_API_KEY'))}")

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
app.include_router(trusted_sources_router, prefix="/api/v1/trusted-sources", tags=["trusted-sources"])

@app.get("/")
async def root():
    return {
        "message": "Trusted Sources - Dementia Care API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Simple health check endpoint for Railway deployment."""
    import time
    return {
        "status": "healthy",
        "timestamp": int(time.time() * 1000),
        "service": "trusted-sources-backend",
        "version": "0.1.0"
    }

@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to check environment configuration."""
    import time
    return {
        "timestamp": int(time.time() * 1000),
        "environment": {
            "port": os.getenv("PORT", "Not set"),
            "openai_key_present": bool(os.getenv("OPENAI_API_KEY")),
            "railway_environment": os.getenv("RAILWAY_ENVIRONMENT", "Not set"),
            "python_path": os.getenv("PYTHONPATH", "Not set"),
            "node_env": os.getenv("NODE_ENV", "Not set")
        },
        "service_status": {
            "fastapi": "running",
            "openai_service": "not_initialized"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)