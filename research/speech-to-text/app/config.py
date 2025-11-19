import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings for Speech-to-Text API."""

    # API Configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Norwegian Speech-to-Text API"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Norwegian speech recognition using NB-Whisper models"

    # Development
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # File Storage for Audio Uploads
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/tmp/speech_uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "100")) * 1024 * 1024  # 100MB default

    # NB-Whisper Configuration
    DEFAULT_WHISPER_MODEL: str = os.getenv("DEFAULT_WHISPER_MODEL", "large")

    # Available model sizes for NB-Whisper
    AVAILABLE_MODEL_SIZES: list = ["tiny", "base", "small", "medium", "large"]

    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()