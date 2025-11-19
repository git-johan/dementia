# ADR: NB-Llama Integration Architecture

**Date**: 2025-11-17
**Status**: Accepted
**Deciders**: Johan Josok

## Context

We need to integrate NB-Llama (Norwegian Language Model) into our existing dementia care AI assistant to enable conversational AI capabilities. The system already has a proven NB-Whisper implementation running on Apple M2 Max with MPS (Metal Performance Shaders) acceleration. We need to decide how to integrate NB-Llama while maintaining optimal performance, privacy compliance, and architectural consistency.

## Decision Drivers

- **Performance Consistency**: Leverage proven MPS acceleration from existing NB-Whisper setup
- **Norwegian Language Quality**: Optimal Norwegian conversation capabilities for dementia care
- **Privacy & GDPR Compliance**: All processing must remain local on Mac M2 Max
- **Architectural Consistency**: Maintain patterns established with successful NB-Whisper implementation
- **Development Simplicity**: Minimize external dependencies and complexity
- **Memory Efficiency**: Optimal utilization of M2 Max 64GB unified memory
- **Future Production Migration**: Easy path to Hetzner servers with vLLM

## Options Considered

### Option 1: Ollama Integration (REJECTED)

**Approach**: Use Ollama to manage NB-Llama with custom Modelfile

**Pros**:
- Simplified model management
- Built-in OpenAI-compatible API
- Easy deployment and updates
- Good community support

**Cons**:
- **External dependency**: Adds service management complexity
- **Inconsistent architecture**: Different from proven NB-Whisper direct approach
- **Model availability uncertainty**: NB-Llama may not be available in Ollama registry
- **Abstraction overhead**: Additional layer between our code and the model
- **Less control**: Limited ability to customize model behavior and safety boundaries
- **API compatibility layer**: Requires OpenAI format compatibility instead of native implementation

### Option 2: Direct MPS Integration with Transformers (CHOSEN)

**Approach**: Extend existing NB-Whisper architecture pattern to include NB-Llama

**Implementation**:
```python
# Add to existing main.py global model loading
from transformers import AutoModelForCausalLM, AutoTokenizer

nb_llama_model = None
nb_llama_tokenizer = None

async def load_global_models():
    # Existing NB-Whisper loading code...

    # Add NB-Llama using same MPS device detection
    logger.info("Loading NB-Llama-8B model...")
    nb_llama_tokenizer = AutoTokenizer.from_pretrained("NbAiLab/nb-llama-3.1-8B-Instruct")
    nb_llama_model = AutoModelForCausalLM.from_pretrained(
        "NbAiLab/nb-llama-3.1-8B-Instruct",
        device_map="mps",  # Same device as NB-Whisper
        torch_dtype=torch.float16
    )
    logger.info("✓ NB-Llama model loaded on Apple M2 Max GPU (MPS)")
```

**Pros**:
- **Architectural consistency**: Same pattern as successful NB-Whisper implementation
- **Optimal performance**: Direct MPS access without abstraction layers
- **Full control**: Complete control over model behavior, safety, and Norwegian optimization
- **Memory sharing**: Efficient unified memory usage with NB-Whisper models
- **No external dependencies**: Pure PyTorch/Transformers stack
- **Easy debugging**: Direct access to model internals and PyTorch debugging tools
- **Custom safety**: Norwegian-specific medical boundary enforcement
- **Production migration**: Same vLLM migration path as planned for NB-Whisper

**Cons**:
- **Manual model management**: Need to handle model loading, memory management manually
- **Custom API development**: Need to build streaming API from scratch
- **More implementation work**: Requires building chat API, streaming, error handling

### Option 3: Hybrid Approach (REJECTED)

**Approach**: Use Ollama for development, direct integration for production

**Rejection Reasons**:
- **Inconsistent development/production environments**: Different behavior and debugging challenges
- **Additional complexity**: Need to maintain two integration approaches
- **Testing complications**: Can't fully validate production behavior in development
- **Migration risk**: Potential issues when switching from Ollama to direct integration

## Decision

**We choose Option 2: Direct MPS Integration with Transformers**

### Primary Rationale

**Architectural Consistency**:
- Leverages proven NB-Whisper MPS implementation (currently working optimally)
- Same device detection, error handling, and logging patterns
- Consistent global model management approach
- Unified memory management for both speech and text models

**Performance Optimization**:
- Direct Metal Performance Shaders (MPS) access on Apple M2 Max 38-core GPU
- No abstraction layer overhead (Ollama would add HTTP API layer)
- Optimal memory utilization of 64GB unified memory
- Shared GPU context between NB-Whisper and NB-Llama models

**Norwegian Language & Safety**:
- Full control over Norwegian-specific system prompts
- Custom medical boundary enforcement for dementia care context
- Direct access to model outputs for quality validation
- No dependency on external service Norwegian language support

**Development & Production Alignment**:
- Same codebase for development (Mac M2) and production (Hetzner + vLLM)
- Consistent debugging and profiling capabilities
- No service management complexity (no Ollama daemon to manage)
- Direct PyTorch integration for advanced optimizations

## Implementation Architecture

### Model Loading Strategy

```python
# Global model storage (consistent with NB-Whisper pattern)
nb_whisper_models = {}  # Existing: 5 models (tiny/base/small/medium/large)
nb_llama_model = None
nb_llama_tokenizer = None

# Memory allocation target:
# - NB-Whisper models: ~8GB total
# - NB-Llama-8B (float16): ~16GB
# - System overhead: ~10GB
# - Available for processing: ~30GB
```

### Device Management

```python
# Same device detection as NB-Whisper
if torch.backends.mps.is_available():
    device = "mps"
    device_name = "Apple M2 Max GPU (MPS)"
elif torch.cuda.is_available():
    device = "cuda"
    device_name = f"CUDA GPU ({torch.cuda.get_device_name()})"
else:
    device = "cpu"
    device_name = "CPU"
```

### API Architecture

```python
# New chat API endpoint
@router.post("/api/chat")
async def chat_stream(request: ChatRequest):
    # Direct model inference with MPS
    # SSE streaming compatible with ai-chat-ui
    # Norwegian safety boundary enforcement
```

### Safety & Privacy Layer

```python
# Norwegian medical boundary detection
MEDICAL_KEYWORDS_NO = [
    "diagnose", "medisin", "behandling", "dosering",
    "sykdom", "symptom", "kurere", "resept"
]

# Local processing ensures GDPR Article 9 compliance
# No external API calls for core chat functionality
```

## Consequences

### Positive

- **Optimal Apple Silicon Performance**: Full utilization of M2 Max GPU capabilities
- **Architectural Consistency**: Same patterns as proven NB-Whisper implementation
- **Norwegian Language Quality**: Direct control over Norwegian conversation optimization
- **Privacy Compliance**: All processing local, no external dependencies
- **Development Efficiency**: Familiar PyTorch patterns, easy debugging and testing
- **Memory Efficiency**: Optimal unified memory usage across speech and text models
- **Production Ready**: Same migration path to Hetzner + vLLM as NB-Whisper

### Negative

- **Implementation Overhead**: More code to write compared to Ollama integration
- **Manual Model Management**: Need to handle loading, memory monitoring ourselves
- **Custom API Development**: Build streaming chat API from scratch
- **Startup Time**: Additional model loading time (estimated +30-60 seconds)

### Neutral

- **Service Management**: No additional services to manage (no Ollama daemon)
- **External Dependencies**: Maintains current dependency profile (PyTorch/Transformers only)

## Implementation Timeline

**Phase 1 (Week 1)**: Backend Implementation
- Add NB-Llama loading to main.py
- Create chat.py with SSE streaming
- Implement Norwegian safety boundaries
- Update health/capabilities endpoints

**Phase 2 (Week 2)**: Frontend Integration
- Create Next.js app with ai-chat-ui
- Configure CustomProvider for local backend
- Norwegian language interface

**Phase 3 (Week 3)**: Testing & Validation
- End-to-end chat functionality
- Performance benchmarking
- Norwegian language quality validation
- Medical boundary enforcement testing

## Future Considerations

**Production Migration (Months 2-3)**:
- Same vLLM migration strategy as planned for NB-Whisper
- Consistent API interface (no frontend changes required)
- Unified model serving infrastructure

**Performance Optimization**:
- Model quantization for memory efficiency
- Batch processing for multiple concurrent users
- GPU memory monitoring and management

**Norwegian Language Enhancement**:
- Fine-tuning on dementia care specific conversations
- Context-aware response optimization
- Integration with curated medical knowledge base

## References

- LLM Hosting Architecture ADR: `/docs/adr/2025-11-14-llm-hosting-architecture.md`
- Development Principles: `/docs/development-principles.md`
- Current NB-Whisper Implementation: `/Users/johanjosok/Documents/Code/dementia/backend/app/main.py:27-84`
- ai-chat-ui Analysis: Research conducted 2025-11-17