# ADR: Use Norwegian Language Models (NB-Whisper + NB-Llama)

**Status:** Accepted
**Date:** 2025-11-05
**Deciders:** Johan Josok

## Decision

Use Norwegian-optimized language models (NB-Whisper for speech recognition, NB-Llama for conversation) as primary AI models instead of international alternatives like OpenAI Whisper or general multilingual models.

## Rationale

- **Superior Norwegian performance**: NB-Whisper achieves 2.2% WER vs OpenAI Whisper's 6.8% WER (3x better accuracy)
- **Extensive Norwegian training**: 66,000 hours Norwegian speech data vs limited Norwegian in multilingual models
- **Zero API costs**: Open source models eliminate €1500-18000/year in API fees
- **Cultural alignment**: Models understand Norwegian context, idioms, and dementia care communication patterns
- **Privacy compliance**: Local processing eliminates data transfer requirements

## Research References

### Primary Analysis
- [Comprehensive Technical Research](../technical-research/2025-11-05-comprehensive-technical-research.md#technology-stack-analysis) - Complete model comparison and performance data
- [Norwegian Language Performance](../technical-research/2025-11-05-comprehensive-technical-research.md#norwegian-language-advantage) - Specific WER comparisons and training data

### Key Performance Data
```python
language_performance = {
    "nb_whisper": "2.2% WER on Norwegian",
    "openai_whisper": "6.8% WER on Norwegian",
    "advantage": "3x better accuracy with local models",
    "training_data": "66,000 hours Norwegian speech"
}
```

### Model Specifications
- **NB-Whisper Large**: 1.5GB, best Norwegian performance
- **NB-Whisper Medium**: 769MB, balanced quality/speed
- **NB-Llama-3.1-8B-Instruct**: Desktop/server deployment, excellent quality
- **NB-Llama-3.2-1B**: Mobile-optimized, 1.2GB quantized

## Alternatives Considered

| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| OpenAI Whisper API | Easy integration, multilingual | 6.8% WER on Norwegian, €20M GDPR risk, API costs | 3x worse Norwegian accuracy, legal risk |
| Multilingual Llama 3.3 | Broader language support | Not Norwegian-optimized, no local cultural context | Norwegian specialization more valuable |
| Azure AI Speech | Enterprise support | US jurisdiction, API costs, worse Norwegian performance | Privacy violation, cost, performance |
| Google Speech API | Good general performance | No Norwegian optimization, data transfer, costs | Privacy concerns, not Norwegian-focused |

## Consequences

**Benefits:**
- 3x better Norwegian speech recognition accuracy
- Superior understanding of Norwegian cultural context and idioms
- €0 operational costs (open source)
- Perfect GDPR compliance (local processing)
- Production-ready technology stack in 2025
- Competitive advantage through Norwegian specialization

**Trade-offs:**
- Limited to Norwegian language (aligns with target market)
- Requires local hardware resources vs cloud APIs
- Model management complexity vs API simplicity

**Implementation Notes:**
- Start with NB-Whisper Large + NB-Llama-8B for development
- Use NB-Whisper Medium for production speed/quality balance
- Consider NB-Llama-70B for complex reasoning tasks
- Maintain compatibility with international models for future expansion

## Future Review Triggers

- When expanding to additional Nordic languages
- If international model Norwegian performance significantly improves
- When mobile hardware constraints require smaller models
- If API costs become negligible vs infrastructure costs