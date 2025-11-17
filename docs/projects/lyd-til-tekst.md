# Lyd til tekst

**DateTime:** 2025-11-13 (Updated)
**Phase:** Prototype & Validation
**Status:** DONE

## Status: READY FOR IMPLEMENTATION

**Current Status:** Architecture defined, milestone-based implementation plan ready
**Next Action:** Begin Milestone 1 - Basic Async Speech Processing API
**Blockers:** None
**Last Updated:** 2025-11-13

### Status Legend
- **PLANNING:** Project defined, research plan created
- **READY FOR IMPLEMENTATION:** Architecture complete, ready to start coding
- **IN_PROGRESS:** Active development work
- **TESTING:** Implementation complete, validation phase
- **COMPLETE:** All deliverables finished, research documented
- **PAUSED:** Temporarily halted, waiting for dependencies
- **CANCELLED:** Project discontinued

## Spørsmål vi må besvare

### 1. Er mobiltelefon-mikrofoner tilstrekkelige for demensomsorg-samtaler?

- Fungerer telefon-mikrofoner godt nok i realistiske miljøer når brukt med native recording apps?
- Hvor mye bedre kvalitet får vi med iOS Voice Memos / Android Recorder vs browser recording?
- Hva er optimal avstand og posisjonering når man bruker device recording apps?
- Hvilke miljøfaktorer påvirker kvaliteten mest med profesjonell device recording?

### 2. Hva er trade-offs mellom self-hosted NB-Whisper vs OpenAI Whisper?

- **Kvalitetsforskjeller på norsk tale**
  - Nøyaktighet på dialekter og eldre stemmer
  - Håndtering av medisinske termer på norsk
  - Performance på demens-relaterte talemønstre
- **Privacy og juridiske implikasjoner**
  - GDPR-compliance og datasuverenitet
  - Risiko ved sending av helsedata til USA
- **Kostnad og teknisk kompleksitet**
  - API-kostnader vs self-hosting
  - Utviklings- og vedlikeholdskompleksitet
- **Performance og skalering**
  - Responstider og tilgjengelighet
  - Skalering fra prototype til produksjon

### 3. Hvordan fungerer talegjenkjenning i real-world demensomsorg-situasjoner?

**Test miljøer:**
- **Hjemme stue** med bakgrunnsstøy (2 personer)
- **Kontrollert hjemmemiljø** (2 personer, minimal støy)
- **Gruppe-samtale** rundt kjøkkenbord
- **Opptak hos lege** (legekontor miljø)

**Fokusområder:**
- Samtaler med flere deltakere
- Overlappende tale og avbrytelser
- Forskjellige støynivåer og akustikk
- Typiske demensomsorg-samtaleemner

---

## 🏗️ Technical Architecture

### Core API Design (Processor Plugin Pattern)

Bygget rundt Memory Domain med extensible processor-arkitektur som støtter fremtidige input-typer (PDF, foto, text, etc.).

**Core Endpoints:**
```
POST /api/process/speech              # Upload audio, få job_id umiddelbart
GET  /api/jobs/{job_id}/status        # Sjekk prosessering-progress
GET  /api/jobs/{job_id}/result        # Få ferdig transkripsjon
```

**Request Format:**
```json
{
  "source": {
    "type": "audio",
    "data": "multipart_upload"
  },
  "metadata": {
    "environment": "quiet_home|noisy_home|medical_office",
    "distance": "20cm|1m|2m",
    "context": "doctor_visit|daily_conversation"
  },
  "processing_options": {
    "processor": "nb-whisper-large|openai-whisper",
    "comparison_mode": true
  }
}
```

### Technology Stack

**Backend:**
- **Python FastAPI** - Async API endpoints og request/response handling
- **Celery + Redis** - Background processing for speech recognition (asynkron)
- **SQLite** - Metadata storage (prototype) → PostgreSQL (production)
- **NB-Whisper** - Norsk speech recognition (self-hosted på Mac M2)
- **OpenAI Whisper API** - Sammenligning og research testing

**Frontend:**
- **React + TypeScript** - Mobil-first web application
- **Tailwind CSS** - UI styling optimalisert for demens-brukere
- **File Upload API** - Integration med device recording apps (iOS Voice Memos, Android Recorder)
- **Axios** - API kommunikasjon med polling for job status

**Audio Input Strategy:**
- **iOS Voice Memos** - Professional audio recording med iOS audio processing
- **Android Recorder** - High-quality recording med Android audio enhancements
- **Audio Format Support** - M4A, AAC, MP3, WAV (device native formats)
- **FFmpeg** - Server-side audio format conversion if needed

## 📁 Project Structure

```
dementia/
├── backend/                           # Python FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application
│   │   ├── config.py                  # Environment configuration
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── speech.py              # Speech processing endpoints
│   │   │   ├── jobs.py                # Job status endpoints
│   │   │   └── models/
│   │   │       ├── __init__.py
│   │   │       ├── requests.py        # Pydantic request models
│   │   │       └── responses.py       # Pydantic response models
│   │   ├── processors/                # Processor plugin system
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # BaseProcessor interface
│   │   │   ├── registry.py            # Processor plugin registry
│   │   │   └── speech.py              # Speech processor implementations
│   │   ├── storage/
│   │   │   ├── __init__.py
│   │   │   ├── files.py               # File storage abstraction
│   │   │   └── database.py            # SQLite metadata storage
│   │   └── workers/
│   │       ├── __init__.py
│   │       └── tasks.py               # Celery background tasks
│   ├── tests/
│   │   ├── test_processors/
│   │   ├── test_api/
│   │   └── fixtures/audio_samples/
│   ├── requirements.txt
│   ├── docker-compose.yml             # Redis for development
│   └── README.md
├── frontend/                          # React web application
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.tsx         # Audio file upload interface
│   │   │   ├── ProcessingStatus.tsx   # Job status display
│   │   │   ├── ResultDisplay.tsx      # Transcription results
│   │   │   └── ModelComparison.tsx    # Side-by-side comparison
│   │   ├── services/
│   │   │   ├── api.ts                 # API client
│   │   │   └── fileUtils.ts           # File handling utilities
│   │   ├── types/api.ts               # TypeScript API types
│   │   └── App.tsx                    # Main application
│   ├── package.json
│   ├── tailwind.config.js
│   └── README.md
└── docs/projects/planning-lyd-til-tekst.md
```

---

## 🏁 Development Milestones

### Milestone 1: Basic Async Speech Processing API

**Goal:** Upload audio file → få transcript tilbake (ingen storage, kun prosessering)

**Build:**
- FastAPI project structure med health endpoints
- Celery + Redis setup for background processing
- NB-Whisper processor integration
- Basic job status tracking (in-memory)
- Core API endpoints

**Manual Testing:**
```bash
# 1. Start services
docker-compose up redis -d
celery -A app.workers.tasks worker --loglevel=info
uvicorn app.main:app --reload

# 2. Record audio with device app
# iOS: Use Voice Memos app → Share → Save to Files
# Android: Use Recorder app → Export → Choose location

# 3. Test audio upload with device recording
curl -X POST http://localhost:8000/api/process/speech \
  -F "file=@voice_memo_001.m4a" \
  -F 'metadata={"environment":"quiet_home","source":"ios_voice_memos","device":"iphone_13"}'

# 4. Check status and get result
curl http://localhost:8000/api/jobs/{job_id}/status
curl http://localhost:8000/api/jobs/{job_id}/result
```

**Completion Criteria:**
- ✅ Audio upload returnerer job_id umiddelbart (<500ms)
- ✅ NB-Whisper prosesserer norsk audio korrekt
- ✅ Status endpoint viser progress updates
- ✅ Result endpoint returnerer transkripsjon med confidence scores

### Milestone 2: Model Comparison & OpenAI Integration

**Goal:** Legg til OpenAI Whisper og comparison mode for research

**Build:**
- OpenAI Whisper processor integration
- Processor selection via request parameter
- Comparison mode (kjører begge modeller parallelt)
- Enhanced result format med processor metadata

**Manual Testing:**
```bash
# Test explicit model selection with device recording
curl -X POST http://localhost:8000/api/process/speech \
  -F "file=@voice_memo_002.m4a" \
  -F 'options={"processor": "openai-whisper"}' \
  -F 'metadata={"source":"ios_voice_memos","duration_seconds":45}'

# Test comparison mode with high-quality device audio
curl -X POST http://localhost:8000/api/process/speech \
  -F "file=@voice_memo_003.m4a" \
  -F 'options={"comparison_mode": true}' \
  -F 'metadata={"environment":"doctor_office","quality":"professional_recording"}'
```

**Completion Criteria:**
- ✅ OpenAI Whisper prosesserer samme audio
- ✅ Comparison mode kjører begge modeller parallelt
- ✅ Results inkluderer model-spesifikk metadata

### Milestone 3: File Upload Web Interface

**Goal:** Upload audio fra device recording apps og se transcription results

**Build:**
- React app med Tailwind CSS (mobile-first design)
- FileUpload component med store, intuitive knapper
- Support for multiple audio formats (M4A, AAC, MP3, WAV)
- Real-time job status polling med progress indicators
- Audio file preview og playback before processing
- Large text display egnet for demensomsorgs-scenarioer

**User Flow:**
1. Record conversation med iOS Voice Memos eller Android Recorder
2. Åpne web app på samme device
3. Upload audio file from device storage
4. Select processing options (model comparison, metadata)
5. View transcription results med large, readable text

**Manual Testing:**
- Record audio med Voice Memos (iOS) eller Recorder (Android)
- Åpne web app på mobil browser
- Test file upload med forskjellige audio formats
- Verifiser audio preview fungerer før processing
- Sjekk at processing status updates i real-time
- Test med forskjellige file sizes (30 seconds til 10+ minutter)

**Completion Criteria:**
- ✅ File upload fungerer med alle major audio formats fra device apps
- ✅ Audio preview og playback fungerer før upload
- ✅ Upload trigger prosessering og viser progress
- ✅ Results vises klart med demens-vennlig UI
- ✅ Supports larger audio files (up to 30+ minutes)

### Milestone 4: Research Comparison Interface

**Goal:** Side-by-side model comparison for research og testing

**Build:**
- Model selection interface
- Side-by-side transcription display
- Quality metrics visualization
- Export results som JSON/CSV for analyse
- Test scenario tracking

**Completion Criteria:**
- ✅ Lett model comparison via web interface
- ✅ Klar quality metrics visualization
- ✅ Research data export funksjonalitet

### Milestone 5: Storage & Retrieval

**Goal:** Persister transcriptions for senere access og analyse

**Build:**
- SQLite database integration
- Transcription storage med metadata
- Retrieval endpoints
- Search og filtering capabilities

**New API Endpoints:**
```
GET /api/transcriptions                    # List stored transcriptions
GET /api/transcriptions/{id}               # Get specific transcription
DELETE /api/transcriptions/{id}            # Delete transcription
```

**Completion Criteria:**
- ✅ Alle transcriptions lagret permanent
- ✅ Efficient retrieval og search capabilities
- ✅ Research data akkumuleres over tid

### Milestone 6: Real-World Testing & Documentation

**Goal:** Systematisk testing og research question analyse

**Real-World Testing:**
- **Quiet Home Environment:** Test device recording distances (20cm, 1m, 2m) med Voice Memos/Recorder
- **Noisy Home Environment:** Kjøkken, TV background, multiple speakers med professional device recording
- **Device Variety:** iPhone Voice Memos, Android Recorder, tablets med built-in noise cancellation
- **Content Variety:** Medical conversations, daily chat, norske dialekter med optimal device audio quality
- **Audio Quality Baseline:** Professional device recordings som foundation for accuracy testing

**Research Analysis:**
- Sammenlign NB-Whisper vs OpenAI accuracy på norsk tale
- Dokument mobile microphone quality effectiveness
- Analyser environmental impact på transcription quality
- Generer anbefalinger for produksjonsdeployment

---

## Teknologi vi bygger

### Processor Plugin Architecture

**Memory Domain med extensible processors:**
```python
# Base interface alle processors implementerer
class MemoryProcessor(ABC):
    @abstractmethod
    async def process(self, content: bytes, metadata: dict) -> ProcessorResult:
        pass

    @abstractmethod
    def validate_input(self, content: bytes) -> bool:
        pass

# Speech processor implementasjoner
class NBWhisperProcessor(MemoryProcessor):
    # NB-Whisper Large/Medium implementation

class OpenAIWhisperProcessor(MemoryProcessor):
    # OpenAI Whisper API implementation
```

**Framtidig utvidelse:**
- `DocumentProcessor` for PDF OCR
- `PhotoProcessor` for medication recognition
- `TextProcessor` for forms og questionnaires

### Quality Assessment System

**Automatic Quality Metrics:**
- Confidence scores fra begge modeller
- Processing time comparison
- Text coherence analysis
- Background noise detection

**Research Metrics Collection:**
- Environment metadata tracking
- Device recording app quality assessment (Voice Memos vs Recorder vs browser)
- Audio format impact analysis (M4A vs WAV vs WebM)
- Success/failure tracking per scenario type med professional audio baseline
- Export functionality for research analysis med audio quality metrics

---

## Deliverables

### 1. Fungerende Async Speech Processing API
- FastAPI backend med processor plugin architecture
- NB-Whisper og OpenAI Whisper integration
- Job-basert async processing med status tracking

### 2. File Upload Web Interface for Testing
- React app optimalisert for device audio file upload
- Professional audio format support (M4A, AAC, MP3, WAV)
- Real-time processing status og results display
- Model comparison interface for research med high-quality audio baseline

### 3. Sammenlignende Analyse av Speech Recognition-modeller
- Kvantitativ sammenligning av nøyaktighet på norsk
- Quality metrics visualization og data export
- Kostnad-nytte analyse av self-hosted vs cloud

### 4. Real-World Testing Data fra Demensomsorg-miljøer
- Dokumenterte test-resultater fra alle fire miljøer
- Analyse av miljøfaktorer som påvirker kvalitet
- Guidelines for optimal opptak-setup

### 5. Skalebar Architecture Foundation
- Processor plugin system ready for future input types
- Domain-driven design aligned med overall architecture
- Clear migration path fra prototype til produksjon

### 6. Research Log Entry med Alle Funn Dokumentert
- Komplett entry i `technical-research/` systemet
- Kvantitative resultater og benchmarks
- Anbefalinger for neste utviklingsfase

---

## Success Criteria

### Minimum Viable Results
- ✅ Fungerende async API som kan teste begge speech recognition modeller
- ✅ File upload web interface som kan process professional device audio
- ✅ Test-data fra alle fire real-world miljøer med high-quality recordings
- ✅ Clear recommendation på hvilken model som skal brukes videre

### Optimal Results
- 🎯 Validert at device recording apps gir tilstrekkelig kvalitet for målbruken
- 🎯 NB-Whisper presterer like bra eller bedre enn OpenAI på professional norsk audio
- 🎯 Audio quality baseline established for future native app comparison
- 🎯 Processor plugin architecture ready for next phase expansion
- 🎯 Foundation som kan skaleres til produksjonsmiljø med proven audio quality

---

## Neste Fase Preview

Basert på resultatene fra "Lyd til tekst" vil neste fase fokusere på:

### Phase 2: Context Domain Integration
- **RAG Implementation** med retrieval av stored transcriptions
- **Relevance determination** for conversation context
- **Integration** med existing Memory domain APIs

### Phase 3: Conversation Domain
- **NB-Llama integration** for norsk language understanding
- **Conversation flow management** med memory retrieval
- **Medical boundary enforcement** på conversation level

### Phase 4: Additional Input Processors
- **Document processor** for PDF OCR (medical documents)
- **Photo processor** for medication recognition
- **Text processor** for forms og structured data input

---

*Dette dokumentet definerer vår milestone-baserte tilnærming til første prototype-fase. Vi bygger en skalebar processor plugin architecture som systematisk kan besvare de kritiske forskningsspørsmålene om voice-to-text processing i demensomsorgs-kontekst.*
