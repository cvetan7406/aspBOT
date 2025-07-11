from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: int = None


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class User(UserBase):
    id: Optional[str] = None

    class Config:
        orm_mode = True


class WakeWordRequest(BaseModel):
    audio_data: str = Field(..., description="Base64 encoded audio data")


class WakeWordResponse(BaseModel):
    detected: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    session_id: Optional[str] = None


class TranscriptionRequest(BaseModel):
    audio_data: str = Field(..., description="Base64 encoded audio data")
    session_id: str


class TranscriptionResponse(BaseModel):
    text: str
    language: str = "bg"
    confidence: float = Field(..., ge=0.0, le=1.0)


class RAGRequest(BaseModel):
    query: str
    session_id: str


class DocumentChunk(BaseModel):
    content: str
    metadata: Dict[str, Any]
    score: float = Field(..., ge=0.0, le=1.0)


class RAGResponse(BaseModel):
    answer: str
    source_documents: List[DocumentChunk]
    query: str


class TextToSpeechRequest(BaseModel):
    text: str
    session_id: str


class TextToSpeechResponse(BaseModel):
    audio_data: str = Field(..., description="Base64 encoded audio data")


class VoiceInteractionRequest(BaseModel):
    audio_data: str = Field(..., description="Base64 encoded audio data")


class VoiceInteractionResponse(BaseModel):
    wake_word_detected: bool
    transcription: Optional[str] = None
    answer: Optional[str] = None
    audio_response: Optional[str] = Field(None, description="Base64 encoded audio data")
    session_id: str


class HealthCheck(BaseModel):
    status: str
    version: str
    services: Dict[str, bool]