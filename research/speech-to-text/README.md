# Norwegian Speech-to-Text API

A fast, accurate Norwegian speech recognition API powered by NB-Whisper models. Built for Norwegian language processing with support for both Bokmål and Nynorsk.

## Features

🎙️ **Norwegian-optimized** - Uses NB-Whisper models specifically trained on Norwegian speech
🚀 **Multiple model sizes** - Choose between 5 model sizes based on speed vs accuracy needs
⚡ **GPU acceleration** - Automatic MPS (Apple Silicon) and CUDA support
📱 **Multiple audio formats** - Supports WAV, MP3, M4A, AAC, FLAC
🔧 **Easy deployment** - Simple setup with automated scripts
📊 **Detailed results** - Confidence scores, timestamps, and segment-level information

## Quick Start

### 1. Setup
```bash
# Clone and navigate to the project
cd research/speech-to-text/

# Run the setup script (installs dependencies, creates venv)
make setup
```

### 2. Start the API
```bash
# Start the server
make run

# Or manually:
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Test the API
```bash
# Check server health
make health

# List available models
make models
```

## API Endpoints

### Health Check
```bash
GET /health
```
Returns server status and loaded model information.

### Transcribe Audio
```bash
POST /api/transcribe
```

**Parameters:**
- `file` (required): Audio file to transcribe
- `model_size` (optional): Model size to use (`tiny`, `base`, `small`, `medium`, `large`)
- `metadata` (optional): JSON metadata about the recording

**Example:**
```bash
curl -X POST http://localhost:8000/api/transcribe \
  -H "Content-Type: multipart/form-data" \
  -F "file=@recording.m4a" \
  -F "model_size=large"
```

### List Models
```bash
GET /api/models
```
Returns information about loaded NB-Whisper models and their capabilities.

## Model Sizes

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| `tiny` | ~39MB | Fastest | Basic | Real-time, low resources |
| `base` | ~74MB | Fast | Good | Quick transcription |
| `small` | ~244MB | Medium | Better | Balanced use |
| `medium` | ~769MB | Slower | High | Quality transcription |
| `large` | ~1550MB | Slowest | Best | Maximum accuracy |

**Default:** `large` (best accuracy)

## Audio Format Support

- **WAV** - Uncompressed audio
- **MP3** - MPEG Audio Layer III
- **M4A** - Apple's AAC audio container
- **AAC** - Advanced Audio Coding
- **FLAC** - Free Lossless Audio Codec

**Maximum file size:** 100MB (configurable)

## Example Response

```json
{
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:05Z",
  "processor_result": {
    "processor": "nb-whisper-large",
    "model_version": "NbAiLab/nb-whisper-large",
    "status": "completed",
    "confidence_score": 0.92,
    "processing_time_ms": 5200,
    "text": "Dette er en test av norsk talegjenkjenning.",
    "segments": [
      {
        "start": 0.0,
        "end": 3.5,
        "text": "Dette er en test av norsk talegjenkjenning.",
        "confidence": 0.92
      }
    ],
    "language": "no"
  },
  "original_filename": "recording.m4a",
  "audio_format": "audio/mp4",
  "duration_seconds": 3.5,
  "quality_metrics": {
    "audio_size_bytes": 45678,
    "processing_time_ms": 5200,
    "sample_rate": 16000,
    "audio_length_seconds": 3.5
  }
}
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Development settings
DEBUG=true

# Upload configuration
UPLOAD_DIR=/tmp/speech_uploads
MAX_FILE_SIZE=100  # MB

# Server configuration
HOST=0.0.0.0
PORT=8000

# Model configuration
DEFAULT_WHISPER_MODEL=large
```

### Hardware Requirements

**Minimum:**
- 4GB RAM
- 2GB disk space (for models)
- Python 3.8+

**Recommended:**
- 16GB RAM (for large model)
- Apple Silicon or NVIDIA GPU
- SSD storage

## Development

### Commands

```bash
# Setup project
make setup

# Start development server
make run

# Check server health
make health

# List available models
make models

# Check GPU availability
make gpu

# Clean up
make clean

# Verify installation
make verify
```

### Project Structure

```
speech-to-text/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── api/
│   │   ├── transcribe.py    # Transcription endpoints
│   │   └── models/          # Request/response models
│   └── processors/
│       ├── base.py          # Processor interface
│       └── speech.py        # NB-Whisper implementation
├── requirements.txt         # Python dependencies
├── setup.sh                 # Installation script
├── run.sh                   # Quick start script
├── Makefile                 # Development commands
└── README.md               # This file
```

## Performance

### Model Loading Time
- **First startup:** ~40 seconds (downloads and loads all 5 models)
- **Subsequent starts:** ~10 seconds (models cached)

### Transcription Speed
Varies by model size and hardware:

| Model | CPU (M2 Max) | GPU (MPS) |
|-------|--------------|-----------|
| tiny | 0.5x realtime | 0.3x realtime |
| base | 0.8x realtime | 0.5x realtime |
| small | 1.5x realtime | 1.0x realtime |
| medium | 3.0x realtime | 2.0x realtime |
| large | 5.0x realtime | 3.5x realtime |

*Lower is faster (0.5x = transcribes 1 minute audio in 30 seconds)*

## API Documentation

When the server is running, interactive API documentation is available at:

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

## Error Handling

The API returns detailed error information:

```json
{
  "status": "failed",
  "processor_result": {
    "processor": "nb-whisper-large",
    "status": "failed",
    "error": "Audio file too large (150MB > 100MB limit)",
    "processing_time_ms": 50
  }
}
```

Common error cases:
- File too large (>100MB)
- Unsupported audio format
- Model loading failure
- Audio processing error

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Returns:
- Server status
- Model loading status
- Available models
- Processing mode
- GPU acceleration status

### Logs

Application logs are written to stdout with structured formatting:

```
2024-01-15 10:30:00 - app.main - INFO - Loading Norwegian Speech Recognition models
2024-01-15 10:30:05 - app.api.transcribe - INFO - Transcribing audio file: test.m4a
2024-01-15 10:30:10 - app.processors.speech - INFO - NB-Whisper transcription completed
```

## Troubleshooting

### Model Download Issues
```bash
# Clear model cache
rm -rf ~/.cache/huggingface/

# Restart and download again
make run
```

### Memory Issues
```bash
# Use smaller model
curl -F "model_size=small" ...

# Check available memory
free -h
```

### Audio Format Issues
```bash
# Convert to supported format using ffmpeg
ffmpeg -i input.wav -ar 16000 output.wav
```

## License

This project uses the NB-Whisper models from NbAiLab, which are based on OpenAI's Whisper architecture.

## Support

For issues and questions:
1. Check the logs for error details
2. Verify audio format is supported
3. Ensure sufficient memory for the model size
4. Try with a smaller model first

---

Built with ❤️ for Norwegian speech recognition