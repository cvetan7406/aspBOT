import logging
import io
import tempfile
import os
from typing import Tuple, Optional
import openai

from app.config import settings
from app.core.errors import SpeechProcessingError

logger = logging.getLogger(__name__)


async def transcribe_audio(audio_data: bytes) -> Tuple[str, float]:
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_temp_file:
            audio_temp_file.write(audio_data)
            audio_file_path = audio_temp_file.name
        
        try:
            openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            with open(audio_file_path, "rb") as audio_file:
                transcription_response = openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="bg",
                    response_format="verbose_json",
                )
            
            transcribed_text = transcription_response.text
            
            # Using fixed confidence since Whisper doesn't provide confidence scores
            estimated_confidence = 0.9
            
            logger.info(f"Successfully transcribed audio: {transcribed_text[:50]}...")
            return transcribed_text, estimated_confidence
        finally:
            if os.path.exists(audio_file_path):
                os.unlink(audio_file_path)
    except Exception as error:
        logger.exception("Failed to transcribe audio")
        raise SpeechProcessingError(f"Speech recognition failed: {str(error)}")


async def check_stt_service() -> bool:
    try:
        sample_rate = 16000  # 16kHz
        test_duration_seconds = 1
        total_samples = sample_rate * test_duration_seconds
        silent_audio_bytes = bytes(total_samples * 2)  # 16-bit samples (2 bytes per sample)
        
        await transcribe_audio(silent_audio_bytes)
        return True
    except Exception:
        logger.exception("Speech recognition service health check failed")
        return False