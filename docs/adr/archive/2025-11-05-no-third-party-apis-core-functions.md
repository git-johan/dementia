# ADR: No Third-Party APIs for Core Functions

**Status:** Accepted
**Date:** 2025-11-05
**Deciders:** Johan Josok

## Decision

Core AI functions (speech recognition, language understanding, conversation generation, memory/RAG) must be implemented using self-hosted models without dependency on third-party APIs, especially for health data processing.

## Rationale

- **Privacy compliance**: Zero third-party data transfer eliminates GDPR Article 9 violations
- **Cost advantage**: €1500-18000/year savings vs API services
- **Legal safety**: No dependency on US-based cloud services removes €20M fine risk
- **Service control**: No external dependencies or rate limits for core functionality
- **Quality advantage**: Norwegian models outperform international API alternatives

## Research References

### Economic Analysis
- [Cost Structure Analysis](../technical-research/2025-11-12-cost-structure-analysis.md#competitive-advantages) - €1500-18000/year API cost savings
- [Technical Research](../technical-research/2025-11-05-comprehensive-technical-research.md#competitive-cost-advantages) - Zero LLM API fees with production quality

### Privacy & Legal Requirements
- [Privacy Legal Risks](../technical-research/2025-11-12-privacy-legal-risks.md#self-hosted-compliance) - Benefits of no third-party data transfer
- [Privacy-First Architecture](2025-11-05-privacy-first-architecture.md) - Overarching architectural principle
- [Avoid OpenAI Whisper API](2025-11-12-avoid-openai-whisper-api.md) - Specific example of third-party API rejection

### Quality Benefits
```python
api_vs_local_comparison = {
    "speech_recognition": "NB-Whisper: 2.2% WER vs OpenAI API: 6.8% WER",
    "cost": "Self-hosted: €500/month vs API: €1500-18000/year",
    "privacy": "Local: Zero transfer vs API: €20M fine risk",
    "control": "Self-hosted: Full control vs API: Rate limits, downtime"
}
```

## Core Functions Scope

### Included (Must Be Self-Hosted)
1. **Speech Recognition**: NB-Whisper models only, no external ASR APIs
2. **Language Understanding**: NB-Llama models, no LLM APIs (OpenAI, Anthropic, etc.)
3. **Conversation Generation**: Local language models, no chat APIs
4. **Memory & RAG**: ChromaDB/Qdrant with local embeddings, no external vector APIs
5. **Data Storage**: PostgreSQL/SQLite on owned infrastructure only

### Excluded (May Use External APIs)
1. **Non-health utilities**: Weather, calendar integration (with user consent)
2. **Infrastructure**: Email delivery, SMS notifications (data minimized)
3. **Analytics**: Anonymized usage metrics (no health data)
4. **Backup services**: Encrypted backup to EU providers (no plaintext health data)

## Alternatives Considered

| Option | Pros | Cons | Status |
|--------|------|------|--------|
| OpenAI/Claude APIs | Easy integration, broad capabilities | €20M GDPR risk, costs €1500+/year, US jurisdiction | ❌ Rejected |
| Azure AI Services | Enterprise support, EU regions | Still Microsoft/US, complex compliance, costs | ❌ Rejected |
| Google AI APIs | Good performance, competitive pricing | US-based, privacy concerns, not Norwegian-optimized | ❌ Rejected |
| Self-hosted + API fallback | Flexibility, reliability options | Complex data routing, partial privacy violation | ❌ Rejected |
| Pure self-hosted | Full control, privacy, cost savings | Infrastructure responsibility, model management | ✅ Chosen |

## Implementation Strategy

### Development Phase (Mac M2)
```python
development_stack = {
    "speech_to_text": "NB-Whisper Large (local)",
    "language_model": "NB-Llama-8B (local)",
    "vector_database": "ChromaDB (embedded)",
    "storage": "SQLite (local)",
    "cost": "€0 external APIs"
}
```

### Production Phase (EU Servers)
```python
production_stack = {
    "speech_to_text": "NB-Whisper on vLLM",
    "language_model": "NB-Llama-8B/70B on vLLM",
    "vector_database": "Qdrant cluster",
    "storage": "PostgreSQL cluster",
    "cost": "€500/month infrastructure vs €1500-18000/year APIs"
}
```

## Consequences

**Benefits:**
- **Cost optimization**: €1500-18000/year API cost elimination
- **Privacy guarantee**: Zero health data transfer to third parties
- **Service reliability**: No external API downtime dependencies
- **Quality control**: Models optimized for Norwegian healthcare context
- **Compliance simplicity**: No third-party data processor agreements needed
- **Competitive advantage**: "No cloud APIs for health data" positioning

**Trade-offs:**
- Infrastructure responsibility vs managed API services
- Model updates and maintenance vs automatic API updates
- Initial setup complexity vs immediate API integration
- Scaling management vs API automatic scaling

**Risk Mitigation:**
- Start simple: Single server deployment before scaling
- Use proven models: NB-Whisper and NB-Llama are production-ready
- Staged migration: Mac M2 → Single server → Multi-server
- Backup strategy: Multiple self-hosted instances, no API fallbacks

## Future Review Triggers

- Any proposal to use external APIs for core functions
- When evaluating new AI capabilities (ensure self-hostable)
- During compliance audits (verify no third-party health data sharing)
- If Norwegian models become insufficient (unlikely based on current performance)
- When expanding internationally (assess local hosting requirements per jurisdiction)

## Exception Process

**For non-core functions requiring external APIs:**
1. Data Protection Impact Assessment required
2. Explicit user consent for each API integration
3. Data minimization: Only non-health data to external services
4. EU jurisdiction requirement for any external provider
5. Regular review of necessity and alternatives

**No exceptions allowed for:**
- Speech recognition APIs
- Language model APIs
- Conversation generation APIs
- Health data storage APIs
- Any US-based services processing health data