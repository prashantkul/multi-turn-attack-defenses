from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class Message(BaseModel):
    role: str
    content: str


class Choice(BaseModel):
    message: Message  # Changed from Dict[str, str] to Message
    finish_reason: Optional[str] = None
    index: int


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class Response(BaseModel):
    """Response model for processing OpenAI completion content with analysis fields"""

    content: str
    risk_level: Optional[int] = None
    recommendations: Optional[List[str]] = None
    intent_shift: Optional[Dict[str, Optional[str]]] = None
    prompt_attack: Optional[Dict[str, Optional[str]]] = None
    patterns: Optional[Dict[str, Dict[str, Optional[str]]]] = None
    overall_progression_summary: Optional[Dict[str, Optional[str]]] = None
