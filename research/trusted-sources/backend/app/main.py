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

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3002",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3003",
        "https://merry-goose-mostly.ngrok-free.app",  # Frontend ngrok URL
    ],  # Frontend URLs
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