# ADR: Chat API Design Decisions

**Date**: 2025-11-17
**Status**: Accepted
**Deciders**: Johan Josok

## Context

We need to design the chat API that will serve as the interface between our NB-Llama model and the ai-chat-ui frontend. The API must support real-time streaming responses, Norwegian language optimization, medical boundary enforcement, and seamless integration with the existing NB-Whisper architecture. Based on analysis of the ai-chat-ui package, we understand the required request/response formats and streaming protocols.

## Decision Drivers

- **ai-chat-ui Compatibility**: Must work seamlessly with ai-chat-ui's CustomProvider
- **Streaming Performance**: Real-time token-by-token streaming for responsive chat experience
- **Norwegian Language Priority**: Optimized for Norwegian dementia care conversations
- **Medical Safety**: Enforce boundaries against medical advice/diagnosis
- **Architectural Consistency**: Align with existing NB-Whisper API patterns
- **Privacy Compliance**: GDPR Article 9 compliance for health data
- **Simple Integration**: Avoid unnecessary complexity or compatibility layers

## Options Considered

### Option 1: OpenAI-Compatible API (REJECTED)

**Approach**: Implement OpenAI Chat Completions API format

**Example**:
```json
POST /v1/chat/completions
{
  "model": "nb-llama-8b",
  "messages": [...],
  "stream": true
}

Response:
data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","choices":[{"delta":{"content":"Hello"}}]}
```

**Pros**:
- Industry standard format
- Works with many tools and libraries
- Well-documented specification
- Future compatibility with other AI tools

**Cons**:
- **Unnecessary complexity**: We don't need full OpenAI compatibility
- **Not Norwegian-first**: Designed for English-centric use cases
- **Additional overhead**: Extra fields and formatting we don't use
- **Against project principles**: Adds dependency on US API design patterns
- **Implementation burden**: More code to maintain compatibility layer

### Option 2: Custom Norwegian-First API (CHOSEN)

**Approach**: Design API specifically for Norwegian dementia care use case

**Format**:
```json
POST /api/chat
{
  "messages": [
    {"role": "user", "content": "Hva er demens?"},
    {"role": "assistant", "content": "Demens er..."}
  ],
  "temperature": 0.7,
  "max_tokens": 2000,
  "stream": true
}

Streaming Response (SSE):
data: {"choices":[{"delta":{"content":"Demens"}}]}
data: {"choices":[{"delta":{"content":" er"}}]}
data: [DONE]

Non-streaming Response:
{
  "choices": [
    {"message": {"content": "Complete response here"}}
  ]
}
```

**Pros**:
- **ai-chat-ui compatible**: Works perfectly with CustomProvider's flexible content parsing
- **Simple implementation**: Minimal required fields, focus on core functionality
- **Norwegian optimized**: Can customize response format for Norwegian language needs
- **Medical safety integration**: Easy to add Norwegian medical keyword detection
- **Consistent with existing architecture**: Similar patterns to NB-Whisper API
- **Future flexibility**: Can evolve API based on actual usage patterns

**Cons**:
- **Custom format**: Not compatible with standard AI tools (not a concern for our use case)
- **Limited ecosystem**: Can't leverage existing OpenAI-compatible tools

### Option 3: Hybrid Approach (REJECTED)

**Approach**: Support both OpenAI format and custom format

**Rejection Reasons**:
- **Unnecessary complexity**: Doubles the implementation burden
- **Testing overhead**: Need to test both API formats
- **Maintenance burden**: Two APIs to maintain and document
- **No clear benefit**: ai-chat-ui works fine with custom format

## Decision

**We choose Option 2: Custom Norwegian-First API**

### Primary Rationale

**ai-chat-ui Compatibility**:
- ai-chat-ui's CustomProvider supports flexible content field resolution
- Works with both SSE format (`data: {...}`) and raw JSON
- No need for full OpenAI compatibility - CustomProvider handles various formats
- Proven to work with custom backends

**Norwegian Language Priority**:
- API can be optimized specifically for Norwegian dementia care context
- Medical boundary enforcement using Norwegian keywords
- Response formatting optimized for Norwegian conversation patterns
- No need to conform to English-centric API design

**Simplicity and Maintainability**:
- Minimal implementation overhead
- Focus on core functionality needed for our use case
- Easy to extend with Norwegian-specific features
- Consistent with our direct MPS integration approach

**Medical Safety Integration**:
```python
# Norwegian medical keyword detection
MEDICAL_KEYWORDS_NO = [
    "diagnose", "diagnostiser", "medisin", "medikament",
    "behandling", "behandle", "dosering", "dose",
    "sykdom", "symptom", "kurere", "helbrede", "resept"
]

SAFETY_RESPONSE_NO = """
Beklager, jeg kan ikke gi medisinske råd, diagnoser eller behandlingsanbefalinger.
Dette er utenfor mine grenser som AI-assistent.

Jeg kan hjelpe med:
- Generell informasjon om demensomsorg
- Organisering av daglige gjøremål
- Minnetekniker og strategier
- Kommunikasjonstips

For medisinske spørsmål, vennligst kontakt lege eller helsepersonell.
"""
```

## API Implementation Specification

### Endpoint Design

```python
# Main chat endpoint
POST /api/chat

# Health check (extended from existing)
GET /health

# Capabilities (extended from existing)
GET /api/processors/capabilities
```

### Request Format

```python
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 2000
    stream: bool = True
```

### Response Format

**Streaming (SSE)**:
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

data: {"choices":[{"delta":{"content":"Hei"}}]}
data: {"choices":[{"delta":{"content":" der"}}]}
data: [DONE]
```

**Non-streaming**:
```json
{
  "choices": [
    {
      "message": {
        "content": "Complete response text here"
      }
    }
  ],
  "model": "nb-llama-8b",
  "processing_time_ms": 1500
}
```

### Error Response Format

```json
{
  "error": {
    "message": "Feilmelding på norsk",
    "type": "medical_boundary_violation",
    "code": "MEDICAL_ADVICE_BLOCKED"
  }
}
```

## Implementation Architecture

### Streaming Implementation

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json
import asyncio

async def stream_chat_response(
    messages: List[ChatMessage],
    temperature: float,
    max_tokens: int
) -> AsyncGenerator[str, None]:
    """Stream NB-Llama responses in ai-chat-ui compatible format."""

    # Build Norwegian conversation prompt
    prompt = build_norwegian_prompt(messages)

    # Check medical boundaries
    is_safe, safety_response = check_medical_boundary(messages)
    if not is_safe:
        yield f'data: {{"choices":[{{"delta":{{"content":"{safety_response}"}}}}]}}\n\n'
        yield "data: [DONE]\n\n"
        return

    # Generate streaming response using global NB-Llama model
    inputs = nb_llama_tokenizer.encode(prompt, return_tensors="pt").to("mps")

    with torch.no_grad():
        for new_token_id in nb_llama_model.generate(
            inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
            pad_token_id=nb_llama_tokenizer.eos_token_id
        ):
            token_text = nb_llama_tokenizer.decode([new_token_id], skip_special_tokens=True)

            # Format as SSE for ai-chat-ui
            sse_data = {"choices": [{"delta": {"content": token_text}}]}
            yield f"data: {json.dumps(sse_data)}\n\n"

    yield "data: [DONE]\n\n"

@router.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with SSE streaming."""
    try:
        if request.stream:
            return StreamingResponse(
                stream_chat_response(request.messages, request.temperature, request.max_tokens),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        else:
            # Non-streaming fallback
            response_text = await generate_complete_response(request.messages, request.temperature, request.max_tokens)
            return {
                "choices": [{"message": {"content": response_text}}],
                "model": "nb-llama-8b"
            }

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Intern serverfeil")
```

### Norwegian System Prompt

```python
def build_norwegian_prompt(messages: List[ChatMessage]) -> str:
    """Build conversation prompt optimized for Norwegian dementia care."""

    system_prompt = """
Du er en AI-assistent for demensomsorg i Norge. Du skal hjelpe brukere med informasjon og støtte,
men aldri gi medisinske råd eller diagnoser.

Dine oppgaver:
- Gi generell informasjon om demensomsorg
- Hjelpe med organisering av daglige gjøremål
- Foreslå minnetekniker og strategier
- Gi kommunikasjonstips
- Være empatisk og støttende

Du må ikke:
- Gi medisinske råd eller diagnoser
- Anbefale medisiner eller behandlinger
- Erstatte profesjonell helsehjelp

Svar alltid på norsk (bokmål) med en varm og forståelsesfull tone.
"""

    conversation = f"System: {system_prompt}\n\n"

    for message in messages:
        role = "Human" if message.role == "user" else "Assistant"
        conversation += f"{role}: {message.content}\n\n"

    conversation += "Assistant:"
    return conversation
```

## Integration with Existing Architecture

### Health Check Extension

```python
# Extend existing health check in main.py
async def health_check():
    # Existing NB-Whisper checks...

    # Add NB-Llama status
    nb_llama_status = "ready" if nb_llama_model else "not_loaded"

    services.update({
        "nb_llama_8b": nb_llama_status,
        "chat_api": "ready" if nb_llama_model else "degraded"
    })
```

### Capabilities Extension

```python
# Extend existing capabilities endpoint
async def get_processor_capabilities():
    # Existing NB-Whisper processors...

    # Add chat model info
    chat_processor = {
        "name": "nb-llama-8b",
        "type": "chat",
        "version": "1.0.0",
        "description": "Norwegian Language Model for dementia care conversations",
        "language": "Norwegian (Bokmål)",
        "model_source": "NbAiLab/nb-llama-3.1-8B-Instruct",
        "status": "ready" if nb_llama_model else "not_loaded",
        "capabilities": ["streaming", "norwegian", "medical_boundaries"]
    }

    processors.append(chat_processor)
```

## Consequences

### Positive

- **Perfect ai-chat-ui Integration**: CustomProvider handles our format seamlessly
- **Norwegian Language Optimization**: API designed specifically for Norwegian dementia care
- **Simple Implementation**: Minimal code overhead, focus on core functionality
- **Medical Safety**: Built-in Norwegian keyword detection and boundary enforcement
- **Consistent Architecture**: Follows same patterns as successful NB-Whisper implementation
- **Performance**: Direct streaming without unnecessary format conversion overhead
- **Future Flexibility**: Easy to extend with Norwegian-specific features

### Negative

- **No OpenAI Tool Compatibility**: Can't use existing OpenAI-compatible tools (not needed for our use case)
- **Custom Documentation**: Need to document our API format (minimal effort)

### Neutral

- **Testing**: Need to test against ai-chat-ui (required regardless of API format)
- **Frontend Configuration**: CustomProvider needs endpoint configuration (same for any API)

## Future Enhancements

**Norwegian Language Features**:
- Sentiment analysis for detecting distress or confusion
- Norwegian medical terminology recognition improvements
- Regional dialect support (Bokmål vs Nynorsk)

**Medical Safety Enhancements**:
- Context-aware medical boundary detection
- Integration with Norwegian health terminology databases
- Escalation protocols for emergency situations

**Performance Optimizations**:
- Response caching for common Norwegian phrases
- Model quantization for faster inference
- Batch processing for multiple concurrent users

## References

- ai-chat-ui Package Analysis: Conducted 2025-11-17
- NB-Llama Integration Architecture ADR: `/docs/adr/2025-11-17-nb-llama-integration-architecture.md`
- Development Principles: `/docs/development-principles.md`
- Privacy Legal Risks Analysis: `/docs/technical-research/2025-11-12-privacy-legal-risks.md`