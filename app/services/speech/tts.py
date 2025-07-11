import logging
import io
import tempfile
import os
import azure.cognitiveservices.speech as speechsdk

from app.config import settings
from app.core.errors import SpeechProcessingError

logger = logging.getLogger(__name__)

speech_synthesizer = None


async def initialize_tts_service():
    global speech_synthesizer
    
    try:
        azure_speech_config = speechsdk.SpeechConfig(
            subscription=settings.AZURE_SPEECH_KEY,
            region=settings.AZURE_SPEECH_REGION
        )
        
        azure_speech_config.speech_synthesis_voice_name = settings.AZURE_SPEECH_VOICE_NAME
        
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=azure_speech_config)
        
        logger.info("Azure speech synthesis service initialized successfully")
        return True
    except Exception as error:
        logger.exception("Failed to initialize Azure speech synthesis service")
        speech_synthesizer = None
        return False


async def text_to_speech(text_content: str) -> bytes:
    global speech_synthesizer
    
    if speech_synthesizer is None:
        service_initialized = await initialize_tts_service()
        if not service_initialized:
            raise SpeechProcessingError("Unable to initialize speech synthesis service")
    
    try:
        synthesis_result = speech_synthesizer.speak_text_async(text_content).get()
        
        if synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logger.info(f"Successfully synthesized speech for text: {text_content[:50]}...")
            return synthesis_result.audio_data
        else:
            error_message = (
                synthesis_result.cancellation_details.error_details 
                if synthesis_result.cancellation_details 
                else "Unknown synthesis error"
            )
            logger.error(f"Speech synthesis failed: {error_message}")
            raise SpeechProcessingError(f"Speech synthesis failed: {error_message}")
    except Exception as error:
        logger.exception("Error during speech synthesis process")
        raise SpeechProcessingError(f"Speech synthesis error: {str(error)}")


async def check_tts_service() -> bool:
    try:
        return await initialize_tts_service()
    except Exception:
        logger.exception("Speech synthesis service health check failed")
        return False