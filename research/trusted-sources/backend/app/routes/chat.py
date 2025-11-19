import time
import logging
from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse, ErrorResponse
from app.services.openai_service import openai_service

# Set up logging
logger = logging.getLogger(__name__)

chat_router = APIRouter()

@chat_router.post("/chat", response_model=ChatResponse)
async def chat_with_gpt5(request: ChatRequest):
    """
    Chat endpoint for Norwegian dementia care conversations using GPT-5.

    Args:
        request: ChatRequest containing the user message

    Returns:
        ChatResponse with GPT-5 response

    Raises:
        HTTPException: If message is empty or GPT-5 API fails
    """
    try:
        # Validate message
        if not request.message or not request.message.strip():
            logger.warning(f"Empty message received from user {request.user_id}")
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )

        logger.info(f"Processing chat request for user {request.user_id}")

        # Get response from GPT-5
        response_text = openai_service.get_chat_response(
            user_message=request.message.strip(),
            user_id=request.user_id
        )

        # Return response
        return ChatResponse(
            response=response_text,
            timestamp=int(time.time() * 1000),  # Milliseconds timestamp
            user_id=request.user_id
        )

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise

    except Exception as error:
        # Log and return error response (clear error logging as requested)
        error_msg = f"Failed to get response from GPT-5: {str(error)}"
        logger.error(f"Chat endpoint error for user {request.user_id}: {error_msg}")

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get response from GPT-5",
                "details": str(error)
            }
        )