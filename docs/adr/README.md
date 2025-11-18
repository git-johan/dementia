# Architecture Decision Records (ADR)

We are using ADRs to document our architectural decisions. Each ADR is a document that describes a specific decision made during the development of our software. The ADRs are stored in the `docs/adr` directory and are named using a timestamp and a short description of the decision.

## Current Active Decisions (2025-11-18)

### Core Architecture
- **[Commercial LLM Strategy](2025-11-18-commercial-llm-strategy.md)** - Use OpenAI GPT-5/GPT-4o for conversational AI
- **[Pragmatic GDPR Compliance](2025-11-18-pragmatic-gdpr-compliance.md)** - Government-standard privacy approach with US companies + EU hosting

### Technical Decisions
- **[EU/Norwegian Server Hosting](2025-11-12-eu-norwegian-server-hosting.md)** - Host our infrastructure in EU/Norway
- **[Frontend Framework Selection](2025-11-17-frontend-framework-selection.md)** - Framework choice for user interface
- **[Mac M2 Development Phase](2025-11-12-mac-m2-development-phase.md)** - Development environment approach
- **[Device Recording Apps](2025-11-13-device-recording-apps.md)** - Audio capture approach

## Archive

The **[archive/](archive/)** directory contains superseded decisions that are preserved for historical context. Major strategic pivot on 2025-11-18 moved from self-hosted Norwegian models to commercial frontier LLMs.

**Key Archived Decisions** (superseded by Commercial LLM Strategy):
- Norwegian Language Models - Quality insufficient for dementia care
- No Third-Party APIs - Pragmatism over purity for frontier quality
- LLM Hosting Architecture - Small team cannot maintain production infrastructure
- NB-Llama Integration - Implementation completed but quality gap identified
- Privacy-First Architecture - Principles maintained, implementation adapted

See **[archive/README.md](archive/README.md)** for detailed explanation of what was archived and why.

## Decision Guidelines

### When to Create ADRs
* When making architectural decisions that affect multiple parts of the system
* When choosing between significant alternatives (frameworks, services, approaches)
* When introducing new technologies or external dependencies
* When making strategic pivots that supersede previous decisions

### When to Archive ADRs
* When fundamental strategic changes make previous decisions obsolete
* When implementation reveals insurmountable practical problems
* When new information significantly changes the decision context
* When market feedback contradicts underlying assumptions

### ADR Quality Standards
* **Context**: Clear explanation of the problem and constraints
* **Decision**: Specific choice made and primary alternative
* **Consequences**: Both positive and negative implications
* **Rationale**: Evidence-based reasoning for the choice
* **Implementation**: Practical steps and success metrics

## Current Strategic Direction

**Product Strategy**: Quality-first approach prioritizing user value over architectural purity
**Privacy Approach**: Pragmatic GDPR compliance using government-standard practices
**Technology Stack**: Hybrid architecture combining commercial APIs with self-hosted privacy components
**Market Validation**: Rapid iteration and user feedback over premature optimization

The 2025-11-18 strategic pivot reflects lessons learned from initial implementation:
- Quality requirements drive architectural choices
- Resource constraints are real constraints that must be respected
- Market validation should precede complex optimization
- Privacy can be enhanced incrementally rather than being foundational

## Supporting Documentation

- **[Technical Research](../technical-research/)** - Detailed analysis supporting ADR decisions
- **[Archive Documentation](archive/README.md)** - Explanation of superseded decisions
