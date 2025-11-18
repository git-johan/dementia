import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""

    # API Configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Dementia Care AI Assistant"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Norwegian-first speech processing for dementia care"

    # Development
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

    # Celery Configuration
    CELERY_BROKER_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    CELERY_RESULT_BACKEND: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

    # Speech Processing
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/tmp/dementia_uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "100")) * 1024 * 1024  # 100MB default

    # NB-Whisper Configuration
    NB_WHISPER_MODEL: str = os.getenv("NB_WHISPER_MODEL", "NbAiLab/nb-whisper-large")

    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()