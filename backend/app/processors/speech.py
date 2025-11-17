import io
import time
import logging
import tempfile
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List

import librosa
import numpy as np
from transformers import pipeline

from .base import MemoryProcessor, ProcessorResult, ProcessorCapabilities

logger = logging.getLogger(__name__)

# Global model cache to avoid re-downloading for each task
_MODEL_CACHE = {}


def preload_nb_whisper_model(model_name: str = "NbAiLab/nb-whisper-large", device: str = "cpu"):
    """Pre-load NB-Whisper model at worker startup for better performance.

    Args:
        model_name: Model to preload
        device: Device to load model on
    """
    cache_key = f"{model_name}_{device}"
    if cache_key in _MODEL_CACHE:
        logger.info(f"NB-Whisper model already cached: {model_name}")
        return

    logger.info(f"Pre-loading NB-Whisper model: {model_name}")
    try:
        model = pipeline(
            "automatic-speech-recognition",
            model=model_name,
            device=device,
            torch_dtype="auto"
        )
        _MODEL_CACHE[cache_key] = model
        logger.info(f"NB-Whisper model pre-loaded and cached: {model_name}")
    except Exception as e:
        logger.error(f"Failed to pre-load NB-Whisper model: {e}")
        # Don't raise - worker should still start even if model pre-loading fails


class NBWhisperProcessor(MemoryProcessor):
    """Processor for Norwegian-optimized Whisper model (NB-Whisper).

    This processor uses the NB-Whisper model which is specifically
    trained on Norwegian speech data.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize NB-Whisper processor.

        Args:
            config: Configuration including model size, device, etc.
        """
        super().__init__(config)

        # Configuration
        self.model_name = config.get("model_name", "NbAiLab/nb-whisper-large")
        self.device = config.get("device", "cpu")  # TODO: Auto-detect if CUDA available
        self.model_size = config.get("model_size", "large")

        # Model loading (lazy loading)
        self._model = None
        self._model_loaded = False

    async def _load_model(self):
        """Load NB-Whisper model (with global caching)."""
        if self._model_loaded:
            return

        # Check global cache first
        cache_key = f"{self.model_name}_{self.device}"
        if cache_key in _MODEL_CACHE:
            logger.info(f"Using cached NB-Whisper model: {self.model_name}")
            self._model = _MODEL_CACHE[cache_key]
            self._model_loaded = True
            return

        logger.info(f"Loading NB-Whisper model (first time): {self.model_name}")

        try:
            # Load NB-Whisper model using transformers pipeline
            model = pipeline(
                "automatic-speech-recognition",
                model=self.model_name,
                device=self.device,
                torch_dtype="auto"
            )

            # Cache the model globally
            _MODEL_CACHE[cache_key] = model
            self._model = model
            self._model_loaded = True

            logger.info(f"NB-Whisper model loaded and cached: {self.model_name}")

        except Exception as e:
            logger.error(f"Failed to load NB-Whisper model: {e}")
            raise

    def validate_input(self, content: bytes, metadata: Dict[str, Any]) -> bool:
        """Validate audio input for NB-Whisper processing.

        Args:
            content: Audio file bytes
            metadata: Processing metadata

        Returns:
            True if valid audio for speech processing
        """
        # Basic validation - check if content exists and has reasonable size
        if not content:
            return False

        # Check file size (reject files larger than 100MB)
        if len(content) > 100 * 1024 * 1024:
            logger.warning(f"Audio file too large: {len(content)} bytes")
            return False

        # TODO: Add more sophisticated audio format validation
        return True

    async def process(self, content: bytes, metadata: Dict[str, Any]) -> ProcessorResult:
        """Process audio with NB-Whisper.

        Args:
            content: Audio file bytes
            metadata: Processing metadata

        Returns:
            ProcessorResult with transcription
        """
        start_time = time.time()

        try:
            # Load model if needed
            await self._load_model()

            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix=".audio", delete=False) as temp_file:
                temp_file.write(content)
                temp_file.flush()

                # Process with Whisper (placeholder implementation)
                logger.info("Starting NB-Whisper transcription")

                # Run in thread pool to avoid blocking event loop
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self._transcribe_sync,
                    temp_file.name
                )

                # Clean up temp file
                Path(temp_file.name).unlink(missing_ok=True)

            processing_time = int((time.time() - start_time) * 1000)

            return ProcessorResult(
                processor=f"nb-whisper-{self.model_size}",
                status="completed",
                text=result.get("text", ""),
                confidence_score=self._calculate_confidence(result),
                processing_time_ms=processing_time,
                segments=result.get("segments", []),
                language=result.get("language", "no"),
                model_version=self.model_name
            )

        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            logger.error(f"NB-Whisper processing failed: {e}")

            return ProcessorResult(
                processor=f"nb-whisper-{self.model_size}",
                status="failed",
                error=str(e),
                processing_time_ms=processing_time
            )

    def _transcribe_sync(self, audio_path: str) -> Dict[str, Any]:
        """Synchronous transcription (runs in thread pool).

        Args:
            audio_path: Path to audio file

        Returns:
            Transcription result dict
        """
        try:
            logger.info(f"Loading audio file: {audio_path}")

            # Load audio using librosa (compatible with transformers pipeline)
            audio, sample_rate = librosa.load(audio_path, sr=16000)  # Whisper expects 16kHz

            logger.info(f"Audio loaded: {len(audio)} samples at {sample_rate} Hz")
            logger.info("Starting NB-Whisper transcription...")

            # Run transcription
            result = self._model(audio, return_timestamps=True)

            logger.info("NB-Whisper transcription completed")

            # Format result to match our expected structure
            text = result.get("text", "")
            chunks = result.get("chunks", [])

            # Convert chunks to segments format
            segments = []
            for chunk in chunks:
                segment = {
                    "start": chunk.get("timestamp", [0, 0])[0],
                    "end": chunk.get("timestamp", [0, 5])[1],
                    "text": chunk.get("text", ""),
                    "avg_logprob": -0.1  # Approximation since pipeline doesn't return logprobs
                }
                segments.append(segment)

            return {
                "text": text,
                "segments": segments,
                "language": "no"  # NB-Whisper is Norwegian-specific
            }

        except Exception as e:
            logger.error(f"NB-Whisper transcription failed: {e}")
            import os
            file_size = os.path.getsize(audio_path)

            # Return error indication but keep processing
            return {
                "text": f"[Transcription failed: {str(e)}]",
                "segments": [{
                    "start": 0.0,
                    "end": 5.0,
                    "text": f"[Error processing {os.path.basename(audio_path)} - {file_size} bytes]",
                    "avg_logprob": -1.0
                }],
                "language": "no"
            }

    def _calculate_confidence(self, result: Dict[str, Any]) -> Optional[float]:
        """Calculate overall confidence score from segments.

        Args:
            result: Whisper transcription result

        Returns:
            Average confidence score or None
        """
        segments = result.get("segments", [])
        if not segments:
            return None

        # Average confidence scores from all segments
        confidences = []
        for segment in segments:
            if "avg_logprob" in segment:
                # Convert log probability to approximate confidence
                confidence = max(0.0, min(1.0, segment["avg_logprob"] + 1.0))
                confidences.append(confidence)

        return sum(confidences) / len(confidences) if confidences else None

    def get_capabilities(self) -> ProcessorCapabilities:
        """Get NB-Whisper processor capabilities.

        Returns:
            ProcessorCapabilities for this processor
        """
        return ProcessorCapabilities(
            name=f"nb-whisper-{self.model_size}",
            version="1.0.0",
            description="Norwegian-optimized Whisper model for speech recognition",
            supported_formats=["wav", "mp3", "m4a", "aac", "flac"],
            max_duration_seconds=3600,  # 1 hour
            requires_api_key=False
        )

    async def health_check(self) -> bool:
        """Check if NB-Whisper processor is healthy.

        Returns:
            True if processor is ready
        """
        try:
            if not self._model_loaded:
                await self._load_model()
            return True
        except Exception as e:
            logger.error(f"NB-Whisper health check failed: {e}")
            return False


class OpenAIWhisperProcessor(MemoryProcessor):
    """Processor for OpenAI Whisper API.

    This processor uses OpenAI's Whisper API for comparison testing.
    Only used for research comparison, not production due to privacy concerns.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize OpenAI Whisper processor.

        Args:
            config: Configuration including API key
        """
        super().__init__(config)

        self.api_key = config.get("api_key")
        if not self.api_key:
            logger.warning("No OpenAI API key provided. OpenAI Whisper will not work.")

        self.model = config.get("model", "whisper-1")

    def validate_input(self, content: bytes, metadata: Dict[str, Any]) -> bool:
        """Validate audio input for OpenAI Whisper.

        Args:
            content: Audio file bytes
            metadata: Processing metadata

        Returns:
            True if valid audio and API key available
        """
        if not self.api_key:
            return False

        # Basic validation
        if not content:
            return False

        # OpenAI has 25MB file size limit
        if len(content) > 25 * 1024 * 1024:
            logger.warning(f"Audio file too large for OpenAI: {len(content)} bytes")
            return False

        return True

    async def process(self, content: bytes, metadata: Dict[str, Any]) -> ProcessorResult:
        """Process audio with OpenAI Whisper API.

        Args:
            content: Audio file bytes
            metadata: Processing metadata

        Returns:
            ProcessorResult with transcription
        """
        start_time = time.time()

        try:
            # TODO: Implement actual OpenAI API call
            # This is a placeholder for now

            # Simulate processing time
            await asyncio.sleep(2)

            processing_time = int((time.time() - start_time) * 1000)

            return ProcessorResult(
                processor="openai-whisper",
                status="completed",
                text="[OpenAI Whisper placeholder - not implemented yet]",
                confidence_score=0.95,
                processing_time_ms=processing_time,
                language="no",
                model_version=self.model
            )

        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            logger.error(f"OpenAI Whisper processing failed: {e}")

            return ProcessorResult(
                processor="openai-whisper",
                status="failed",
                error=str(e),
                processing_time_ms=processing_time
            )

    def get_capabilities(self) -> ProcessorCapabilities:
        """Get OpenAI Whisper processor capabilities.

        Returns:
            ProcessorCapabilities for this processor
        """
        return ProcessorCapabilities(
            name="openai-whisper",
            version="1.0.0",
            description="OpenAI Whisper API for speech recognition (research comparison only)",
            supported_formats=["wav", "mp3", "m4a", "aac", "flac", "webm"],
            max_duration_seconds=1800,  # 30 minutes (OpenAI limit)
            requires_api_key=True
        )

    async def health_check(self) -> bool:
        """Check if OpenAI Whisper processor is healthy.

        Returns:
            True if API key is available
        """
        return bool(self.api_key)