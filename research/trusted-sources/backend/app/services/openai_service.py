import os
import logging
from openai import OpenAI
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not found!")
            raise ValueError("OPENAI_API_KEY must be set")

        logger.info(f"Initializing OpenAI client with API key: {api_key[:10]}...")
        self.client = OpenAI(api_key=api_key)
        self.norwegian_dementia_care_instructions = """You are a compassionate assistant helping with dementia care questions in Norwegian.

Respond in Norwegian with empathy and understanding. Provide supportive, helpful information about dementia care challenges.

IMPORTANT: You cannot provide medical advice, diagnosis, or treatment recommendations. Always encourage consulting with healthcare professionals for medical concerns.

Keep responses warm, supportive, and practical. Focus on emotional support, practical daily care tips, and general guidance for caregivers and families dealing with dementia."""

    def get_chat_response(self, user_message: str, user_id: Optional[str] = None) -> str:
        """
        Get a response from GPT-5 for the user message using Responses API.

        Args:
            user_message: The user's message
            user_id: Optional user identifier for logging

        Returns:
            Response text from GPT-5

        Raises:
            Exception: If GPT-5 API call fails
        """
        try:
            logger.info(f"Sending message to GPT-5 for user {user_id}: {user_message[:100]}...")

            # Use GPT-5 Responses API exactly as documented
            response = self.client.responses.create(
                model="gpt-5",
                reasoning={"effort": "low"},
                instructions=self.norwegian_dementia_care_instructions,
                input=user_message,
            )

            response_text = response.output_text
            logger.info(f"GPT-5 response received for user {user_id}: {response_text[:100]}...")

            return response_text

        except Exception as error:
            # Clear error logging as requested (no fallbacks)
            logger.error(f"GPT-5 API Error for user {user_id}: {str(error)}")
            logger.error(f"Error type: {type(error).__name__}")

            if hasattr(error, 'response'):
                logger.error(f"HTTP status: {error.response.status_code}")
                logger.error(f"Response text: {error.response.text}")

            # Re-raise the error (no fallbacks as requested)
            raise error

# Global service instance
openai_service = OpenAIService()