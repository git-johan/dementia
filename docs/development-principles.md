# Development Principles – AI-assistent for demensomsorg

This document establishes the high-level architectural principles and development approach for our dementia care AI assistant. These principles guide all technical decisions and ensure consistency across the project's evolution from prototype to production.

---

## 🎯 Core Development Principles

### Separation of Concerns
Clear boundaries between business domains and responsibilities. Each component handles one specific aspect of the system without bleeding into others. This makes the codebase easier to understand, test, and maintain.

### Code-Reusability
Apply DRY (Don't Repeat Yourself) principles consistently. Create shared components, utilities, and patterns that can be used across domains. Build once, use many times.

### Modularized Approach
Domain-driven development that creates clear modules for both human developers and AI assistants to understand. Each domain is self-contained with well-defined interfaces to other domains.

### Medical Boundary Enforcement
Code-level safeguards that prevent the system from ever giving medical advice, diagnoses, or health recommendations. These boundaries are enforced at the architectural level, not just through prompts or documentation.

### Observable and Debuggable
Comprehensive logging, monitoring, and debugging capabilities specifically designed for research and development. During development, we want to see failures clearly to solve the problems, not mask them.

### Leverage Platform Capabilities
Use existing device features and native apps rather than rebuilding functionality. Integrate with platform-optimized capabilities (iOS Voice Memos, Android Recorder) to achieve better quality results with less development complexity.

---

## 🇳🇴 Norwegian-First Architecture

### Language Models Drive Design
Our architecture is built around Norwegian language models (NB-Whisper, NB-Llama) rather than international alternatives. This decision impacts:
- Data processing pipelines optimized for Norwegian speech patterns
- Local hosting requirements for quality Norwegian models
- Integration patterns between Norwegian-trained models

### Local-First Processing
All language processing happens locally or within Norwegian/EU infrastructure:
- No dependency on US-based APIs for core functionality
- Reduced latency for Norwegian language processing
- Better quality results from models trained on Norwegian data
- Complete data sovereignty and GDPR compliance
- Device-native audio processing leverages platform optimization for Norwegian speech patterns

### Integration Patterns
Clean interfaces between Norwegian language models:
- NB-Whisper (speech-to-text) → structured text data
- NB-Llama (text processing) → contextual understanding
- Consistent data formats between Norwegian language components

### Performance Considerations
Optimize for Norwegian speech and text processing:
- Model sizing appropriate for target hardware (Mac M2, production servers)
- Efficient Norwegian tokenization and embedding strategies
- Response times suitable for dementia care scenarios (under 3 seconds)

---

## 🔒 Privacy & Security Patterns

### Health Data Handling
Treat all user data as sensitive health information under GDPR Article 9:
- Explicit consent required for all data processing
- Purpose limitation - data only used for documented care assistance
- Data minimization - collect only what's necessary
- User control - ability to view, correct, and delete all data

### Local-First Data Flow
Design data flows to keep information as local as possible:
- Processing on user's device or local infrastructure preferred
- Cloud services only when necessary and with appropriate safeguards
- No transfer to non-adequate countries (USA, etc.)
- Transparent data location and processing documentation

### Secure Patient-Caregiver Data Sharing
Enable safe information sharing between patients and caregivers:
- Explicit permission model for data sharing
- Role-based access controls
- Audit logging of all data access
- Easy revocation of sharing permissions

### No External Dependencies for Core Processing
Core speech and text processing independent of external APIs:
- Self-hosted Norwegian language models
- Local storage for conversation history and medical information
- External APIs only for non-sensitive features (if any)

---

## 🏗️ Domain-Driven Architecture

### Memory Domain
**Responsibility:** Storage, persistence, and ingestion of information from all sources

**Handles:**
- Voice recordings and transcriptions
- Medical documents and notes (OCR processing)
- Structured data from forms and questionnaires
- Conversation history between all parties
- Visual content (medication photos, handwritten notes)
- Approved web content (with healthcare provider authorization)

**Technical Concerns:**
- Database design and data modeling
- File storage and retrieval systems
- Data backup and recovery processes
- API endpoints for data ingestion

### Context Domain
**Responsibility:** Retrieval, relevance determination, and situational awareness

**Handles:**
- Determining what information is relevant for current conversation
- RAG (Retrieval-Augmented Generation) query processing
- Embedding and vector similarity search
- Context ranking and filtering
- Temporal relevance (recent vs historical information)

**Technical Concerns:**
- Vector database management
- Embedding model optimization
- Search and retrieval algorithms
- API endpoints for context queries

### Conversation Domain
**Responsibility:** AI dialogue flow and interaction management

**Handles:**
- Natural language understanding and generation
- Conversation state management
- Medical boundary enforcement during conversations
- Response generation and formatting
- Multi-turn dialogue coherence

**Technical Concerns:**
- LLM integration and prompt management
- Conversation state persistence
- Safety filters and boundary checks
- API endpoints for chat functionality

### User Interface Domain
**Responsibility:** Presentation layer and user interaction

**Handles:**
- Web application interface (mobile-first)
- File upload and management interfaces for device recordings
- Audio file preview and playback controls
- Text display and editing capabilities optimized for dementia care
- Integration with device native apps and file systems
- User authentication and session management

**Technical Concerns:**
- Frontend framework and responsive design
- File handling APIs for multiple audio formats (M4A, AAC, MP3, WAV)
- Mobile-optimized file selection and preview capabilities
- User experience for dementia care scenarios with familiar device recording workflows
- API integration with other domains

### Cross-Cutting Concerns
**Shared across all domains:**
- **API Patterns:** Consistent REST/GraphQL conventions, error handling, validation
- **Authentication:** Unified user authentication and authorization
- **Logging:** Structured logging for debugging and research analysis
- **Infrastructure:** Deployment, monitoring, and scaling patterns
- **Data Consistency:** Transaction boundaries and data synchronization

---

## 📈 Scalability & Deployment Evolution

### Phase 1: Mac M2 Prototype (0-30 users)
**Timeline:** Months 1-3
**Architecture:** All domains running on single Mac M2 machine
- Monolithic deployment for rapid development and testing
- Local file storage and SQLite databases
- Development-focused logging and debugging
- Zero infrastructure costs

### Phase 2: Single Server Deployment (100+ users)
**Timeline:** Months 4-6
**Architecture:** Domains as separate services on dedicated server
- Domain separation with internal API boundaries
- Shared database with domain-specific schemas
- Professional logging and monitoring
- Basic load balancing and redundancy

### Phase 3: Distributed Architecture (500+ users)
**Timeline:** Months 6+
**Architecture:** Independent scaling per domain
- Microservices with separate databases per domain
- Distributed file storage and caching
- Auto-scaling based on domain-specific metrics
- Full production monitoring and alerting

### Migration Patterns
**Clean evolution between phases:**
- Database migration scripts for schema changes
- API versioning to support gradual transitions
- Data consistency checks during architecture changes
- Rollback procedures for each migration step

---

## ⚡ Development Workflow Principles

### Research-Driven Development
Systematic approach to answering the 46 key research questions identified in our planning:
- Each feature development addresses specific research questions
- Clear success criteria before implementation begins
- Documentation of findings for future reference

### Prototype-First Validation
Validate core assumptions before expanding features:
- Build minimal viable prototypes to test specific hypotheses
- Real-world testing in actual dementia care environments
- Data collection and analysis before feature expansion

### Clear Documentation of Decisions
Document architectural decisions and research findings:
- Decision records for all major architectural choices
- Research logs with quantitative results and conclusions
- Code documentation focused on domain boundaries and interfaces

### Modular Testing Approach
Testing strategy aligned with domain boundaries:
- Unit tests within each domain
- Integration tests for cross-domain communication
- End-to-end tests for complete user workflows
- Performance testing for Norwegian language model integration

### Development-Focused Error Visibility
During research and development phases, prioritize visibility over user experience:
- Detailed error logging and stack traces
- Clear failure indicators in development interfaces
- Research-focused metrics and debugging information
- No masking of failures that could hide problems we need to solve

### Platform Integration Strategy
Work with device capabilities rather than against them:
- Leverage existing native recording apps for superior audio quality
- Integrate with platform-optimized features instead of rebuilding them
- Use device file systems and sharing mechanisms
- Align with user's existing workflows and familiar interfaces

### Quality-First Research Approach
Prioritize data quality to ensure reliable research conclusions:
- Use professional audio sources (device recording apps) over convenience alternatives
- Establish high-quality baselines for accurate model comparison
- Design testing protocols that eliminate quality variables
- Focus development effort on core research questions rather than peripheral functionality

---

## 🚀 Next Steps

This document establishes our high-level approach. The next step is creating a detailed technical specification document that covers:
- Specific technology choices (frameworks, libraries, tools)
- Implementation details for each domain
- API specifications and data formats
- Development environment setup and deployment procedures

The current priority is building the "Lyd til tekst" prototype to validate our voice-to-text pipeline and answer key research questions about mobile microphone quality and Norwegian speech recognition performance.