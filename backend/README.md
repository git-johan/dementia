# Dementia Care AI Assistant - Backend

Norwegian-first speech processing backend for dementia care AI assistant.

## Overview

This FastAPI backend provides:
- **Async speech processing** with Norwegian-optimized models (NB-Whisper)
- **Research comparison** with OpenAI Whisper for model evaluation
- **Processor plugin architecture** for future input types (PDF, photos, text)
- **Job-based processing** with real-time status tracking

## Architecture

### Core Components

- **FastAPI** - Async web framework for API endpoints
- **Celery + Redis** - Background job processing for speech recognition
- **Processor Plugin System** - Extensible architecture for different input types
- **NB-Whisper** - Norwegian-trained speech recognition models

### API Endpoints

```
POST /api/process/speech      # Submit audio for processing
GET  /api/jobs/{id}/status    # Check processing status
GET  /api/jobs/{id}/result    # Get transcription results
GET  /api/processors/capabilities  # List available processors
GET  /health                  # Health check
```

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start Redis

```bash
docker-compose up redis -d
```

### 3. Start Celery Worker

```bash
celery -A app.workers.tasks worker --loglevel=info
```

### 4. Start FastAPI Server

```bash
uvicorn app.main:app --reload
```

### 5. Test API

```bash
# Check health
curl http://localhost:8000/health

# Check capabilities
curl http://localhost:8000/api/processors/capabilities

# Upload audio (record with Voice Memos first)
curl -X POST http://localhost:8000/api/process/speech \
  -F "file=@voice_memo.m4a" \
  -F 'metadata={"environment":"quiet_home","source":"ios_voice_memos"}'
```

## Configuration

Create `.env` file:

```bash
# API Configuration
DEBUG=true

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# OpenAI (optional - for comparison testing)
OPENAI_API_KEY=your_openai_api_key_here

# File Storage
UPLOAD_DIR=/tmp/dementia_uploads
MAX_FILE_SIZE=100  # MB

# NB-Whisper Model
NB_WHISPER_MODEL=NbAiLab/nb-whisper-large
```

## Development

### Project Structure

```
backend/
├── app/
│   ├── api/                   # API endpoints
│   │   ├── speech.py          # Speech processing endpoints
│   │   ├── jobs.py            # Job status endpoints
│   │   └── models/            # Pydantic models
│   ├── processors/            # Processor plugin system
│   │   ├── base.py            # BaseProcessor interface
│   │   ├── registry.py        # Processor registry
│   │   └── speech.py          # Speech processors
│   ├── workers/               # Background processing
│   │   └── tasks.py           # Celery tasks
│   ├── config.py              # Configuration
│   └── main.py                # FastAPI application
├── tests/                     # Test files
├── requirements.txt           # Dependencies
├── docker-compose.yml         # Redis service
└── README.md                  # This file
```

### Adding New Processors

```python
# 1. Create processor class
class NewProcessor(MemoryProcessor):
    async def process(self, content: bytes, metadata: dict) -> ProcessorResult:
        # Implementation here
        pass

# 2. Register processor
processor_registry.register_processor(
    name="new-processor",
    processor_class=NewProcessor,
    config={"param": "value"}
)
```

## Testing

### Manual Testing Protocol

#### 1. Record Audio with Device
```bash
# iOS: Use Voice Memos app → Share → Save to Files
# Android: Use Recorder app → Export → Choose location
```

#### 2. Test Upload and Processing
```bash
# Submit processing job
curl -X POST http://localhost:8000/api/process/speech \
  -F "file=@voice_memo.m4a" \
  -F 'metadata={"environment":"quiet_home","device":"iphone_13"}' \
  -F 'processing_options={"processor":"nb-whisper-large"}'

# Response: {"job_id": "abc123", ...}
```

#### 3. Check Status
```bash
curl http://localhost:8000/api/jobs/abc123/status
```

#### 4. Get Results
```bash
curl http://localhost:8000/api/jobs/abc123/result
```

### Comparison Testing
```bash
# Test both models
curl -X POST http://localhost:8000/api/process/speech \
  -F "file=@norwegian_speech.m4a" \
  -F 'processing_options={"comparison_mode": true}'
```

## Deployment

### Local Development
```bash
# Start all services
docker-compose up redis -d
celery -A app.workers.tasks worker --loglevel=info &
uvicorn app.main:app --reload
```

### Production (Future)
- Deploy on Hetzner AX102 server
- Use Redis Cluster for high availability
- Scale Celery workers based on load
- Add nginx reverse proxy

## Monitoring

### Logs
```bash
# API logs
tail -f app.log

# Celery logs
celery -A app.workers.tasks worker --loglevel=info

# Redis logs
docker logs dementia-redis
```

### Health Checks
```bash
# Overall health
curl http://localhost:8000/health

# Processor health
curl http://localhost:8000/api/processors/capabilities
```

## Research Features

### Model Comparison
- Parallel processing with NB-Whisper and OpenAI Whisper
- Quality metrics collection (confidence scores, processing time)
- Research data export functionality

### Audio Quality Analysis
- Support for device recording formats (M4A, AAC, MP3, WAV)
- Environment metadata tracking
- Audio quality baseline establishment

### Norwegian-First Processing
- NB-Whisper Large and Medium models
- Local processing (no data leaves your infrastructure)
- GDPR-compliant by design

## Troubleshooting

### Common Issues

**Redis Connection Failed:**
```bash
# Check Redis is running
docker ps | grep redis

# Start if needed
docker-compose up redis -d
```

**Celery Worker Not Processing:**
```bash
# Check worker status
celery -A app.workers.tasks inspect active

# Restart worker
pkill -f celery
celery -A app.workers.tasks worker --loglevel=info
```

**NB-Whisper Model Loading Error:**
```bash
# Check disk space and memory
df -h
free -h

# Model will be downloaded on first use
# Large models need 4-8GB RAM
```

**Audio Processing Fails:**
```bash
# Check file format
file voice_memo.m4a

# Test with different audio formats
ffmpeg -i input.m4a output.wav
```

## Next Steps

1. **Complete NB-Whisper Integration** - Replace placeholder with actual NB-Whisper models
2. **Add File Storage** - Implement SQLite storage for transcription results
3. **Frontend Integration** - Build React file upload interface
4. **Real-World Testing** - Test with device recordings in multiple environments

## API Documentation

Once running, visit:
- http://localhost:8000/api/docs - Interactive API documentation
- http://localhost:8000/api/redoc - Alternative documentation format