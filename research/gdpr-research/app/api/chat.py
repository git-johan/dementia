"""
Chat API with ai-chat-ui compatible SSE streaming for NB-Llama integration
"""

import json
import logging
from typing import List

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import torch

# Note: Import global models at runtime to avoid circular imports

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["chat"])

# Norwegian medical keywords for boundary enforcement
MEDICAL_KEYWORDS_NO = [
    "diagnose", "diagnostiser", "medisin", "medikament", "pille", "tablet",
    "behandling", "behandle", "dosering", "dose", "mg", "gram",
    "sykdom", "symptom", "kurere", "helbrede", "resept", "legemiddel",
    "operasjon", "kirurgi", "undersøkelse", "prøve", "blodprøve",
    "smerter", "vondt", "feber", "infeksjon", "virus", "bakterie"
]

SAFETY_RESPONSE_NO = """
Beklager, jeg kan ikke gi medisinske råd, diagnoser eller behandlingsanbefalinger.
Dette er utenfor mine grenser som AI-assistent.

Jeg kan hjelpe med:
• Generell informasjon om demensomsorg
• Organisering av daglige gjøremål
• Minnetekniker og strategier
• Kommunikasjonstips
• Aktiviteter og stimulering

For medisinske spørsmål, vennligst kontakt lege eller helsepersonell.
"""


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Chat request model for Norwegian dementia care AI"""
    messages: List[ChatMessage] = []
    prompt: str = ""
    system_prompt: str = ""
    user_prompt: str = ""
    model_name: str = ""  # Ollama model name (e.g., "llama3.1:8b", "mistral:7b", etc.)
    temperature: float = 0.7
    max_tokens: int = 2000


def check_medical_boundary(messages: List[ChatMessage] = None, prompt: str = "", user_prompt: str = "") -> tuple[bool, str]:
    """
    Check if conversation contains medical keywords requiring boundary enforcement

    Returns:
        (is_safe, safety_response)
    """

    # Determine what text to check
    text_to_check = ""
    if user_prompt:
        text_to_check = user_prompt.lower()
    elif prompt:
        text_to_check = prompt.lower()
    elif messages:
        # Get the latest user message
        latest_message = messages[-1].content.lower()
        text_to_check = latest_message
    else:
        return True, ""

    # Check for medical keywords
    for keyword in MEDICAL_KEYWORDS_NO:
        if keyword in text_to_check:
            logger.warning(f"Medical boundary triggered by keyword: {keyword}")
            return False, SAFETY_RESPONSE_NO

    return True, ""


def build_norwegian_prompt(messages: List[ChatMessage]) -> str:
    """
    Build conversation prompt optimized for Norwegian dementia care
    Modified for GGUF instruct model - uses simple completion format
    """

    if not messages:
        return ""

    # Get the latest user message
    latest_message = messages[-1].content

    # Use simpler completion format without special tokens
    prompt = f"""Du er en støttende norsk assistent som hjelper med demensomsorg. Du svarer alltid på norsk og gir praktiske råd om omsorg, aktiviteter og kommunikasjon. Du gir aldri medisinske diagnoser.

Spørsmål: {latest_message}

Svar:"""

    return prompt



@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint for Norwegian dementia care AI
    """

    try:
        prompt_info = f"prompt={bool(request.prompt)}" if request.prompt else f"{len(request.messages)} messages"
        logger.info(f"Chat request received: {prompt_info}")

        # Import Ollama client at runtime to avoid circular imports
        import app.main
        ollama_client = app.main.ollama_client
        default_ollama_model = app.main.ollama_model

        # Use provided model name or default to global setting
        selected_model = request.model_name if request.model_name else default_ollama_model

        if ollama_client is None:
            raise HTTPException(
                status_code=503,
                detail="Ollama is not available. Please ensure Ollama is running and the model is downloaded."
            )

        # Check medical boundaries
        is_safe, safety_response = check_medical_boundary(request.messages, request.prompt, request.user_prompt)
        if not is_safe:
            return {
                "choices": [{"message": {"content": safety_response}}],
                "model": selected_model
            }

        # Convert messages to Ollama format or use direct prompts
        ollama_messages = []

        # Handle system prompt and user prompt separately
        if request.system_prompt or request.user_prompt:
            # Check if this is a completion model (non-instruct)
            is_completion_model = "normistral" in selected_model.lower() and "instruct" not in selected_model.lower()

            if is_completion_model:
                # For completion models, format as a single completion prompt
                completion_prompt = ""
                if request.system_prompt and request.user_prompt:
                    completion_prompt = f"{request.system_prompt}\n\nSpørsmål: {request.user_prompt}\n\nSvar:"
                elif request.user_prompt:
                    completion_prompt = f"Spørsmål om demensomsorg: {request.user_prompt}\n\nSvar:"
                elif request.system_prompt:
                    completion_prompt = request.system_prompt

                ollama_messages.append({
                    "role": "user",
                    "content": completion_prompt
                })
            else:
                # For instruction models, use normal system/user format
                if request.system_prompt:
                    ollama_messages.append({
                        "role": "system",
                        "content": request.system_prompt
                    })
                if request.user_prompt:
                    ollama_messages.append({
                        "role": "user",
                        "content": request.user_prompt
                    })
        elif request.prompt:
            # Use single prompt as user message
            ollama_messages.append({
                "role": "user",
                "content": request.prompt
            })
        elif request.messages:
            # Convert messages to Ollama format
            for msg in request.messages:
                ollama_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        else:
            # Default fallback
            ollama_messages.append({
                "role": "user",
                "content": "Hei, kan du hjelpe meg?"
            })

        logger.info(f"Generating complete response with Ollama {selected_model} (temp={request.temperature}, max_tokens={request.max_tokens})")

        # Use Ollama's chat API for complete response
        response = ollama_client.chat(
            model=selected_model,
            messages=ollama_messages,
            stream=False,
            options={
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            }
        )

        # Debug: Log the raw response structure for troubleshooting
        logger.info(f"DEBUG: Raw Ollama response for {selected_model}: {response}")

        # Extract the response text
        response_content = response["message"]["content"]
        logger.info(f"DEBUG: Extracted content for {selected_model}: '{response_content}' (len={len(response_content)})")

        return {
            "choices": [{"message": {"content": response_content}}],
            "model": selected_model
        }

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Intern serverfeil: {str(e)}"
        )


# Health check extension for chat functionality
@router.get("/chat/health")
async def chat_health():
    """Check chat functionality health"""

    # Import Ollama client at runtime to avoid circular imports
    import app.main
    ollama_client = app.main.ollama_client
    ollama_model = app.main.ollama_model

    ollama_available = ollama_client is not None

    return {
        "status": "healthy" if ollama_available else "degraded",
        "ollama_available": ollama_available,
        "ollama_model": ollama_model if ollama_available else None,
        "medical_boundaries": "active",
        "streaming": "enabled"
    }