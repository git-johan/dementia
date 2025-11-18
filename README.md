# Norwegian Dementia Care AI Assistant

A research project exploring how to responsibly build AI-powered assistance for dementia care in Norway, with focus on privacy, data sovereignty, and user safety.

## 🔬 Project Structure

This project is organized into clear research, development, and production phases:

```
/
├── docs/                    # Project-wide documentation and decisions
│   ├── adr/                 # Architecture Decision Records
│   ├── key_questions.md     # Core research questions
│   └── technical-research/  # Research findings and analysis
├── research/                # Research projects and prototypes
│   ├── gdpr-research/       # Privacy-first AI implementation research
│   ├── trusted-sources/     # Authoritative health information research
│   └── shared/              # Shared utilities for research projects
├── development/             # Future production-ready services (currently empty)
└── production/              # Production deployment (reminder: not ready yet)
```

## 🧠 Core Research Questions

### Primary Question
**"Hvordan håndterer vi sensitiv persondata i en AI-verden?"**
*How do we handle sensitive personal data in an AI world?*

### Supporting Questions
1. How do we build trustworthy AI for vulnerable dementia patients?
2. What's the right balance between privacy and AI capability?
3. How do we ensure Norwegian language quality in dementia care?
4. What sources can we trust for dementia care information?

## 📚 Research Projects

### GDPR Research (`research/gdpr-research/`)
**Question**: How do we implement privacy-first AI for dementia care?

**Status**: Completed research phase
- ✅ Self-hosted Norwegian AI technically feasible
- ❌ Quality gap too significant for dementia care requirements
- ✅ Privacy-first patterns proven and documented
- 📄 **Outcome**: Strategic pivot to commercial APIs with GDPR compliance

**Key Findings**: Privacy-first is technically possible but requires quality vs. privacy trade-offs for dementia care use cases.

### Trusted Sources Research (`research/trusted-sources/`)
**Question**: How do we build a database of trusted dementia information for AI enhancement?

**Status**: Active research phase
- 🧪 Content collection from Norwegian health authorities
- 🧪 Quality assessment and deduplication methods
- 🧪 RAG-ready content preparation
- 🧪 Privacy-compliant processing methods

**Goal**: Create foundation for evidence-based AI responses with proper source attribution.

## 🏗️ Architecture Decisions

Key architectural decisions are documented in [Architecture Decision Records](docs/adr/):

### Current Strategy ([ADR 2025-11-18](docs/adr/2025-11-18-commercial-llm-strategy.md))
- **Primary LLM**: OpenAI GPT-5 (target) / GPT-4o (immediate)
- **Speech Processing**: Self-hosted NB-Whisper (proven 3x better Norwegian accuracy)
- **Privacy Approach**: GDPR-compliant commercial APIs with future privacy tier option
- **Rationale**: Quality requirements for dementia care exceed open-source capabilities

### Privacy Principles ([Archived ADR](docs/adr/archive/2025-11-05-privacy-first-architecture.md))
- User data ownership and control
- Transparent privacy policies
- EU/Norwegian data sovereignty where feasible
- Complete deletion and export rights

## 🔍 Development Philosophy

### Research Phase (Current)
- **Experimental and messy** - quick iterations, throw away what doesn't work
- **Question-driven** - every project answers specific research questions
- **Documentation-heavy** - capture learnings for future decisions
- **Risk-tolerant** - safe to fail fast and learn

### Development Phase (Future)
- **Production-bound** - code being built for eventual deployment
- **Quality-focused** - proper testing, documentation, maintainability
- **User-validated** - proven concepts with market demand

### Production Phase (Not Ready)
- **User-safe** - extensively tested with dementia patients and caregivers
- **Legally compliant** - full GDPR and Norwegian health data compliance
- **Professionally validated** - healthcare professional approval and oversight

## 🇳🇴 Norwegian Focus

### Language Technology
- **NB-Whisper**: Norwegian speech recognition (3x better than OpenAI for Norwegian)
- **NB-Llama**: Norwegian language model evaluation (quality insufficient for dementia care)
- **Norwegian Content**: Prioritizing helsedirektoratet.no, fhi.no, and other trusted Norwegian sources

### Compliance Requirements
- **GDPR Article 9**: Special category health data protection
- **Helseregisterloven**: Norwegian health data regulations
- **Datatilsynet**: Norwegian data protection authority compliance

## 📊 Current Status

### Completed Research
- [x] Privacy-first architecture feasibility study
- [x] Norwegian language model evaluation
- [x] Commercial LLM strategy analysis and decision

### Active Research
- [ ] Trusted sources content collection and quality assessment
- [ ] RAG-ready content preparation methods
- [ ] Norwegian dementia care terminology analysis

### Future Work
- [ ] User testing with dementia patients and caregivers
- [ ] Healthcare professional validation
- [ ] Production deployment architecture

## 🚀 Getting Started

### For Research
1. **Explore existing research**: Start with `research/gdpr-research/README.md`
2. **Review decisions**: Check ADRs in `docs/adr/` for architectural context
3. **Run experiments**: Each research project has runnable experiments

### For Development (Future)
1. **Wait for research completion**: Current focus is research phase
2. **Review graduation criteria**: See `development/README.md` for requirements
3. **Follow ADR decisions**: Architecture decisions guide implementation approach

## 🤝 Contributing

### Research Contributions
- Document research questions clearly in project READMEs
- Capture findings and learnings, both positive and negative
- Reference related ADRs and cross-link research projects
- Keep experiments simple and focused

### Code Quality
- Research code can be messy - optimization for learning
- Development code must be production-ready
- All user-facing features require extensive testing

## 📖 Key Documentation

- [Architecture Decision Records](docs/adr/) - All major technical and strategic decisions
- [Key Research Questions](docs/key_questions.md) - Core questions driving the project
- [GDPR Research Findings](research/gdpr-research/README.md) - Privacy-first AI implementation research
- [Trusted Sources Research](research/trusted-sources/README.md) - Content collection and quality research

## ⚠️ Important Disclaimers

- **Not medical software**: This is research into AI assistance, not medical diagnosis or treatment
- **Not production ready**: All current work is experimental and not suitable for patient use
- **Research purpose**: Findings may inform healthcare AI but require professional validation
- **Privacy focused**: Even in research phase, Norwegian/EU data sovereignty maintained

---

*This project represents responsible exploration of AI in healthcare, prioritizing patient safety, privacy, and evidence-based approaches over rapid deployment.*