# Project: NB-Llama Chat Integration

**Start Date**: 2025-11-17
**Status**: Planning Phase
**Lead**: Johan Josok
**Estimated Duration**: 3-4 weeks

## Overview

This project integrates NB-Llama (Norwegian Language Model) with our existing dementia care AI assistant to enable conversational AI capabilities. The integration will provide Norwegian-optimized chat functionality while maintaining our privacy-first architecture and optimal Apple M2 Max performance.

## Goals & Objectives

### Primary Goals
1. **Enable Conversational AI**: Add NB-Llama chat capabilities to complement existing NB-Whisper speech recognition
2. **Norwegian Language Excellence**: Provide high-quality Norwegian conversation optimized for dementia care context
3. **Seamless Integration**: Integrate with ai-chat-ui frontend package for professional chat interface
4. **Performance Optimization**: Leverage Apple M2 Max MPS acceleration for optimal inference speed
5. **Medical Safety**: Implement Norwegian medical boundary enforcement to prevent inappropriate advice

### Success Criteria
- [ ] NB-Llama-8B model running on MPS with <3 second response times
- [ ] SSE streaming chat interface working with ai-chat-ui
- [ ] Norwegian medical boundary enforcement preventing diagnosis/treatment advice
- [ ] Next.js frontend with proper Norwegian language support
- [ ] End-to-end chat workflow from user input to model response
- [ ] Memory usage under 30GB total (including existing NB-Whisper models)

## Architecture Overview

### Technical Stack
- **Backend**: FastAPI + PyTorch + Transformers + MPS
- **Model**: NbAiLab/nb-llama-3.1-8B-Instruct
- **Frontend**: Next.js + TypeScript + ai-chat-ui
- **Device**: Apple M2 Max with 64GB unified memory
- **Streaming**: Server-Sent Events (SSE) for real-time chat

### Integration Pattern
```
User Input → Next.js Frontend → CustomProvider → FastAPI Backend → NB-Llama (MPS) → SSE Stream → Chat Interface
```

### Memory Allocation (M2 Max 64GB)
- **Existing NB-Whisper**: ~8GB (5 models)
- **NB-Llama-8B**: ~16GB (float16)
- **System + Apps**: ~10GB
- **Available**: ~30GB for processing

## Project Phases

### Phase 1: Documentation & Setup (Week 1) ✅
**Status**: Completed 2025-11-17

**Deliverables**:
- [x] ADR: NB-Llama Integration Architecture
- [x] ADR: Frontend Framework Selection (Next.js)
- [x] ADR: Chat API Design Decisions
- [x] Project roadmap documentation
- [x] Git repository setup and initial commit
- [x] Linear project with issue tracking

**Key Decisions**:
- Direct MPS integration over Ollama for consistency with NB-Whisper
- Custom Norwegian-first API design (no OpenAI compatibility layer)
- Next.js over Vite for SSR and Norwegian language support
- SSE streaming for ai-chat-ui compatibility

### Phase 2: Backend Development (Week 1-2)
**Status**: Ready to Start

**Tasks**:
1. **NB-Llama Model Integration**
   - Add NB-Llama loading to existing main.py
   - Implement same MPS device detection pattern
   - Test model loading and memory usage

2. **Chat API Development**
   - Create `/backend/app/api/chat.py`
   - Implement SSE streaming endpoint
   - Add Norwegian system prompt optimization
   - Integrate medical boundary enforcement

3. **Safety & Compliance**
   - Norwegian medical keyword detection
   - GDPR-compliant local processing validation
   - Error handling consistent with NB-Whisper patterns

4. **Backend Testing**
   - Unit tests for chat endpoints
   - Integration tests with existing NB-Whisper
   - Performance benchmarking on M2 Max

**Acceptance Criteria**:
- [ ] `POST /api/chat` endpoint functional with SSE streaming
- [ ] NB-Llama responding in Norwegian with dementia care context
- [ ] Medical boundary enforcement blocking inappropriate advice
- [ ] Response times under 3 seconds for typical queries
- [ ] Memory usage monitoring and optimization

### Phase 3: Frontend Development (Week 2-3)
**Status**: Pending Backend Completion

**Tasks**:
1. **Next.js Application Setup**
   - Create `/frontend` directory with Next.js + TypeScript
   - Install and configure ai-chat-ui package
   - Set up Tailwind CSS for styling

2. **ai-chat-ui Integration**
   - Configure CustomProvider for local backend
   - Implement Norwegian language interface
   - Test SSE streaming with chat interface

3. **Norwegian Localization**
   - Norwegian text throughout interface
   - Proper character encoding (æ, ø, å)
   - Error messages in Norwegian
   - Responsive design for various devices

4. **Frontend Testing**
   - Component testing for chat interface
   - Integration testing with backend API
   - Cross-browser compatibility testing
   - Mobile responsiveness testing

**Acceptance Criteria**:
- [ ] Chat interface displays properly in Norwegian
- [ ] Real-time streaming messages appear correctly
- [ ] Error handling with Norwegian error messages
- [ ] Responsive design for desktop and mobile
- [ ] Proper loading states and user feedback

### Phase 4: Integration & Testing (Week 3-4)
**Status**: Pending Frontend Completion

**Tasks**:
1. **End-to-End Integration**
   - Frontend-backend connectivity testing
   - SSE streaming validation across browsers
   - Norwegian language input/output testing
   - Performance testing under load

2. **Medical Safety Validation**
   - Test Norwegian medical keyword detection
   - Verify appropriate responses to medical queries
   - Validate boundary enforcement effectiveness
   - Test edge cases and corner scenarios

3. **Performance Optimization**
   - M2 Max resource utilization monitoring
   - Concurrent user testing (speech + chat)
   - Memory optimization and garbage collection
   - Response time optimization

4. **Documentation & Deployment**
   - User guide creation
   - API documentation updates
   - Deployment preparation for production migration
   - Performance benchmarks documentation

**Acceptance Criteria**:
- [ ] Full conversation workflow functional
- [ ] Norwegian language quality meets standards
- [ ] Medical boundaries effectively enforced
- [ ] Performance targets achieved (<3s responses)
- [ ] Documentation complete and accurate

## Risk Assessment & Mitigation

### High Risk
**Model Performance on M2 Max**
- *Risk*: NB-Llama-8B may be too large or slow for optimal user experience
- *Mitigation*: Performance testing early in Phase 2, quantization options available
- *Contingency*: Consider smaller NB-Llama variants if needed

**Memory Constraints**
- *Risk*: Combined models may exceed M2 Max memory capacity
- *Mitigation*: Continuous memory monitoring, model optimization
- *Contingency*: Implement model unloading/loading if needed

### Medium Risk
**ai-chat-ui Integration Complexity**
- *Risk*: SSE streaming or API compatibility issues
- *Mitigation*: Thorough analysis of ai-chat-ui requirements completed
- *Contingency*: Fallback to custom chat interface if needed

**Norwegian Language Quality**
- *Risk*: NB-Llama responses may not meet dementia care standards
- *Mitigation*: Extensive testing with Norwegian medical professionals
- *Contingency*: Fine-tuning or prompt engineering improvements

### Low Risk
**Frontend Development Timeline**
- *Risk*: Next.js learning curve may slow development
- *Mitigation*: Strong documentation and community support
- *Contingency*: Simplify frontend features if needed

## Success Metrics

### Performance Metrics
- **Response Time**: <3 seconds for 90% of queries
- **Memory Usage**: <30GB total system memory utilization
- **Concurrent Users**: Support 5+ concurrent chat sessions
- **Uptime**: >99% during development testing

### Quality Metrics
- **Norwegian Language**: Native speaker validation of responses
- **Medical Safety**: 100% blocking of inappropriate medical advice
- **User Experience**: Smooth streaming without interruptions
- **Error Rate**: <1% of requests result in errors

### Business Metrics
- **Feature Completeness**: All planned chat features functional
- **Integration Success**: Seamless workflow with existing speech features
- **Documentation Quality**: Complete technical and user documentation
- **Production Readiness**: Clear migration path to Hetzner servers

## Timeline

```
Week 1: Phase 1 (Completed) + Phase 2 Start
├── Documentation complete ✅
├── Git setup complete ✅
├── Linear project setup ⏳
└── Begin NB-Llama backend integration ⏳

Week 2: Phase 2 Completion + Phase 3 Start
├── Chat API functional
├── Backend testing complete
├── Begin Next.js frontend
└── ai-chat-ui integration

Week 3: Phase 3 Completion + Phase 4 Start
├── Frontend complete
├── Norwegian localization
├── Begin end-to-end testing
└── Performance optimization

Week 4: Phase 4 Completion
├── Integration testing complete
├── Documentation finalized
├── Performance benchmarks
└── Production deployment preparation
```

## Dependencies

### Internal Dependencies
- Existing NB-Whisper system must remain functional
- Mac M2 Max development environment
- FastAPI backend architecture

### External Dependencies
- **ai-chat-ui**: npm package for chat interface
- **NB-Llama model**: HuggingFace model availability
- **Next.js**: Frontend framework stability
- **PyTorch MPS**: Apple Silicon acceleration support

## Communication Plan

### Stakeholders
- **Primary**: Johan Josok (Product Owner/Developer)
- **Secondary**: Future team members, Norwegian medical professionals for validation

### Reporting
- **Daily**: Todo list updates and progress tracking
- **Weekly**: Phase completion reviews and milestone assessment
- **Project End**: Comprehensive documentation and handover materials

## Post-Project Considerations

### Production Migration
- **Timeline**: 1-2 months after project completion
- **Platform**: Hetzner servers with vLLM
- **Effort**: API compatibility maintained, infrastructure setup needed

### Future Enhancements
- **Voice Input Integration**: Combine NB-Whisper → NB-Llama → TTS workflow
- **Context Memory**: Persistent conversation history
- **Knowledge Base**: Integration with Norwegian dementia care literature
- **Multi-Modal**: Image understanding for medical diagrams

### Maintenance
- **Model Updates**: NB-Llama model version management
- **Performance Monitoring**: Ongoing optimization opportunities
- **User Feedback**: Continuous improvement based on actual usage
- **Security Updates**: Regular dependency and framework updates

## References

### Technical Documentation
- [NB-Llama Integration Architecture ADR](../adr/2025-11-17-nb-llama-integration-architecture.md)
- [Frontend Framework Selection ADR](../adr/2025-11-17-frontend-framework-selection.md)
- [Chat API Design Decisions ADR](../adr/2025-11-17-chat-api-design-decisions.md)
- [Development Principles](../development-principles.md)

### External Resources
- [ai-chat-ui Documentation](https://github.com/git-johan/ai-chat-ui)
- [NB-Llama Model](https://huggingface.co/NbAiLab/nb-llama-3.1-8B-Instruct)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Last Updated**: 2025-11-17
**Next Review**: Weekly during active development