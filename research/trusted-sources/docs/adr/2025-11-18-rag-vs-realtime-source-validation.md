# ADR: RAG vs Real-Time Source Validation for Trusted Information

**Date**: 2025-11-18
**Status**: Accepted
**Decision**: Use Retrieval-Augmented Generation (RAG) with pre-crawled trusted sources instead of real-time source validation

## Context

Core safety requirement from QUESTIONS.md: "How do we make sure the AI-assistant references only trusted sources when patients ask questions that require safe and trusted sources?"

For dementia care families asking medical questions, we must provide information that is:
- Verifiably from Norwegian health authorities (helsedirektoratet.no, fhi.no, etc.)
- Properly attributed with citations
- Current and accurate
- Available reliably in conversational interface

Two primary technical approaches considered for ensuring trusted source compliance.

## Options Evaluated

### Option 1: RAG with Pre-Crawled Sources (Selected)
**Architecture**: Crawl trusted domains → Vector database → Semantic search → Augment LLM prompt → Cited response

**Technical Implementation**:
- Periodic crawling of 7 configured trusted domains
- Content processing and chunking for Norwegian text
- Vector embeddings (OpenAI multilingual or Norwegian-specific)
- Query-time semantic search + LLM generation
- Source attribution in responses

### Option 2: Real-Time Source Validation
**Architecture**: LLM response → Claim extraction → Live source fetching → Evidence validation → Modified response

**Technical Implementation**:
- Generate initial response with GPT-4o
- Extract verifiable claims using NLP models
- Concurrent HTTP requests to trusted sources
- Real-time content parsing and semantic matching
- Validate/modify response based on evidence

## Decision Matrix

| Factor | RAG | Real-Time |
|--------|-----|-----------|
| **Response Latency** | 1.6-3.2s | 4-11s |
| **Reliability** | High (no live dependencies) | Low (depends on all sources) |
| **Development Complexity** | Medium (5 components) | High (7+ interdependent systems) |
| **Norwegian Language** | Good (pre-process once) | Poor (real-time NLP challenges) |
| **Quality Control** | Full (pre-vet content) | Limited (live content variability) |
| **Operational Cost** | €15-80/month | €60-180+/month |
| **Failure Mode** | Graceful degradation | Hard failures |

## Technical Rationale

### Performance Requirements
- **Conversational UX**: Sub-3-second responses critical for dementia families
- **Real-time bottleneck**: Norwegian government sites (helsedirektoratet.no) frequently slow (1-5s response times)
- **Concurrent source fetching**: Even with parallelization, slowest source determines latency

### Norwegian Language Challenges
- **Claim extraction**: Available models primarily English-trained
- **Semantic matching**: Norwegian medical terminology requires specialized handling
- **Real-time processing**: Error-prone for compound Norwegian medical terms

### Source Characteristics
- **Update frequency**: Norwegian health guidance changes quarterly, not daily
- **Content stability**: Official health authorities publish comprehensive, stable information
- **Site reliability**: Government sites have 99% uptime but unpredictable response times

### Quality Control Requirements
- **Pre-validation**: RAG allows vetting content before families see it
- **Consistency**: Dementia care requires predictable, reliable information access
- **Attribution accuracy**: RAG enables precise chunk-to-source citation

## Implementation Constraints

### Team Resources
- Small development team requires maintainable solution
- RAG: 10-15 hours/month maintenance
- Real-time: 20-30 hours/month + emergency response for site changes

### Infrastructure Requirements
- RAG: Simple vector database + periodic crawling
- Real-time: Complex claim extraction, concurrent fetching, evidence matching pipelines

### Failure Tolerance
- **Dementia care context**: Cannot afford unreliable responses for vulnerable families
- **RAG degradation**: Potentially stale information (weekly refresh acceptable)
- **Real-time failure**: Complete validation failure when sources unavailable

## Decision

**Selected: RAG with Pre-Crawled Trusted Sources**

Primary factors:
1. **Performance**: 2x faster response times essential for conversational experience
2. **Reliability**: Must work when government sites are slow/down
3. **Quality control**: Pre-validation critical for medical information safety
4. **Resource efficiency**: Sustainable for small team

The trade-off of potential content staleness (mitigated by weekly refresh) is acceptable given the stability of Norwegian health authority guidance.

## Implementation Consequences

### Enables
- Reliable sub-3-second response times
- Complete control over indexed content quality
- Precise source attribution and citation
- Predictable operational costs and maintenance

### Requires
- Periodic re-crawling infrastructure (weekly/monthly)
- Content freshness monitoring
- Vector database management
- Quality assessment of crawled content

### Risks
- Content staleness between updates
- Crawler maintenance when sites restructure
- Vector database storage and performance scaling

---

**Technical Decision**: RAG architecture prioritizes user experience reliability and safety over real-time content freshness for Norwegian dementia care context.