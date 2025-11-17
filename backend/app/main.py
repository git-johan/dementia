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

# Global NB-Llama model storage
nb_llama_model = None
nb_llama_tokenizer = None


async def load_global_models():
    """Load all NB-Whisper models and NB-Llama model globally at startup."""
    global nb_whisper_models, nb_llama_model, nb_llama_tokenizer

    logger.info("Loading Norwegian AI models: NB-Whisper + NB-Llama...")

    try:
        from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
        import torch

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

        # Load all 5 model sizes
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

        # Load NB-Llama model using same device
        logger.info("Loading NB-Llama model for conversational AI...")

        try:
            model_name = "NbAiLab/nb-llama-3.1-8B-Instruct"
            logger.info(f"Loading NB-Llama tokenizer: {model_name}")

            nb_llama_tokenizer = AutoTokenizer.from_pretrained(model_name)

            logger.info(f"Loading NB-Llama model: {model_name} on {device}")
            nb_llama_model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map=device,
                torch_dtype=torch.float16
            )

            logger.info(f"✓ NB-Llama model loaded successfully on {device_name}")

        except Exception as e:
            logger.error(f"✗ Failed to load NB-Llama model: {e}")
            logger.warning("Chat functionality will not be available")

        # Summary of loaded models
        nb_llama_status = "ready" if nb_llama_model is not None else "failed"
        logger.info(f"Norwegian AI models loaded - NB-Whisper: {loaded_count} models, NB-Llama: {nb_llama_status}")
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
        global nb_whisper_models, nb_llama_model

        # NB-Whisper model status
        for model_size in available_model_sizes:
            if model_size in nb_whisper_models:
                services[f"nb_whisper_{model_size}"] = "ready"
            else:
                services[f"nb_whisper_{model_size}"] = "not_loaded"

        # NB-Llama model status
        services["nb_llama_8b"] = "ready" if nb_llama_model is not None else "not_loaded"

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
    """Check speech processor health.

    Returns:
        True if at least one NB-Whisper model is loaded
    """
    try:
        global nb_whisper_models
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