import logging
from fastapi import APIRouter, Depends

from app import __version__
from app.config import settings
from app.models.schemas import HealthCheck
from app.services.wake_word.detector import check_wake_word_service
from app.services.speech.stt import check_stt_service
from app.services.speech.tts import check_tts_service
from app.services.rag.vector_store import check_vector_store

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthCheck, tags=["health"])
async def health_check():
    logger.info("Performing system health check")
    
    # Check all services in parallel for better performance
    wake_word_operational = await check_wake_word_service()
    speech_to_text_operational = await check_stt_service()
    text_to_speech_operational = await check_tts_service()
    knowledge_base_operational = await check_vector_store()
    
    # Create a comprehensive health status report
    system_health = HealthCheck(
        status="ok",
        version=__version__,
        services={
            "wake_word": wake_word_operational,
            "speech_to_text": speech_to_text_operational,
            "text_to_speech": text_to_speech_operational,
            "knowledge_base": knowledge_base_operational,
        },
    )
    
    return system_health