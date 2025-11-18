# Archived Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) that have been superseded by subsequent decisions. These decisions are preserved for historical context and audit trail purposes.

## Archival Date: 2025-11-18

## Superseding Decision: [Commercial LLM Strategy](../2025-11-18-commercial-llm-strategy.md)

On 2025-11-18, after comprehensive evaluation of open-source vs commercial LLM approaches, we made the strategic decision to adopt commercial frontier LLMs (OpenAI GPT-5/GPT-4o) for core conversational AI instead of self-hosted Norwegian language models.

## Archived Decisions

### 1. [Norwegian Language Models](2025-11-05-norwegian-language-models.md)
**Original Decision**: Use Norwegian-specialized models (NB-Whisper + NB-Llama) for all AI processing
**Why Archived**: Quality evaluation showed specialized Norwegian models insufficient for dementia care conversation requirements
**Key Learning**: Language specialization less important than general conversational intelligence for this use case

### 2. [No Third-Party APIs for Core Functions](2025-11-05-no-third-party-apis-core-functions.md)
**Original Decision**: Avoid external APIs for core functionality to maintain privacy and control
**Why Archived**: Pragmatic assessment revealed commercial APIs necessary for frontier-quality conversational AI
**Key Learning**: Absolute API avoidance impractical when quality requirements exceed self-hosted capabilities

### 3. [LLM Hosting Architecture](2025-11-14-llm-hosting-architecture.md)
**Original Decision**: Self-host large language models on dedicated server infrastructure
**Why Archived**: Small team cannot maintain production-quality LLM infrastructure while building product
**Key Learning**: Infrastructure complexity can overwhelm product development capacity

### 4. [NB-Llama Integration Architecture](2025-11-17-nb-llama-integration-architecture.md)
**Original Decision**: Integrate NB-Llama as primary conversational AI model
**Why Archived**: Implementation completed but quality evaluation showed insufficient conversational sophistication
**Key Learning**: Technical integration success doesn't guarantee product-market fit

## Key Insights from Archived Decisions

### Quality vs. Idealism Trade-off
The archived decisions prioritized privacy and Norwegian specialization over conversational quality. Evaluation revealed that:
- Users need high-quality emotional support over perfect Norwegian grammar
- Dementia care requires frontier-level conversational intelligence
- Specialized Norwegian models lag significantly behind general frontier models

### Resource Reality Check
The archived decisions underestimated the engineering complexity of:
- Production-quality LLM hosting and maintenance
- Model fine-tuning and prompt optimization
- Infrastructure reliability and scaling
- Ongoing model updates and improvements

### Market Validation Priority
The archived decisions pursued perfect solutions before validating market demand:
- Privacy-first approach prevented rapid user feedback
- Complex infrastructure delayed product-market fit testing
- Perfect Norwegian language less important than useful functionality

## Lessons for Future Decisions

### 1. Quality Requirements Drive Architecture
User experience quality requirements must be the primary architectural constraint, not idealistic preferences.

### 2. Resource Constraints Are Real Constraints
Small team capacity is a hard constraint that must shape architectural choices, not be solved through heroic engineering effort.

### 3. Validate First, Optimize Later
Prove product-market fit with pragmatic solutions before investing in complex optimizations.

### 4. Privacy Can Be Phased
Privacy optimization can be a later enhancement rather than a foundational requirement if market demands it.

## What Was Preserved

Not all decisions were reversed. Several principles and implementations remain valid:

### Maintained Decisions
- **[Privacy-First Architecture](../2025-11-05-privacy-first-architecture.md)**: Principles maintained, implementation adapted
- **[Desktop-First Development](../2025-11-05-desktop-first-development.md)**: Still valid approach
- **[EU/Norwegian Server Hosting](../2025-11-12-eu-norwegian-server-hosting.md)**: Applies to our infrastructure
- **[Avoid OpenAI Whisper API](../2025-11-12-avoid-openai-whisper-api.md)**: NB-Whisper remains self-hosted

### Preserved Implementations
- **NB-Whisper Integration**: Self-hosted speech-to-text remains unchanged
- **FastAPI Backend**: Core framework and API structure preserved
- **User Data Control**: Deletion, export, and control features maintained
- **EU Infrastructure**: Backend servers remain EU-hosted

## Current Architecture (Post-Archival)

### Hybrid Approach
The new architecture combines pragmatic commercial APIs with privacy-preserving self-hosted components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Device   │    │   EU Backend     │    │ Commercial APIs │
│                 │    │  (Self-hosted)   │    │   (GDPR-DPA)    │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Audio Input │ ├────► │ NB-Whisper   │ │    │ │ OpenAI      │ │
│ └─────────────┘ │    │ │ (Privacy)    │ │    │ │ GPT-5/4o    │ │
│                 │    │ └──────────────┘ │    │ │ (Quality)   │ │
│ ┌─────────────┐ │    │ ┌──────────────┐ │ ┌──► │             │ │
│ │Text Response│ ◄────┼─┤ Chat API     │ ├─┘  │ └─────────────┘ │
│ └─────────────┘ │    │ │ (Control)    │ │    │ ┌─────────────┐ │
└─────────────────┘    │ └──────────────┘ │    │ │ Claude 3.5  │ │
                       │ ┌──────────────┐ │    │ │ (Fallback)  │ │
                       │ │ User Data    │ │    │ └─────────────┘ │
                       │ │ (Sovereign)  │ │    └─────────────────┘
                       │ └──────────────┘ │
                       └──────────────────┘
```

### Best of Both Worlds
- **Quality**: Frontier commercial LLMs for conversational AI
- **Privacy**: Self-hosted speech processing and data management
- **Control**: EU-based infrastructure for our components
- **Flexibility**: Future privacy tier option if market demands

## Archive Governance

### When to Archive ADRs
ADRs should be archived when:
1. A fundamental strategic change makes them no longer applicable
2. New information significantly changes the decision context
3. Implementation reveals insurmountable practical problems
4. Market feedback contradicts underlying assumptions

### Archive vs. Update
- **Archive**: When the core decision is fundamentally wrong or impossible
- **Update**: When implementation details change but core decision remains valid

### Historical Value
Archived ADRs provide valuable historical context:
- Understanding why certain approaches were tried and abandoned
- Learning from implementation challenges and quality issues
- Providing context for future architectural decisions
- Maintaining audit trail for regulatory and compliance purposes

## Future Considerations

### Potential Un-archival Conditions
These decisions might become relevant again if:
- Open-source Norwegian models dramatically improve (GPT-5 quality level)
- Norwegian regulations require absolute data locality
- Market unanimously demands privacy-first approach
- Team grows sufficient to maintain complex infrastructure

### Monitoring Triggers
- Open-source model quality improvements
- User privacy tier demand (>20% of users)
- Regulatory environment changes
- Commercial API cost escalation

---

*This archive preserves our decision-making journey and provides context for understanding how we arrived at our current commercial LLM strategy.*