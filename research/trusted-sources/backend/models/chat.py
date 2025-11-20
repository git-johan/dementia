from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    timestamp: int
    user_id: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None