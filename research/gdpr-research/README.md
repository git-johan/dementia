# GDPR Research Project

## Research Question
**"Hvordan håndterer vi sensitiv persondata i en AI-verden?"**

How do we handle sensitive personal data in an AI world? This research project explored implementing a privacy-first AI assistant for dementia care using self-hosted Norwegian language models and strict data sovereignty principles.

## Implementation Overview

This project contains a working implementation of privacy-first architecture featuring:

### Core Technologies
- **NB-Llama 3.1-8B-Instruct**: Norwegian-optimized language model for conversations
- **NB-Whisper Large**: Norwegian speech-to-text processing (1.5GB model)
- **FastAPI Backend**: Self-hosted API with EU/Norwegian data sovereignty
- **ChromaDB**: Local vector database for RAG capabilities
- **PyTorch/MPS**: Direct Metal Performance Shaders integration on M2

### Architecture Components
- `app/api/chat.py` - NB-Llama chat API implementation
- `app/processors/transcribe.py` - NB-Whisper speech processing (working)
- `app/main.py` - FastAPI server with health checks
- `tests/` - Validation tests for Norwegian language capabilities

## Key Research Findings

### ✅ Technical Feasibility
- **Self-hosted Norwegian AI is technically viable**
- NB-Whisper demonstrates 3x better accuracy than OpenAI (2.2% vs 6.8% WER)
- Privacy-first architecture successfully implemented
- GDPR-compliant data processing achieved
- EU/Norwegian data sovereignty maintained

### ❌ Quality Gap Identified
- **Open-source models insufficient for dementia care conversations**
- NB-Llama lacks conversational quality needed for vulnerable users
- Limited reasoning capabilities compared to frontier models
- Insufficient safety guardrails for sensitive health interactions
- Norwegian specialization present but overall quality inadequate

### ⚠️ Resource Requirements
- **Significant infrastructure and maintenance overhead**
- Need for specialized AI infrastructure team
- Ongoing model management and optimization required
- Development velocity impact vs commercial APIs

## Research Outcome

The findings from this research project directly informed the strategic decision documented in [Commercial LLM Strategy ADR](../../docs/adr/2025-11-18-commercial-llm-strategy.md):

1. **Privacy-first is technically feasible** but insufficient for product quality requirements
2. **Quality gap too significant** for vulnerable dementia care users
3. **Resource investment** better focused on product features than infrastructure
4. **Pragmatic approach**: Use commercial APIs with GDPR compliance initially

## Code Status

### Working Components
- ✅ **NB-Whisper Integration** (`app/processors/transcribe.py`) - Production-ready speech processing
- ✅ **FastAPI Framework** - Solid backend architecture
- ✅ **Privacy Patterns** - GDPR-compliant data handling implementations
- ✅ **Health Checks** - System monitoring and status endpoints

### Implemented but Quality-Limited
- ⚠️ **NB-Llama Chat API** (`app/api/chat.py`) - Functional but insufficient quality
- ⚠️ **Medical Keyword Detection** - Basic safety boundaries implemented
- ⚠️ **Norwegian Language Processing** - Works but limited compared to frontier models

### Research Value
- 📚 **Reusable Infrastructure**: Patterns and code can be reused for future privacy tier
- 📚 **Quality Baseline**: Provides comparison point for commercial API quality
- 📚 **Migration Foundation**: Self-hosted infrastructure ready if needed
- 📚 **Compliance Template**: GDPR/Norwegian health data handling examples

## Development Environment

### Current Setup
- **Platform**: Mac M2 64GB with MPS acceleration
- **Capacity**: 20-30 concurrent users, 10-15 concurrent transcriptions
- **Models**: NB-Llama (~16GB RAM), NB-Whisper (1.5GB)
- **Cost**: 0 EUR infrastructure during validation phase

### Running the Research Code
```bash
pip install -r requirements.txt
python -m app.main  # Start FastAPI server
```

## Future Considerations

### Potential Graduation to Development
If market demands privacy tier or open-source models improve significantly:
- Code can be moved to `development/` folder structure
- Infrastructure patterns are proven and reusable
- Privacy compliance frameworks established

### Lessons for Trusted Sources
This research informs the trusted sources project:
- Self-hosted processing methods are viable
- Content quality assessment using local models possible
- Privacy-compliant data collection patterns established

## Related Documentation

- [Commercial LLM Strategy ADR](../../docs/adr/2025-11-18-commercial-llm-strategy.md) - Strategic decision based on research
- [Privacy-First Architecture ADR](../../docs/adr/archive/2025-11-05-privacy-first-architecture.md) - Original architecture vision
- [Technical Research Documents](../../docs/technical-research/) - Supporting analysis and investigations

---

*This research project successfully answered the question "How do we handle sensitive data in AI?" - the answer is "Privacy-first is possible but requires quality vs. privacy trade-offs for specific use cases."*