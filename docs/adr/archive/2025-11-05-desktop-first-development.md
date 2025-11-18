# ADR: Desktop-First Development

**Status:** Accepted
**Date:** 2025-11-05
**Deciders:** Johan Josok

## Decision

Develop the dementia care AI assistant as a web application targeting desktop/tablet browsers first, before mobile app development. Use progressive architecture: Desktop prototype → API-based web app → Mobile app deployment.

## Rationale

- **Development efficiency**: No mobile RAM constraints during prototyping phase
- **Quality optimization**: Full 8B+ language models accessible on desktop with unlimited RAM
- **Cost validation**: €0 infrastructure cost during product-market fit validation
- **User testing**: Easier multi-user alpha/beta testing on larger screens
- **Technical simplicity**: Complete development toolchain available, no mobile platform complexity

## Research References

### Technical Analysis
- [Comprehensive Technical Research](../technical-research/2025-11-05-comprehensive-technical-research.md#desktop-first-development-approach) - Development benefits and progressive architecture
- [LLM Hosting Architecture](2025-11-14-llm-hosting-architecture.md) - Mobile RAM constraints analysis (7-9GB needed vs 2-3GB available)
- [Progressive Architecture](../technical-research/2025-11-05-comprehensive-technical-research.md#progressive-architecture) - Phased deployment strategy

### Cost & Development Benefits
```python
desktop_first_benefits = {
    "development_speed": "No mobile constraints during prototyping",
    "model_access": "Full 8B models with unlimited RAM",
    "debugging": "Complete development toolchain available",
    "testing": "Easy user testing with larger groups",
    "cost": "€0 infrastructure during validation phase"
}
```

### Mobile Constraints
- Mobile RAM: 7-9GB needed vs 2-3GB typically available
- Device compatibility: Only high-end phones (12GB+ RAM) could run quality models
- Development complexity: Platform-specific optimization required
- Quality degradation: 1B mobile models vs 8B desktop models

## Alternatives Considered

| Option | Pros | Cons | Status |
|--------|------|------|--------|
| Mobile-First Development | Targets end-user devices, native performance | Mobile RAM constraints, platform complexity, slower development | ❌ Rejected |
| Simultaneous Desktop+Mobile | Covers all platforms immediately | Double development effort, mobile constraints affect design | ❌ Rejected |
| Desktop-Only | Simple development, no mobile complexity | Limits accessibility for elderly users | ❌ Rejected |
| Progressive Desktop→Mobile | Best development efficiency, quality validation first | Delayed mobile deployment | ✅ Chosen |

## Progressive Development Strategy

### Phase 1: Desktop Prototype (Months 1-3)
```python
phase_1_target = {
    "platform": "Web application (desktop/tablet browsers)",
    "deployment": "Mac M2 local development server",
    "models": "NB-Whisper Large + NB-Llama-8B (full quality)",
    "users": "20-30 alpha testers",
    "cost": "€0 infrastructure",
    "focus": "Core functionality validation"
}
```

### Phase 2: Web App Production (Months 4-6)
```python
phase_2_target = {
    "platform": "Responsive web application",
    "deployment": "Hetzner server with API architecture",
    "models": "NB-Whisper + NB-Llama (server-hosted)",
    "users": "100-200 beta users",
    "cost": "€500/month infrastructure",
    "focus": "Scalability and user experience refinement"
}
```

### Phase 3: Mobile App (Months 7+)
```python
phase_3_target = {
    "platform": "Native iOS/Android apps",
    "deployment": "API calls to EU servers",
    "models": "Server-hosted (avoids mobile RAM constraints)",
    "users": "500+ production users",
    "cost": "€1500+/month infrastructure",
    "focus": "Mobile UX optimization and accessibility"
}
```

## User Experience Considerations

### Desktop/Tablet Advantages for Elderly Users
- **Large displays**: Better visibility for users with vision challenges
- **Familiar interfaces**: Many elderly users more comfortable with computers/tablets
- **Text verification**: Larger screens better for reviewing transcriptions
- **Physical keyboards**: Option for text input alongside voice
- **Stable platforms**: Reduced risk of dropping device during use

### Dementia-Specific Interface Features
```python
accessibility_features = {
    "manual_start_stop": "Physical button activation",
    "text_confirmation": "Show transcription for verification",
    "error_recovery": "Graceful handling of recognition failures",
    "progress_feedback": "Clear processing status indicators",
    "large_text_display": "High contrast, adjustable font size"
}
```

## Consequences

**Benefits:**
- **Rapid development**: No mobile platform constraints during prototyping
- **Maximum model quality**: Full 8B/70B parameter models available
- **Cost optimization**: €0 infrastructure during validation phase
- **Better debugging**: Complete development toolchain access
- **User testing efficiency**: Easy screen sharing and collaboration
- **Natural progression**: Desktop → responsive web → mobile app

**Trade-offs:**
- **Delayed mobile deployment**: Mobile app comes in Phase 3 instead of Phase 1
- **Platform limitations**: Desktop/tablet only during initial phases
- **Mobile UX debt**: Desktop-first design may require mobile optimization later

**Risk Mitigation:**
- **Responsive design**: Plan mobile-friendly UI from start
- **API architecture**: Same backend serves desktop and future mobile clients
- **Progressive enhancement**: Desktop features translate to mobile
- **User feedback**: Validate core functionality before mobile complexity

## Technical Implementation

### Web Application Architecture
```python
web_app_stack = {
    "frontend": "Next.js/React with responsive design",
    "backend": "FastAPI + Celery for async processing",
    "deployment": "Progressive: Mac M2 → Hetzner server → Multi-server",
    "models": "Server-hosted NB-Whisper + NB-Llama",
    "database": "SQLite → PostgreSQL progression"
}
```

### Mobile Transition Planning
- **Same API backend**: No server-side changes needed for mobile
- **Responsive design**: Mobile-friendly UI patterns from start
- **Progressive Web App**: Intermediate step before native apps
- **Native development**: React Native or native iOS/Android when ready

## Future Review Triggers

- When desktop/web beta testing shows strong product-market fit
- If user research indicates immediate mobile app demand
- When mobile hardware capabilities significantly improve (12GB+ RAM standard)
- After achieving sustainable user growth on desktop platform
- If competitive pressure requires faster mobile deployment

## Success Metrics

**Phase 1 (Desktop Prototype):**
- 20-30 active alpha users
- Core functionality validated
- Norwegian language quality confirmed

**Phase 2 (Web Production):**
- 100+ active beta users
- Server architecture proven scalable
- User retention and engagement metrics positive

**Phase 3 Readiness:**
- Stable web application with good user feedback
- Clear mobile UX requirements identified
- Sustainable revenue model validated