# ADR: Commercial LLM Strategy for Core Conversational AI

**Status:** Accepted
**Date:** 2025-11-18
**Deciders:** Johan Josok
**Supersedes:** [Archived ADRs](archive/) - Norwegian Language Models, No Third-Party APIs, LLM Hosting Architecture, NB-Llama Integration

## Decision

Adopt frontier commercial LLM APIs (OpenAI GPT-5, GPT-4o, Anthropic Claude) for core conversational AI instead of self-hosted Norwegian language models, with OpenAI GPT-5 as the primary target and GPT-4o as the immediate implementation choice.

## Context

After implementing and evaluating various approaches to Norwegian language AI for dementia care assistance, we've reached a fundamental conclusion about quality requirements versus implementation complexity.

### Key Realizations

1. **Quality Gap**: Open-source models (including specialized Norwegian models like NB-Llama) are insufficient for the conversational quality required for dementia care assistance
2. **Resource Constraints**: A small development team cannot maintain production-quality self-hosted LLM infrastructure while building product features
3. **Market Reality**: Unknown product-market fit makes premature optimization for privacy infrastructure a risky investment
4. **User Segmentation**: Not all users require maximum data sovereignty; many will accept GDPR-compliant commercial services
5. **Time-to-Market**: Need to validate product concept before investing in complex privacy infrastructure

## Strategic Architecture

### Primary LLM Strategy
```python
llm_strategy = {
    "primary_target": "OpenAI GPT-5",           # When available (Q1 2025)
    "immediate": "OpenAI GPT-4o",               # MVP implementation
    "fallback": "Anthropic Claude 3.5 Sonnet", # Redundancy/comparison
    "speech_processing": "NB-Whisper (self-hosted)", # Keep existing
    "migration_approach": "Phased transition with user choice"
}
```

### Rationale

#### **Frontier Quality Requirements**
- **Conversational Excellence**: GPT-5/GPT-4o provide significantly superior:
  - Context understanding and memory
  - Empathetic responses for dementia care scenarios
  - Complex reasoning and multi-turn conversations
  - Safety guardrails and harmful content prevention
  - Norwegian language capability (while not specialized, sufficient quality)

- **Open-Source Limitations**:
  - Insufficient conversational quality for sensitive dementia care scenarios
  - Limited reasoning capabilities compared to frontier models
  - Requires extensive prompt engineering and fine-tuning
  - Less reliable safety boundaries for vulnerable user interactions

#### **Pragmatic Product Development**
- **Validate First**: Prove product-market fit before complex privacy architecture
- **Resource Efficiency**: Small team focus on product features, not infrastructure management
- **Faster Iteration**: Commercial APIs enable rapid development and user feedback cycles
- **Cost Efficiency (Early Stage)**: €100-500/month API costs vs €1000-2000/month self-hosted + engineering overhead

#### **Privacy Pragmatism**
- **GDPR Compliance**: OpenAI provides compliant Data Processing Agreements
- **User Segmentation Strategy**:
  - **MVP Target**: Users comfortable with GDPR-compliant commercial services (estimated 70-80% of market)
  - **Future Enterprise**: Self-hosted tier for maximum privacy requirements (if market demands)
- **Regulatory Reality**: OpenAI GDPR compliance sufficient for Norwegian market entry

## Implementation Strategy

### Phase 1: Commercial API MVP (Immediate - Month 3)
**Target Model**: OpenAI GPT-4o
**Goal**: Validate product-market fit
**User Base**: 10-100 beta users
**Cost**: €100-500/month
**Focus**: Product validation and user feedback

**Technical Implementation**:
- Replace existing LLM integration with OpenAI API
- Maintain NB-Whisper for speech-to-text (proven, privacy-friendly)
- GDPR-compliant data processing setup
- User consent flow for commercial LLM usage

### Phase 2: GPT-5 Migration (Q1-Q2 2025)
**Target Model**: OpenAI GPT-5 (when available)
**Goal**: Leverage next-generation frontier capabilities
**User Base**: 100-1000 users
**Cost**: €500-2000/month
**Decision Point**: Monitor privacy tier demand

**Triggers for GPT-5 Migration**:
- GPT-5 general availability
- Quality improvements over GPT-4o demonstrated
- API pricing competitive with GPT-4o

### Phase 3: Segmented Strategy (Year 2+)
**Conditional Implementation**: Only if market demands privacy tier
**Standard Tier**: Commercial LLMs (OpenAI/Claude)
**Enterprise Tier**: Self-hosted Norwegian models
**Pricing**: Premium for self-hosted privacy

**Triggers for Privacy Tier**:
- 20%+ users explicitly request maximum privacy option
- Enterprise/hospital partnerships require self-hosted solutions
- Revenue supports dedicated infrastructure team
- Open-source Norwegian models reach sufficient quality

## Alternatives Considered

### Option 1: Continue with Self-Hosted NB-Llama (REJECTED)

**Why Rejected**:
- ❌ Insufficient conversational quality for dementia care requirements
- ❌ Requires specialized team and infrastructure expertise
- ❌ Premature optimization before market validation
- ❌ Months of engineering effort before user value delivery

### Option 2: Wait for Better Open Models (REJECTED)

**Why Rejected**:
- ❌ Unknown timeline (potentially years for frontier quality)
- ❌ Delays product validation indefinitely
- ❌ Competitive disadvantage in rapidly moving market
- ❌ Market opportunity window may close

### Option 3: Hybrid Architecture (PARTIALLY ADOPTED)

**Selected Elements**:
- ✅ Primary: OpenAI GPT-5/GPT-4o for conversational AI
- ✅ Secondary: Claude for fallback and comparison
- ✅ Keep NB-Whisper: Self-hosted speech-to-text (working well)
- ✅ Future optionality: Privacy tier if market demands

## Privacy and Compliance Strategy

### GDPR Compliance Approach
- **OpenAI DPA**: Implement Data Processing Agreement for GDPR compliance
- **EU Data Residency**: Utilize OpenAI's European data processing options
- **Data Minimization**: Send only necessary conversational context to APIs
- **User Transparency**: Clear privacy policies about commercial API usage
- **User Control**: Maintain data deletion and export capabilities

### Risk Assessment
**Previous Concerns** (from archived ADRs):
- €20M maximum fine exposure
- US jurisdiction data processing concerns
- Datatilsynet enforcement precedents

**Updated Assessment**:
- **Managed Risk**: Proper DPA implementation reduces regulatory exposure
- **Market Precedent**: Norwegian healthcare apps successfully use commercial APIs
- **User Choice**: Transparent consent and future privacy tier option
- **Regulatory Balance**: GDPR compliance vs product innovation needs

### Comparison to Privacy-First Vision
**Unchanged Principles**:
- User data ownership and control
- Transparent privacy policies
- EU/Norwegian data sovereignty where feasible
- User deletion and export rights

**Adapted Implementation**:
- Pragmatic GDPR-compliant commercial APIs for core LLM
- Self-hosted components where simpler (speech processing)
- Future migration path to maximum privacy if demanded

## Technical Migration Plan

### Immediate Changes (Week 1-2)
1. **Replace LLM Integration**: Swap NB-Llama calls with OpenAI API
2. **Implement DPA**: Set up GDPR-compliant data processing with OpenAI
3. **Update Privacy Policy**: Transparent disclosure of commercial API usage
4. **User Consent Flow**: Clear opt-in for commercial LLM processing
5. **Cost Monitoring**: Implement usage tracking and cost controls

### Keep Unchanged
- **NB-Whisper Integration**: Speech-to-text remains self-hosted
- **FastAPI Backend**: Core architecture unchanged
- **User Data Management**: Deletion, export, and control features
- **EU Server Hosting**: Our infrastructure remains EU-based

### Future Decision Points
**Month 3**: MVP success assessment
- User satisfaction with conversational quality
- Privacy concern feedback from users
- Cost per user at current usage patterns

**Month 6**: GPT-5 migration evaluation
- GPT-5 availability and performance vs GPT-4o
- User base growth and cost scaling

**Month 12**: Privacy tier decision point
- Demand signals from users/enterprises
- Open-source model quality improvements
- Revenue to support infrastructure complexity

## Cost-Benefit Analysis

### Financial Projections

**Commercial API Costs**:
```
MVP (10-100 users):     €100-500/month
Growth (100-1000 users): €500-2000/month
Scale (1000+ users):    €2000+/month
```

**Self-Hosted Alternative** (if we had continued):
```
Infrastructure: €500-1500/month
Engineering: 3-6 months full-time
Maintenance: 20-30% ongoing engineering capacity
Quality risk: Insufficient for product requirements
```

**Break-Even Analysis**:
- Commercial APIs cheaper until 1000+ users
- BUT: Quality gap means self-hosted not viable regardless of cost
- **Decision**: Commercial provides 10x better quality-adjusted value

### Non-Financial Benefits
- ✅ **Superior User Experience**: Frontier model conversational quality
- ✅ **Faster Product Development**: Team focuses on features, not infrastructure
- ✅ **Rapid Market Validation**: Quick testing and iteration cycles
- ✅ **Competitive Advantage**: Best-in-class AI capabilities from day one
- ✅ **Future Flexibility**: Option to add privacy tier if market demands

## Risk Mitigation

### Technical Risks
- **Vendor Lock-in**: Mitigated by dual provider strategy (OpenAI + Claude)
- **API Reliability**: Implement graceful fallback and error handling
- **Cost Escalation**: Monitor usage patterns, implement cost controls and alerts
- **Model Availability**: Plan for GPT-5 migration timeline uncertainties

### Privacy Risks
- **GDPR Compliance**: Proactive DPA implementation and legal review
- **User Trust**: Transparent communication about data processing
- **Regulatory Changes**: Monitor Datatilsynet guidance, maintain migration options
- **Data Exposure**: Minimize context sent to APIs, implement audit logging

### Product Risks
- **Quality Dependency**: Extensive testing before full user deployment
- **Norwegian Language**: Continuous evaluation vs specialized models
- **User Acceptance**: Clear privacy policies and consent, monitor feedback
- **Market Shift**: Preserve optionality for privacy tier if preferences change

## Success Metrics

### MVP Validation (Month 3)
- **User Satisfaction**: >4.0/5 for conversational quality
- **Privacy Concerns**: <20% users requesting maximum privacy alternative
- **Cost Per User**: Within €5-10/month target range
- **Technical Reliability**: >99.5% API uptime

### Growth Validation (Month 6-12)
- **User Retention**: >80% monthly retention rate
- **Word of Mouth**: Organic growth from satisfied users
- **Enterprise Interest**: Inbound inquiries for privacy tier
- **Norwegian Quality**: Competitive with specialized models for use case

## Consequences

### Positive Outcomes
- ✅ **Best-in-Class Quality**: Frontier model conversational capabilities for dementia care
- ✅ **Rapid Market Entry**: Fast product validation and user feedback cycles
- ✅ **Team Focus**: Engineering effort on product features, not infrastructure
- ✅ **User Value**: Superior assistance quality from day one
- ✅ **Strategic Flexibility**: Option for privacy tier if market demands

### Research Outcomes
- ✅ **Proven Infrastructure**: GDPR research project demonstrates self-hosted capabilities in `research/gdpr-research/`
- ✅ **Quality Baseline**: NB-Llama implementation provides comparison point for commercial API quality
- ✅ **Migration Foundation**: Research infrastructure can be reused if returning to self-hosted approach

### Trade-offs Accepted
- ❌ **Privacy Compromise**: Health conversations processed by commercial APIs
- ❌ **Vendor Dependency**: Reliance on OpenAI/Anthropic for core functionality
- ❌ **Cost Scaling**: Per-conversation costs vs fixed infrastructure
- ❌ **Norwegian Specialization**: Less linguistic optimization than dedicated models

### Mitigation of Trade-offs
- **Privacy**: GDPR compliance, user choice, future privacy tier option
- **Vendor Risk**: Dual provider strategy, maintain migration capability
- **Cost Management**: Usage monitoring, tier optimization, user value focus
- **Language Quality**: Continuous evaluation, prompt optimization, future model improvements

## Future Evolution

### Expected Trajectory
**Short-term (0-12 months)**:
- GPT-4o → GPT-5 migration for quality improvements
- User base growth with commercial API approach
- Monitor demand for privacy alternatives

**Medium-term (1-3 years)**:
- Conditional privacy tier if 20%+ demand
- Enterprise partnerships requiring self-hosted options
- Open-source model quality reassessment

**Long-term (3+ years)**:
- Potential full migration back to self-hosted if:
  - Open-source models reach GPT-5 quality
  - Regulatory environment requires it
  - User base demands maximum privacy

### Decision Reversal Triggers
**Back to Self-Hosted**:
- Datatilsynet challenges commercial API approach
- OpenAI/Claude pricing becomes unsustainable
- Open-source Norwegian models reach frontier quality
- Market unanimously demands privacy-first positioning

**Forward to Maximum Privacy**:
- Norwegian regulatory changes require local processing
- Enterprise market demands exceed consumer market
- Self-hosted technology becomes significantly easier

## References

### Superseded Decisions
- [Norwegian Language Models](archive/2025-11-05-norwegian-language-models.md) - Quality insufficient for requirements
- [No Third-Party APIs](archive/2025-11-05-no-third-party-apis-core-functions.md) - Pragmatism over purity
- [LLM Hosting Architecture](archive/2025-11-14-llm-hosting-architecture.md) - Self-hosting not viable for small team
- [NB-Llama Integration](archive/2025-11-17-nb-llama-integration-architecture.md) - Implementation completed but quality gap identified

### Supporting Research
- [Technical Research: Commercial LLM Evaluation](../technical-research/2025-11-18-commercial-llm-evaluation.md) *(to be created)*
- [Qwen3:30b API Compatibility Analysis](../technical-research/qwen3-api-investigation.md) - Discovered thinking field vs content field issue

### Research Implementation
- [GDPR Research Project](../../research/gdpr-research/README.md) - Contains implementation of privacy-first architecture that informed this decision
- [NB-Llama Implementation](../../research/gdpr-research/app/api/chat.py) - Working Norwegian language model implementation
- [NB-Whisper Integration](../../research/gdpr-research/app/processors/transcribe.py) - Proven self-hosted speech processing

### Unchanged Decisions (Still Valid)
- [Privacy-First Architecture](2025-11-05-privacy-first-architecture.md) - Principles maintained, implementation adapted
- [Desktop-First Development](2025-11-05-desktop-first-development.md) - Still valid
- [EU/Norwegian Server Hosting](2025-11-12-eu-norwegian-server-hosting.md) - Applies to our infrastructure
- [Avoid OpenAI Whisper API](2025-11-12-avoid-openai-whisper-api.md) - NB-Whisper remains self-hosted

## Implementation Notes

### Immediate Technical Tasks
1. **OpenAI Integration**: Replace current LLM calls with OpenAI API
2. **GDPR Setup**: Implement Data Processing Agreement
3. **User Consent**: Add clear opt-in flow for commercial processing
4. **Cost Monitoring**: Track usage and implement alerts
5. **Privacy Policy**: Update with transparent API disclosure

### Preserved Architecture
- **NB-Whisper**: Continue self-hosted speech-to-text
- **FastAPI Backend**: Core framework unchanged
- **User Data Control**: Deletion and export capabilities
- **EU Infrastructure**: Backend servers remain EU-hosted

### Success Monitoring
- User satisfaction surveys focused on conversational quality
- Privacy concern feedback tracking
- Cost per user monitoring and optimization
- Competitive analysis against other dementia care solutions

---

*This ADR represents a major strategic pivot from privacy-first to pragmatic product validation. The decision prioritizes user value and market validation while preserving future optionality for maximum privacy approaches.*