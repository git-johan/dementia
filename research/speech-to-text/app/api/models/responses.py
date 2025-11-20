from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class JobStatus(str, Enum):
    """Job processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessorResult(BaseModel):
    """Result from NB-Whisper speech transcription."""

    processor: str = Field(..., description="NB-Whisper model name", example="nb-whisper-large")
    model_version: Optional[str] = Field(None, description="Model version used")
    status: JobStatus = Field(..., description="Processing status")
    confidence_score: Optional[float] = Field(None, description="Overall confidence score", ge=0, le=1)
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")

    # Main result
    text: Optional[str] = Field(None, description="Transcribed Norwegian text")

    # Detailed result (if available)
    segments: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Detailed segments with timestamps and confidence scores"
    )

    language: Optional[str] = Field(None, description="Detected language", example="no")

    # Error information
    error: Optional[str] = Field(None, description="Error message if transcription failed")


class SpeechProcessingJobResponse(BaseModel):
    """Response when submitting a speech transcription job."""

    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    created_at: datetime = Field(..., description="Job creation timestamp")
    estimated_completion: Optional[datetime] = Field(
        None,
        description="Estimated completion time"
    )

    links: Dict[str, str] = Field(
        default_factory=dict,
        description="Links to related endpoints",
        example={
            "status": "/api/jobs/{job_id}/status",
            "result": "/api/jobs/{job_id}/result"
        }
    )


class JobStatusResponse(BaseModel):
    """Response for transcription job status queries."""

    job_id: str = Field(..., description="Job identifier")
    status: JobStatus = Field(..., description="Current status")
    created_at: datetime = Field(..., description="Job creation time")
    started_at: Optional[datetime] = Field(None, description="Processing start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")

    progress: Optional[float] = Field(
        None,
        description="Progress percentage",
        ge=0,
        le=100
    )

    estimated_completion: Optional[datetime] = Field(
        None,
        description="Estimated completion time"
    )

    processors: List[str] = Field(
        default_factory=list,
        description="NB-Whisper models being used for this job"
    )

    error: Optional[str] = Field(None, description="Error message if failed")


class SpeechProcessingResultResponse(BaseModel):
    """Complete result response for speech transcription processing."""

    job_id: str = Field(..., description="Job identifier")
    status: JobStatus = Field(..., description="Final job status")
    created_at: datetime = Field(..., description="Job creation time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")

    # Processing results
    processors_used: List[ProcessorResult] = Field(
        default_factory=list,
        description="Results from all NB-Whisper models"
    )

    # Original request metadata
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Original audio metadata"
    )

    # File information
    original_filename: Optional[str] = Field(None, description="Original audio filename")
    audio_format: Optional[str] = Field(None, description="Detected audio format")
    duration_seconds: Optional[float] = Field(None, description="Audio duration")

    # Quality metrics
    quality_metrics: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Audio quality assessment"
    )


class SpeechTranscriptionResponse(BaseModel):
    """Direct speech transcription response for simplified processing."""

    status: JobStatus = Field(..., description="Processing status")
    created_at: datetime = Field(..., description="Processing start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Processing completion timestamp")

    # Processing result
    processor_result: ProcessorResult = Field(..., description="Transcription result")

    # Original request metadata
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Original audio metadata"
    )

    # File information
    original_filename: Optional[str] = Field(None, description="Original audio filename")
    audio_format: Optional[str] = Field(None, description="Audio format")
    duration_seconds: Optional[float] = Field(None, description="Audio duration in seconds")

    # Quality metrics
    quality_metrics: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Audio processing metrics"
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., example="healthy")
    timestamp: datetime = Field(..., description="Response timestamp")
    version: str = Field(..., description="API version")
    services: Dict[str, str] = Field(
        default_factory=dict,
        description="Status of NB-Whisper models",
        example={"nb_whisper_large": "ready", "nb_whisper_medium": "ready"}
    )