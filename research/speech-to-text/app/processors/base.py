from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProcessorCapabilities:
    """Metadata about processor capabilities."""

    name: str
    version: str
    description: str
    supported_formats: list[str]
    max_duration_seconds: Optional[int] = None
    requires_api_key: bool = False


@dataclass
class ProcessorResult:
    """Result from processing audio through a processor."""

    processor: str
    status: str  # "completed", "failed", "processing"
    text: Optional[str] = None
    confidence_score: Optional[float] = None
    processing_time_ms: Optional[int] = None
    segments: Optional[list] = None
    language: Optional[str] = None
    model_version: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MemoryProcessor(ABC):
    """Base interface for speech transcription processors.

    This follows our processor plugin pattern where different NB-Whisper
    model sizes can implement this interface.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize processor with configuration."""
        self.config = config or {}

    @abstractmethod
    async def process(self, content: bytes, metadata: Dict[str, Any]) -> ProcessorResult:
        """Process input content and return structured result.

        Args:
            content: Raw audio file bytes for speech processor
            metadata: Additional context and processing options

        Returns:
            ProcessorResult with structured transcription output
        """
        pass

    @abstractmethod
    def validate_input(self, content: bytes, metadata: Dict[str, Any]) -> bool:
        """Validate that input is compatible with this processor.

        Args:
            content: Input audio data to validate
            metadata: Additional context for validation

        Returns:
            True if input is valid for this processor
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> ProcessorCapabilities:
        """Return processor metadata and capabilities.

        Returns:
            ProcessorCapabilities describing what this processor can do
        """
        pass

    def estimate_processing_time(self, content: bytes, metadata: Dict[str, Any]) -> Optional[int]:
        """Estimate processing time in milliseconds.

        Args:
            content: Input audio data
            metadata: Processing context

        Returns:
            Estimated processing time in milliseconds, or None if unknown
        """
        return None

    async def health_check(self) -> bool:
        """Check if processor is healthy and ready.

        Returns:
            True if processor is ready to process requests
        """
        return True