# ADR: Avoid OpenAI Whisper API

**Status:** Accepted
**Date:** 2025-11-12
**Deciders:** Johan Josok

## Decision

Never use OpenAI Whisper API or any US-based third-party speech recognition service for processing dementia patient voice data. Use local processing with NB-Whisper or self-hosted alternatives instead.

## Rationale

- **Maximum GDPR penalty exposure**: €20 million fine risk for health data transfer to USA
- **Automatic violation**: Voice data from dementia patients is "special category" data requiring explicit consent
- **US jurisdiction incompatibility**: No adequacy decision, government access rights conflict with GDPR
- **Norwegian regulatory focus**: Datatilsynet actively monitoring US cloud services in health sector
- **Superior local alternatives**: NB-Whisper achieves better Norwegian performance (2.2% vs 6.8% WER)

## Research References

### Legal Risk Analysis
- [Privacy & Legal Risks](../technical-research/2025-11-12-privacy-legal-risks.md#critical-legal-risks-openai-whisper) - GDPR Article 9 penalty exposure and violation analysis
- [GDPR Maximum Penalty Risk](../technical-research/2025-11-12-privacy-legal-risks.md#gdpr-article-9---maximum-penalty-risk) - Specific fine calculations and enforcement probability
- [Recent Enforcement Actions](../technical-research/2025-11-12-privacy-legal-risks.md#recent-enforcement-actions) - Datatilsynet track record with US cloud services

### Key Risk Data
```python
legal_penalties = {
    "maximum_fine": "€20 million OR 4% global annual revenue",
    "additional_sanctions": "Immediate cessation order for data transfers",
    "personal_liability": "Daily fines for management during continued violation",
    "probability": "HIGH - Datatilsynet actively monitoring health sector"
}
```

### Enforcement Track Record
- €1.2M fine to Oslo Kommune (Google Workspace, 2022)
- Microsoft Teams banned in schools (2023)
- Increased focus on US cloud services in health sector
- Dementia patients = vulnerable group = higher scrutiny

## Alternatives Considered

| Option | Pros | Cons | Status |
|--------|------|------|--------|
| OpenAI Whisper API | Easy integration, good general performance | €20M fine risk, US jurisdiction, worse Norwegian performance | ❌ Rejected |
| Azure AI Speech | Microsoft integration | US-based, same GDPR risks, not Norwegian-optimized | ❌ Rejected |
| Google Speech API | Fast processing | US-based, privacy concerns, no Norwegian optimization | ❌ Rejected |
| NB-Whisper (Local) | 3x better Norwegian accuracy, zero legal risk, €0 cost | Requires local infrastructure | ✅ Chosen |
| Self-hosted Whisper | Known technology, EU hosting possible | Worse Norwegian performance than NB-Whisper | 🔄 Backup option |

## Consequences

**Benefits:**
- **Zero legal risk**: No data transfer = no GDPR Article 9 violations
- **Superior performance**: NB-Whisper 2.2% WER vs OpenAI 6.8% WER on Norwegian
- **Cost savings**: €0 vs potential €20M fine + ongoing API costs
- **Competitive advantage**: Privacy-first positioning intact
- **Norwegian compliance**: Full alignment with Helseregisterloven requirements

**Trade-offs:**
- Local infrastructure required vs API simplicity
- Model management responsibility vs cloud service
- Initial setup complexity vs immediate API access

**Risk Mitigation:**
- €500/month local server cost vs €20M potential fine
- NB-Whisper provides better Norwegian accuracy anyway
- Local processing eliminates all data transfer concerns
- Future-proof against changing privacy regulations

## Implementation Notes

**Immediate Actions:**
- Never integrate OpenAI Whisper API in any development environment
- Use NB-Whisper Large for all speech recognition during development
- Document data sovereignty in all technical specifications
- Train team on GDPR Article 9 special category data requirements

**Architecture Decisions:**
- All speech processing on Norwegian/EU infrastructure only
- No third-party APIs for core speech recognition functionality
- Local processing pipeline from recording to transcription
- Encrypted storage on Norwegian/EU servers only

## Future Review Triggers

- If EU-US adequacy decision is reinstated (unlikely)
- When evaluating any new US-based AI services
- Before considering any cloud speech recognition alternatives
- During compliance audits or legal review processes