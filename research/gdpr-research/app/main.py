import logging
import os
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.models.responses import HealthResponse
from app.api import speech

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global models storage for multi-model support
nb_whisper_models = {}
default_model_size = "large"
available_model_sizes = ["tiny", "base", "small", "medium", "large"]

# Global Ollama client for Norwegian AI
ollama_client = None
ollama_model = "llama3.1:8b"  # Using Llama 3.1 8B for Norwegian conversational AI


async def load_global_models():
    """Load all NB-Whisper models and initialize Ollama client globally at startup."""
    global nb_whisper_models, ollama_client

    logger.info("Loading Norwegian AI models: NB-Whisper + Ollama...")

    try:
        from transformers import pipeline
        import torch
        import ollama

        # Auto-detect best device: MPS (Apple Silicon) > CUDA (NVIDIA) > CPU
        logger.info(f"Checking device availability...")
        logger.info(f"MPS available: {torch.backends.mps.is_available()}")
        logger.info(f"MPS built: {torch.backends.mps.is_built()}")
        logger.info(f"CUDA available: {torch.cuda.is_available()}")

        if torch.backends.mps.is_available():
            device = "mps"
            device_name = "Apple M2 Max GPU (MPS)"
        elif torch.cuda.is_available():
            device = "cuda"
            device_name = f"CUDA GPU ({torch.cuda.get_device_name()})"
        else:
            device = "cpu"
            device_name = "CPU"

        logger.info(f"Selected device: {device_name} ({device})")

        # Load all 5 NB-Whisper model sizes
        for model_size in available_model_sizes:
            model_name = f"NbAiLab/nb-whisper-{model_size}"
            logger.info(f"Loading {model_size} model: {model_name}")

            try:
                nb_whisper_models[model_size] = pipeline(
                    "automatic-speech-recognition",
                    model=model_name,
                    device=device,
                    torch_dtype="auto"
                )
                logger.info(f"✓ {model_size} model loaded successfully")
            except Exception as e:
                logger.error(f"✗ Failed to load {model_size} model: {e}")
                # Continue loading other models even if one fails
                continue

        loaded_count = len(nb_whisper_models)
        logger.info(f"Loaded {loaded_count}/{len(available_model_sizes)} NB-Whisper models on {device_name}")

        if loaded_count == 0:
            raise Exception("No NB-Whisper models were loaded successfully")

        # Initialize Ollama client for Norwegian conversational AI
        logger.info("Initializing Ollama client for conversational AI...")

        try:
            # Create Ollama client
            ollama_client = ollama.Client()

            # Test connection and model availability
            models_list = ollama_client.list()
            available_models = [model.get('name', model.get('model', '')) for model in models_list.get('models', [])]

            if ollama_model in available_models:
                logger.info(f"✓ Ollama model '{ollama_model}' is available")

                # Test the model with a simple Norwegian question
                test_response = ollama_client.chat(
                    model=ollama_model,
                    messages=[{"role": "user", "content": "Kan du svare på norsk?"}]
                )

                logger.info("✓ Ollama model tested successfully with Norwegian response")
                logger.info(f"Norwegian AI ready with Llama 3.1 8B via Ollama")

            else:
                logger.warning(f"Ollama model '{ollama_model}' not found in: {available_models}")
                logger.info(f"To install the model, run: ollama pull {ollama_model}")
                ollama_client = None

        except Exception as e:
            logger.error(f"✗ Failed to initialize Ollama client: {e}")
            logger.warning("Chat functionality will not be available - ensure Ollama is running")
            ollama_client = None

        # Summary of loaded models
        ollama_status = "ready" if ollama_client is not None else "failed"
        logger.info(f"Norwegian AI models loaded - NB-Whisper: {loaded_count} models, Ollama: {ollama_status}")
        logger.info("Multi-model system ready for speech recognition and chat")

    except Exception as e:
        logger.error(f"Failed to load Norwegian AI models: {e}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("Starting Dementia Care AI Assistant API")

    # Create upload directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info(f"Upload directory ready: {settings.UPLOAD_DIR}")

    # Load all NB-Whisper models globally
    await load_global_models()
    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Dementia Care AI Assistant API")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(speech.router)

# Import and include chat router (for NB-Llama integration)
from app.api import chat
app.include_router(chat.router)


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint redirect."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check API health and service status"
)
async def health_check():
    """Health check endpoint.

    Returns:
        Current API health status
    """
    try:
        # Check processor status
        processor_status = await _check_processor_status()

        # Show status of each loaded model
        services = {}
        global nb_whisper_models, ollama_client

        # NB-Whisper model status
        for model_size in available_model_sizes:
            if model_size in nb_whisper_models:
                services[f"nb_whisper_{model_size}"] = "ready"
            else:
                services[f"nb_whisper_{model_size}"] = "not_loaded"

        # Ollama model status
        services["ollama_chat"] = "ready" if ollama_client is not None else "not_loaded"

        return HealthResponse(
            status="healthy" if processor_status else "degraded",
            timestamp=datetime.utcnow(),
            version=settings.VERSION,
            services=services
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {e}")


async def _check_processor_status() -> bool:
    """Check speech and chat processor health.

    Returns:
        True if at least one NB-Whisper model is loaded
    """
    try:
        global nb_whisper_models
        # Consider system healthy if NB-Whisper is working (NB-Llama is optional)
        return len(nb_whisper_models) > 0

    except Exception as e:
        logger.warning(f"Processor health check failed: {e}")
        return False


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "internal_error"
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )