# ADR: LLM Hosting Architecture

**Date**: 2025-11-14
**Status**: Accepted
**Deciders**: Johan Josok

## Context

We are building a Norwegian dementia care AI assistant that requires speech-to-text and conversational AI capabilities. The system must prioritize privacy, GDPR compliance, and high-quality Norwegian language processing. We need to decide where to host the LLM models: on user devices (mobile phones), on our servers, or a hybrid approach.

## Decision Drivers

- **Privacy & Legal**: GDPR Article 9 compliance for health data
- **Language Quality**: Optimal Norwegian speech recognition and conversation
- **User Experience**: Fast, reliable responses across all devices
- **Technical Feasibility**: Resource constraints and development complexity
- **Cost Structure**: Sustainable economic model
- **Device Support**: Wide compatibility across user devices

## Options Considered

### Option 1: Server-Hosted Models (CHOSEN)

**Approach**: Host NB-Whisper and NB-Llama models on EU servers (Hetzner/Green Mountain)

**Pros**:
- Full model quality (NB-Llama-8B/70B, NB-Whisper Large)
- Works on all devices regardless of specifications
- Single deployment and maintenance point
- Predictable server costs (€500-800/month)
- EU data sovereignty (GDPR compliant)
- Superior Norwegian performance (2.2% WER vs 6.8% for international models)

**Cons**:
- Requires internet connectivity
- Server infrastructure costs
- Network latency (mitigated by EU hosting)

### Option 2: Mobile-Hosted Models

**Approach**: Deploy quantized models directly on user devices

**Technical Requirements**:
- NB-Whisper Medium: 769MB storage, ~3GB RAM
- NB-Llama-1B: 1.2GB storage, ~4-6GB RAM
- **Total**: ~2GB storage, 7-9GB RAM when running

**Pros**:
- Zero server costs for inference
- Complete privacy (no data transmission)
- Offline functionality
- Zero network latency

**Cons**:
- **RAM constraints**: Most phones have 6-8GB total RAM, leaving only 2-3GB for apps
- **Device compatibility**: Only high-end phones (12GB+ RAM) could reliably run both models
- **Quality degradation**: 1B parameter model significantly less capable than 8B+ server models
- **Battery impact**: Continuous LLM inference drains battery quickly
- **Development complexity**: Platform-specific optimizations (iOS/Android)
- **Update difficulty**: Model updates require app updates
- **Storage pressure**: 2GB additional storage per user

**Technical Analysis**:
```
Memory Reality Check:
- iPhone 14/15: 6GB total → 2-3GB available → ❌ Insufficient
- Samsung Galaxy S24: 8GB total → 4-5GB available → ❌ Too tight
- iPhone 15 Pro: 8GB total → 4-5GB available → ⚠️ Marginal
- High-end phones: 12-16GB → 8-12GB available → ✅ Would work
```

### Option 3: Hybrid Mobile/Server

**Approach**: Small models on device, larger models on server with intelligent routing

**Architecture**:
- NB-Whisper Medium on device (faster, private)
- NB-Llama-1B on device for simple queries
- NB-Llama-8B on server for complex conversations
- Intelligent routing based on query complexity

**Pros**:
- Best of both worlds for high-end devices
- Offline capability for basic functions
- Optimized for privacy and performance

**Cons**:
- **Complexity**: Significantly more complex development and maintenance
- **Inconsistent experience**: Different capabilities based on device specs
- **Still has mobile RAM constraints**: Limited to high-end devices
- **Routing complexity**: Difficult to determine query complexity reliably
- **Testing burden**: Must test across device capability matrix

### Option 4: Third-Party APIs (REJECTED)

**Examples**: OpenAI API, Anthropic Claude, Azure OpenAI

**Rejection Reasons**:
- **Legal risk**: €20M GDPR fines for health data transfer to US
- **Language quality**: Norwegian WER 6.8% vs 2.2% for NB-Whisper
- **Privacy violation**: Contradicts core privacy-first architecture
- **Cost structure**: €2160+/month vs €500/month self-hosted
- **No control**: Dependent on third-party service availability and policies

## Decision

**We choose Option 1: Server-Hosted Models**

### Primary Rationale

**Technical Feasibility**:
- Mobile RAM constraints make reliable deployment impossible on majority of user devices
- Server hosting provides consistent experience across all devices
- Higher quality models (8B/70B parameters) deliver significantly better conversations

**User Experience**:
- Works reliably on budget phones, older devices, and tablets
- Consistent response quality regardless of device specifications
- No battery drain from continuous AI processing
- Faster development iteration and model updates

**Privacy & Compliance**:
- EU server hosting maintains GDPR compliance
- Norwegian/EU data sovereignty preserved
- No compromise on privacy principles while avoiding mobile constraints

**Economic Model**:
- Predictable server costs (€500-800/month for 100+ users)
- Scales efficiently with user base
- No need for complex device-specific optimizations

## Consequences

### Positive

- **Universal Device Support**: Works on any smartphone/tablet with internet
- **Maximum Model Quality**: Can use full 8B/70B parameter models for superior conversations
- **Simplified Development**: Single deployment target, easier testing and maintenance
- **Consistent Performance**: Same experience for all users regardless of device specs
- **Future-Proof**: Easy to upgrade models without app updates
- **Privacy Maintained**: EU hosting preserves data sovereignty

### Negative

- **Internet Dependency**: Requires network connectivity for AI features
- **Server Costs**: €500-800/month ongoing infrastructure costs
- **Network Latency**: ~100-300ms additional response time (mitigated by EU hosting)

### Neutral

- **Offline Functionality**: Could be added later with lightweight models as backup
- **Mobile Optimization**: Door remains open for future hybrid approach as mobile hardware improves

## Implementation Notes

**Chosen Technology Stack**:
- **Models**: NB-Whisper Large + NB-Llama-8B-Instruct (production)
- **Infrastructure**: Hetzner servers (Germany) for EU compliance
- **Serving**: vLLM for high-performance inference
- **API**: FastAPI + Celery for async processing
- **Development**: Start with Ollama on Mac M2, migrate to vLLM for production

**Migration Path**:
- Phase 1: Mac M2 development (0-30 users, €0 cost)
- Phase 2: Hetzner server (100+ users, €500/month)
- Phase 3: Multi-server cluster (500+ users, €1500+/month)

## Future Considerations

**Potential Mobile Enhancement (2026+)**:
- **Lightweight Offline Mode**: Whisper Tiny + sub-1B model for emergencies
- **Target**: <2GB RAM total, basic functionality only
- **Trigger**: When mobile hardware standardizes on 12GB+ RAM

**Technology Evolution**:
- **Edge Computing**: Consider edge servers for reduced latency
- **Federated Learning**: Explore privacy-preserving collaborative training
- **Model Compression**: Monitor advances in model quantization techniques

## References

- Technical Research: `/docs/technical-research/2025-11-05-comprehensive-technical-research.md`
- Privacy Analysis: `/docs/technical-research/2025-11-12-privacy-legal-risks.md`
- Cost Analysis: `/docs/technical-research/2025-11-12-cost-structure-analysis.md`
- Mac M2 Validation: `/docs/technical-research/2025-11-12-mac-m2-server-analysis.md`