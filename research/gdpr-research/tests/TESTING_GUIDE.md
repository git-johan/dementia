# API Testing Guide - Milestone 1

## Quick Setup

### 1. Start Services
```bash
# Terminal 1: Start Redis
cd backend
docker-compose up redis -d

# Terminal 2: Start Celery Worker
cd backend
source venv/bin/activate
celery -A app.workers.tasks worker --loglevel=info

# Terminal 3: Start FastAPI Server
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 2. Import Postman Collection

**File to import:** `tests/Dementia_API_Testing.postman_collection.json`

**Steps:**
1. Open Postman
2. Click "Import" button
3. Select the collection JSON file
4. The collection will appear as "Dementia API Testing - Milestone 1"

### 3. Run Tests

**Option A - Run Individual Tests:**
- Navigate through the folders in order (01 → 02 → 03 → 04 → 05 → 06)
- Run each request manually to see detailed responses

**Option B - Run Complete Collection:**
1. Right-click on "Dementia API Testing - Milestone 1"
2. Select "Run collection"
3. Click "Run Dementia API Testing"
4. Watch all tests execute automatically

## Test Coverage

### ✅ **01. Health Checks**
- Basic health endpoint (`/health`)
- Root endpoint information (`/`)
- **Expected:** All services responding correctly

### ✅ **02. Processor Capabilities**
- List available processors (`/api/processors/capabilities`)
- **Expected:** NB-Whisper processors registered and available

### ✅ **03. Speech Processing Workflow**
- **Upload:** Send test file → get job_id instantly
- **Status:** Check processing progress → see status updates
- **Result:** Retrieve final transcription → complete Norwegian output
- **Expected:** Complete end-to-end workflow functions

### ✅ **04. Model Comparison Testing**
- Test specific processor selection
- Test comparison mode (multiple processors)
- **Expected:** Different processing options work correctly

### ✅ **05. Error Handling**
- Invalid job IDs → proper 404 responses
- Missing files → proper validation errors
- **Expected:** Graceful error handling

### ✅ **06. Performance Testing**
- Concurrent request handling
- Response time validation
- **Expected:** System handles load appropriately

## Success Criteria Validation

Each test validates specific Milestone 1 requirements:

| Criterion | Test Section | Validation |
|-----------|--------------|------------|
| Audio upload returns job_id instantly (<500ms) | 03. Speech Processing Workflow | Response time + job_id presence |
| NB-Whisper processes Norwegian audio correctly | 03. Speech Processing Workflow | Norwegian language detection + transcription |
| Status endpoint shows progress updates | 03. Speech Processing Workflow | Progress tracking + status changes |
| Result endpoint returns transcription with confidence scores | 03. Speech Processing Workflow | Complete result structure |

## Troubleshooting

### Common Issues:

**Tests fail with connection errors:**
```bash
# Check if services are running
curl http://localhost:8000/health
docker ps | grep redis
ps aux | grep celery
```

**File upload tests fail:**
- Ensure `test_audio.txt` exists in backend directory
- Check file permissions

**Job status returns "error":**
- Check Celery worker logs for processor errors
- Verify Redis connection

### Expected Test Results:

**All tests should PASS** for Milestone 1 completion.

**Sample successful workflow response:**
```json
{
  "job_id": "abc-123-def-456",
  "status": "completed",
  "processors_used": [
    {
      "processor": "nb-whisper-large",
      "text": "[Norwegian transcription]",
      "language": "no",
      "confidence_score": 0.8,
      "processing_time_ms": 150
    }
  ],
  "quality_metrics": {
    "audio_size_bytes": 19,
    "processing_time_total_ms": 150
  }
}
```

## Next Steps

Once all tests pass:
1. ✅ Milestone 1 is **COMPLETE**
2. Ready for Milestone 2: Model Comparison & OpenAI Integration
3. Ready for Milestone 3: File Upload Web Interface

---

**Need Help?**
- Check server logs in each terminal
- Verify all services are running with `ps aux | grep -E "(uvicorn|celery|redis)"`
- Test individual endpoints with curl if needed