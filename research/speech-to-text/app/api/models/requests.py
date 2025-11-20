from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ProcessingOptions(BaseModel):
    """Options for speech transcription processing."""

    processor: Optional[str] = Field(
        default=None,
        description="Explicit NB-Whisper model size to use (tiny, base, small, medium, large)",
        example="large"
    )

    comparison_mode: bool = Field(
        default=False,
        description="Run multiple model sizes in parallel for comparison"
    )

    processors: Optional[List[str]] = Field(
        default=None,
        description="List of NB-Whisper model sizes to run in comparison mode",
        example=["medium", "large"]
    )


class AudioMetadata(BaseModel):
    """Metadata about the audio recording."""

    environment: Optional[str] = Field(
        default=None,
        description="Recording environment",
        example="quiet_home"
    )

    distance: Optional[str] = Field(
        default=None,
        description="Distance from microphone",
        example="1m"
    )

    context: Optional[str] = Field(
        default=None,
        description="Context of the recording",
        example="doctor_visit"
    )

    source: Optional[str] = Field(
        default=None,
        description="Source recording app",
        example="ios_voice_memos"
    )

    device: Optional[str] = Field(
        default=None,
        description="Recording device model",
        example="iphone_13"
    )

    duration_seconds: Optional[int] = Field(
        default=None,
        description="Duration of recording in seconds"
    )

    additional: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata fields"
    )


class SpeechProcessingRequest(BaseModel):
    """Request model for speech transcription processing."""

    metadata: Optional[AudioMetadata] = Field(
        default_factory=AudioMetadata,
        description="Audio recording metadata"
    )

    processing_options: Optional[ProcessingOptions] = Field(
        default_factory=ProcessingOptions,
        description="Speech transcription processing options"
    )

    # Note: File upload is handled separately via FastAPI's UploadFile