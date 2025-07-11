import logging
import uuid
import base64
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config import settings
from app.core.security import get_current_active_user
from app.models.schemas import (
    WakeWordRequest,
    WakeWordResponse,
    TranscriptionRequest,
    TranscriptionResponse,
    RAGRequest,
    RAGResponse,
    TextToSpeechRequest,
    TextToSpeechResponse,
    VoiceInteractionRequest,
    VoiceInteractionResponse,
    User,
)
from app.services.wake_word.detector import detect_wake_word
from app.services.speech.stt import transcribe_audio
from app.services.speech.tts import text_to_speech
from app.services.rag.retriever import query_rag_system
from app.core.errors import (
    SpeechProcessingError,
    WakeWordError,
    RAGError,
    NoRelevantDocumentsError,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/wake-word", response_model=WakeWordResponse)
async def wake_word_detection(
    request: WakeWordRequest,
    current_user: User = Depends(get_current_active_user),
):
    logger.info("Processing wake word detection request")
    
    try:
        audio_bytes = base64.b64decode(request.audio_data)
        
        is_wake_word_detected, detection_confidence = await detect_wake_word(audio_bytes)
        
        conversation_id = str(uuid.uuid4()) if is_wake_word_detected else None
        
        return WakeWordResponse(
            detected=is_wake_word_detected,
            confidence=detection_confidence,
            session_id=conversation_id,
        )
    except Exception as error:
        logger.exception("Failed to detect wake word in audio")
        raise WakeWordError(str(error))


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(
    request: TranscriptionRequest,
    current_user: User = Depends(get_current_active_user),
):
    logger.info(f"Converting speech to text for session {request.session_id}")
    
    try:
        audio_bytes = base64.b64decode(request.audio_data)
        
        transcribed_text, recognition_confidence = await transcribe_audio(audio_bytes)
        
        return TranscriptionResponse(
            text=transcribed_text,
            confidence=recognition_confidence,
        )
    except Exception as error:
        logger.exception("Failed to transcribe audio to text")
        raise SpeechProcessingError(str(error))


@router.post("/rag", response_model=RAGResponse)
async def retrieve_answer(
    request: RAGRequest,
    current_user: User = Depends(get_current_active_user),
):
    logger.info(f"Finding answer for query in session {request.session_id}")
    
    try:
        generated_answer, relevant_documents = await query_rag_system(request.query)
        
        if not generated_answer:
            raise NoRelevantDocumentsError()
        
        return RAGResponse(
            answer=generated_answer,
            source_documents=relevant_documents,
            query=request.query,
        )
    except NoRelevantDocumentsError:
        return RAGResponse(
            answer=settings.DEFAULT_RESPONSE,
            source_documents=[],
            query=request.query,
        )
    except Exception as error:
        logger.exception("Failed to generate answer from knowledge base")
        raise RAGError(str(error))


@router.post("/tts", response_model=TextToSpeechResponse)
async def synthesize_speech(
    request: TextToSpeechRequest,
    current_user: User = Depends(get_current_active_user),
):
    logger.info(f"Converting text to speech for session {request.session_id}")
    
    try:
        audio_bytes = await text_to_speech(request.text)
        
        audio_base64_string = base64.b64encode(audio_bytes).decode("utf-8")
        
        return TextToSpeechResponse(
            audio_data=audio_base64_string,
        )
    except Exception as error:
        logger.exception("Failed to convert text to speech")
        raise SpeechProcessingError(str(error))


@router.post("/interact", response_model=VoiceInteractionResponse)
async def complete_voice_interaction(
    request: VoiceInteractionRequest,
    current_user: User = Depends(get_current_active_user),
):
    logger.info("Processing complete voice interaction flow")
    
    try:
        audio_bytes = base64.b64decode(request.audio_data)
        
        conversation_id = str(uuid.uuid4())
        
        is_wake_word_detected, _ = await detect_wake_word(audio_bytes)
        
        if not is_wake_word_detected:
            return VoiceInteractionResponse(
                wake_word_detected=False,
                session_id=conversation_id,
            )
        
        transcribed_text, _ = await transcribe_audio(audio_bytes)
        
        generated_answer, _ = await query_rag_system(transcribed_text)
        
        if not generated_answer:
            generated_answer = settings.DEFAULT_RESPONSE
        
        speech_audio_bytes = await text_to_speech(generated_answer)
        
        speech_audio_base64 = base64.b64encode(speech_audio_bytes).decode("utf-8")
        
        return VoiceInteractionResponse(
            wake_word_detected=True,
            transcription=transcribed_text,
            answer=generated_answer,
            audio_response=speech_audio_base64,
            session_id=conversation_id,
        )
    except Exception as error:
        logger.exception("Error in voice interaction pipeline")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        )