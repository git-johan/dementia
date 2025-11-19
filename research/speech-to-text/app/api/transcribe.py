import logging
import tempfile
import time
from datetime import datetime
from typing import Optional
from pathlib import Path

import librosa
import numpy as np
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from pydantic import ValidationError

from app.api.models.requests import AudioMetadata, ProcessingOptions
from app.api.models.responses import SpeechTranscriptionResponse, ProcessorResult
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["transcription"])


@router.post(
    "/transcribe",
    response_model=SpeechTranscriptionResponse,
    summary="Transcribe audio file",
    description="Upload audio file for Norwegian speech-to-text transcription using NB-Whisper"
)
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file to transcribe"),
    metadata: Optional[str] = Form(
        None,
        description="JSON-encoded audio metadata",
        example='{"environment":"quiet_home","source":"ios_voice_memos","device":"iphone_13"}'
    ),
    processing_options: Optional[str] = Form(
        None,
        description="JSON-encoded processing options (currently ignored)",
        example='{"processor":"nb-whisper-large"}'
    ),
    model_size: str = Form(
        "large",
        description="NB-Whisper model size to use",
        example="large",
        regex="^(tiny|base|small|medium|large)$"
    )
):
    """Transcribe audio file to Norwegian text.

    This endpoint accepts audio files from device recording apps and transcribes
    them using the globally loaded Norwegian NB-Whisper models.

    Args:
        file: Audio file (M4A, AAC, MP3, WAV supported)
        metadata: Optional metadata about the recording
        processing_options: Optional processing configuration (currently ignored)
        model_size: NB-Whisper model size to use (tiny/base/small/medium/large)

    Returns:
        Transcription result with Norwegian text, timestamps, and confidence scores
    """
    try:
        logger.info(f"Transcribing audio file: {file.filename}")

        # Validate file
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No audio file provided"
            )

        # Check file size
        if file.size and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE // (1024*1024)}MB"
            )

        # Validate audio format
        allowed_types = ["audio/wav", "audio/mp3", "audio/mpeg", "audio/m4a", "audio/aac", "audio/x-m4a"]
        if file.content_type and file.content_type not in allowed_types:
            logger.warning(f"Potentially unsupported file type: {file.content_type}")

        # Read audio content
        audio_content = await file.read()
        if not audio_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty audio file"
            )

        logger.info(f"Read audio file: {len(audio_content)} bytes")

        # Parse metadata
        try:
            if metadata:
                import json
                metadata_dict = json.loads(metadata)
                audio_metadata = AudioMetadata(**metadata_dict)
            else:
                audio_metadata = AudioMetadata()
        except (json.JSONDecodeError, ValidationError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid metadata JSON: {e}"
            )

        # Validate model size
        from app.main import available_model_sizes
        if model_size not in available_model_sizes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid model size: {model_size}. Available sizes: {', '.join(available_model_sizes)}"
            )

        # Add file information to metadata
        metadata_dict = audio_metadata.dict()
        metadata_dict.update({
            "original_filename": file.filename,
            "content_type": file.content_type,
            "file_size_bytes": len(audio_content),
            "model_size": model_size
        })

        # Process audio directly using selected model
        result = await process_audio_transcription(audio_content, metadata_dict, model_size)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Speech transcription failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


async def process_audio_transcription(audio_content: bytes, metadata: dict, model_size: str) -> SpeechTranscriptionResponse:
    """Process audio content for transcription using the selected NB-Whisper model."""
    start_time = time.time()

    # Get the models from main.py
    from app.main import nb_whisper_models

    if not nb_whisper_models or model_size not in nb_whisper_models:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"NB-Whisper {model_size} model not loaded. Available models: {list(nb_whisper_models.keys())}"
        )

    selected_model = nb_whisper_models[model_size]

    try:
        # Create temporary file for audio processing
        with tempfile.NamedTemporaryFile(suffix=".audio", delete=False) as temp_file:
            temp_file.write(audio_content)
            temp_file.flush()

            logger.info(f"Loading audio file: {temp_file.name}")

            # Load audio using librosa
            audio, sample_rate = librosa.load(temp_file.name, sr=16000)  # Whisper expects 16kHz

            logger.info(f"Audio loaded: {len(audio)} samples at {sample_rate} Hz")
            logger.info("Starting NB-Whisper transcription...")

            # Run transcription using the selected model
            result = selected_model(audio, return_timestamps=True)

            logger.info("NB-Whisper transcription completed")

            # Clean up temp file
            Path(temp_file.name).unlink(missing_ok=True)

        processing_time = int((time.time() - start_time) * 1000)

        # Format result
        text = result.get("text", "")
        chunks = result.get("chunks", [])

        # Convert chunks to segments format
        segments = []
        for chunk in chunks:
            segment = {
                "start": chunk.get("timestamp", [0, 0])[0],
                "end": chunk.get("timestamp", [0, 5])[1],
                "text": chunk.get("text", ""),
                "confidence": 0.8  # Approximate confidence
            }
            segments.append(segment)

        # Calculate confidence score
        confidence_score = sum(s.get("confidence", 0.8) for s in segments) / len(segments) if segments else 0.8

        processor_result = ProcessorResult(
            processor=f"nb-whisper-{model_size}",
            model_version=f"NbAiLab/nb-whisper-{model_size}",
            status="completed",
            confidence_score=confidence_score,
            processing_time_ms=processing_time,
            text=text,
            segments=segments,
            language="no"
        )

        response = SpeechTranscriptionResponse(
            status="completed",
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            processor_result=processor_result,
            metadata=metadata,
            original_filename=metadata.get("original_filename"),
            audio_format=metadata.get("content_type"),
            duration_seconds=len(audio) / sample_rate,
            quality_metrics={
                "audio_size_bytes": len(audio_content),
                "processing_time_ms": processing_time,
                "sample_rate": sample_rate,
                "audio_length_seconds": len(audio) / sample_rate
            }
        )

        return response

    except Exception as e:
        processing_time = int((time.time() - start_time) * 1000)
        logger.error(f"NB-Whisper transcription failed: {e}")

        processor_result = ProcessorResult(
            processor=f"nb-whisper-{model_size}",
            status="failed",
            error=str(e),
            processing_time_ms=processing_time
        )

        response = SpeechTranscriptionResponse(
            status="failed",
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            processor_result=processor_result,
            metadata=metadata,
            original_filename=metadata.get("original_filename")
        )

        return response


@router.get(
    "/models",
    summary="Get available models",
    description="Get information about the loaded NB-Whisper models"
)
async def get_available_models():
    """Get information about all loaded NB-Whisper speech recognition models.

    Returns:
        Information about all available NB-Whisper models, their capabilities, and status
    """
    try:
        from app.main import nb_whisper_models, available_model_sizes, default_model_size

        if not nb_whisper_models:
            return {
                "models": [],
                "status": "Models not loaded yet",
                "message": "NB-Whisper models are still loading. Please wait."
            }

        # Build model information for each loaded model
        models = []
        for model_size in available_model_sizes:
            if model_size in nb_whisper_models:
                model_info = {
                    "name": f"nb-whisper-{model_size}",
                    "size": model_size,
                    "version": "1.0.0",
                    "description": f"Norwegian-optimized Whisper {model_size} model for speech recognition",
                    "supported_formats": ["wav", "mp3", "m4a", "aac", "flac"],
                    "max_duration_seconds": 3600,  # 1 hour
                    "requires_api_key": False,
                    "language": "Norwegian (Bokmål/Nynorsk)",
                    "model_source": f"NbAiLab/nb-whisper-{model_size}",
                    "status": "ready"
                }
                models.append(model_info)

        # Determine current device
        try:
            import torch
            if torch.backends.mps.is_available():
                gpu_status = "Apple M2 Max GPU (MPS)"
            elif torch.cuda.is_available():
                gpu_status = "NVIDIA GPU (CUDA)"
            else:
                gpu_status = "CPU"
        except:
            gpu_status = "Unknown"

        return {
            "models": models,
            "available_model_sizes": available_model_sizes,
            "loaded_models": list(nb_whisper_models.keys()),
            "default_model": default_model_size,
            "status": "ready",
            "processing_mode": "Multi-model direct transcription",
            "gpu_acceleration": gpu_status,
            "usage": "Add model_size parameter to /api/transcribe (tiny/base/small/medium/large)"
        }

    except Exception as e:
        logger.error(f"Failed to get model information: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model information: {e}"
        )