# ADR: Privacy-First Architecture

**Status:** Accepted
**Date:** 2025-11-05
**Deciders:** Johan Josok

## Decision

Adopt privacy-by-design as the fundamental architectural principle, with local processing, EU/Norwegian data sovereignty, user data ownership, and zero dependency on US-based cloud services for health data.

## Rationale

- **User data ownership**: "All informasjon behandles lokalt eller innenfor EØS; brukeren eier dataene og kan slette dem når som helst" (Vision document)
- **Legal compliance**: GDPR Article 9 requires highest protection for health data from dementia patients
- **Competitive advantage**: Privacy-first positioning differentiates from US cloud-dependent competitors
- **Trust building**: Norwegian healthcare system demands Norwegian/EU data sovereignty
- **Risk elimination**: Local processing eliminates €20M GDPR fine exposure entirely

## Research References

### Vision & Principles Foundation
- [Vision & Principles](../vision-and-principles.md#kjerneprinsipper) - Core principle: "Personvern og kontroll: All informasjon behandles lokalt eller innenfor EØS"
- [GDPR Compliance Analysis](../technical-research/2025-11-05-comprehensive-technical-research.md#privacy--regulatory-landscape) - Local processing advantages and risk elimination
- [Privacy Legal Risks](../technical-research/2025-11-12-privacy-legal-risks.md) - Comprehensive analysis of compliance requirements

### Supporting ADR Decisions
- [ADR: Norwegian Language Models](2025-11-05-norwegian-language-models.md) - Local models eliminate data transfer
- [ADR: Avoid OpenAI Whisper API](2025-11-12-avoid-openai-whisper-api.md) - No US-based APIs for health data
- [ADR: EU/Norwegian Server Hosting](2025-11-12-eu-norwegian-server-hosting.md) - Data sovereignty implementation

## Architecture Principles

### Core Privacy Requirements
```python
privacy_architecture = {
    "data_processing": "Local-first, EU/Norwegian servers only",
    "user_control": "Complete data ownership and deletion rights",
    "third_party_apis": "None for health data processing",
    "legal_compliance": "GDPR Article 9 + Helseregisterloven",
    "competitive_moat": "Privacy advantage over cloud-dependent competitors"
}
```

### Data Flow Design
1. **Voice Recording**: Local device storage until user upload
2. **Speech Processing**: NB-Whisper on EU/Norwegian servers only
3. **Conversation AI**: NB-Llama local processing
4. **Data Storage**: Norwegian/EU servers with user-controlled retention
5. **Backup**: Encrypted, Norwegian/EU jurisdiction only

## Implementation Consequences

**Benefits:**
- **Zero GDPR transfer risk**: All health data stays within adequate jurisdictions
- **User trust**: Complete transparency about data location and control
- **Regulatory advantage**: Exceeds Norwegian healthcare compliance requirements
- **Competitive differentiation**: Privacy-first vs privacy-second competitors
- **Cost optimization**: No API fees for core functions (€1500-18000/year savings)

**Architectural Requirements:**
- Local/self-hosted models for all core AI functions
- EU/Norwegian hosting for all data processing
- User-controlled data retention and deletion
- End-to-end encryption for data at rest and in transit
- No dependencies on non-EU cloud services

**Trade-offs:**
- Higher infrastructure responsibility vs cloud APIs
- Local model management vs managed services
- EU/Norwegian hosting costs vs global cloud pricing

## Privacy-by-Design Implementation

### Data Minimization
- Process only explicitly provided health information
- No web scraping or external data sources
- User controls what data is retained vs deleted

### User Control
- Complete data export capability
- Granular deletion controls (conversations, recordings, metadata)
- Transparent data processing logs
- Opt-in for all data sharing with caregivers/healthcare providers

### Security by Design
- End-to-end encryption for all sensitive data
- Local authentication where possible
- Minimal attack surface (no unnecessary third-party integrations)
- Regular security audits with Norwegian/EU providers

### Transparency
- Clear documentation of all data flows
- User-facing privacy policy in Norwegian
- Technical documentation for healthcare providers
- Open-source components where possible

## Future Review Triggers

- Any proposal to use US-based cloud services
- When evaluating new third-party integrations
- During healthcare compliance audits
- If Norwegian/EU privacy regulations change
- When expanding to other jurisdictions with different requirements

## Compliance Framework

**GDPR Article 9 (Special Category Data):**
- Explicit consent for health data processing
- Legal basis documentation for all processing activities
- Data Protection Impact Assessment completed
- Regular compliance monitoring

**Norwegian Helseregisterloven:**
- Stricter consent requirements beyond GDPR
- Potential Datatilsynet pre-approval requirements
- Explicit prohibition on non-adequate country transfers

**Competitive Advantage:**
- Market positioning: "Norwegian data stays in Norway"
- Healthcare trust: Alignment with Norwegian privacy values
- Regulatory future-proofing: Ahead of compliance curve