# Trusted Sources Research Project

## Research Question
**How do we build a comprehensive, privacy-compliant database of trusted dementia information that can enhance our AI assistant's knowledge without compromising data sovereignty?**

This research explores creating a curated knowledge base from Norwegian and international health authorities to support evidence-based responses in dementia care conversations.

## Research Goals

### Primary Objectives
1. **Content Collection**: Gather high-quality dementia care information from Norwegian health authorities
2. **Quality Assessment**: Evaluate content extraction and deduplication methods
3. **RAG Preparation**: Create content suitable for knowledge enhancement
4. **Privacy Compliance**: Ensure collection methods meet Norwegian/EU requirements

### Success Criteria
- Successfully collect content from 5+ Norwegian health sources
- Process and deduplicate ~100 articles
- Document content quality findings
- Identify best sources and collection methods
- Create foundation for potential RAG enhancement

## Experimental Approach

This is **research-focused development**:
- **Simple and experimental**: SQLite storage, basic Python scripts
- **Manual triggers**: CLI commands for experiments
- **Easy iteration**: Can throw away and restart approaches
- **Documentation-heavy**: Capture findings and learnings

## Research Experiments

### 1. Source Evaluation
**Goal**: Identify the best Norwegian sources for dementia care content

**Method**:
- Test content collection from different Norwegian health sites
- Evaluate content quality, freshness, and relevance
- Document which sources provide the most valuable information

**Expected Outcome**: Ranked list of trusted sources with quality assessments

### 2. Content Collection Methods
**Goal**: Find the most effective way to extract useful content

**Method**:
- Compare web scraping approaches (BeautifulSoup, readability, etc.)
- Test different content extraction methods
- Evaluate metadata extraction quality

**Expected Outcome**: Best practices for content collection from Norwegian health sites

### 3. Quality Assessment & Deduplication
**Goal**: Ensure collected content is high-quality and unique

**Method**:
- Implement content similarity detection
- Test deduplication strategies
- Develop quality scoring methods

**Expected Outcome**: Automated quality assessment and deduplication pipeline

### 4. RAG Preparation
**Goal**: Prepare content for potential integration with NB-Llama or commercial LLMs

**Method**:
- Chunk content appropriately for RAG
- Generate metadata for citations
- Test embedding generation with local models

**Expected Outcome**: RAG-ready content with proper attribution

## Trusted Sources Configuration

### 🇳🇴 Norwegian Priority Sources
- **helsedirektoratet.no** (High Priority)
  - Official health authority guidelines
  - Policy documents and recommendations
- **fhi.no** (High Priority)
  - Research findings and health surveillance data
  - Evidence-based guidelines
- **aldringoghelse.no** (Medium Priority)
  - Specialized aging and health content
  - Care guidance for families
- **nasjonalforeningen.no** (Medium Priority)
  - Patient advocacy and support information
  - Practical care advice

### 🌍 International Sources (Lower Priority)
- **who.int** - Global health standards
- **alzheimer-europe.org** - European research and guidelines
- **alz.org** - International best practices
- **ncbi.nlm.nih.gov** - Peer-reviewed research (selected articles)

## Project Structure

```
research/trusted-sources/
├── README.md                      # This file - research goals and findings
├── prototype/                     # Main prototype implementation
│   ├── __init__.py
│   ├── config.py                  # Trusted domains configuration
│   ├── collector.py               # Content collection engine
│   ├── processor.py               # Content processing and cleaning
│   ├── storage.py                 # Simple SQLite storage
│   └── main.py                    # CLI interface for experiments
├── experiments/                   # Quick tests and trials
│   ├── test_crawling.py           # Test different crawling approaches
│   ├── test_content_quality.py    # Content quality experiments
│   └── test_deduplication.py      # Deduplication experiments
├── data/                          # Research data and results
│   ├── trusted_domains.json       # Norwegian health authorities list
│   └── samples/                   # Small sample collections
└── requirements.txt               # Research dependencies
```

## Research CLI Interface

```bash
# Experiment with content collection
python prototype/main.py collect --domain fhi.no --max-pages 5

# Test content processing
python prototype/main.py process --input data/samples/

# Evaluate deduplication
python prototype/main.py dedupe --threshold 0.8

# Export results for analysis
python prototype/main.py export --format json --output results.json
```

## Privacy & Compliance Considerations

### Data Handling
- **Public Content Only**: Collection limited to publicly available information
- **No User Data**: No personal or health data involved in research phase
- **Attribution**: Proper source attribution and citation generation
- **EU Processing**: Content processing on EU/Norwegian infrastructure when moving beyond research

### Ethical Guidelines
- **Respectful Crawling**: Rate limiting and robots.txt compliance
- **Source Attribution**: Clear citation of original sources
- **Content Integrity**: No modification of original content meaning
- **Transparency**: Clear documentation of collection methods

## Research Outcomes (To Be Updated)

### Phase 1: Initial Collection (Current)
- [ ] Source accessibility assessment
- [ ] Basic content extraction working
- [ ] Quality baseline established

### Phase 2: Method Optimization
- [ ] Best content extraction methods identified
- [ ] Deduplication strategies tested
- [ ] Quality scoring implemented

### Phase 3: RAG Preparation
- [ ] Content chunking optimized
- [ ] Citation format standardized
- [ ] Integration pathway defined

## Integration Potential

### With GDPR Research
- Use privacy-compliant processing patterns from `research/gdpr-research/`
- Apply Norwegian language processing knowledge
- Leverage local model capabilities for content assessment

### Future Development Graduation
If research proves successful:
- **Clean Implementation**: Move to `development/trusted-sources-service/`
- **Production Integration**: FastAPI service with PostgreSQL + ChromaDB
- **RAG Pipeline**: Full integration with chosen LLM strategy

## Related Documentation

- [GDPR Research Project](../gdpr-research/README.md) - Privacy-first processing methods
- [Commercial LLM Strategy ADR](../../docs/adr/2025-11-18-commercial-llm-strategy.md) - Current LLM approach
- [Privacy-First Architecture ADR](../../docs/adr/archive/2025-11-05-privacy-first-architecture.md) - Privacy principles

---

*This research answers: "How do we responsibly enhance AI knowledge with authoritative health information while maintaining privacy and accuracy standards?"*