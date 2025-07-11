import logging
import io
import numpy as np
from typing import Tuple, Optional
import pvporcupine
import struct
import wave

from app.config import settings
from app.core.errors import WakeWordError

logger = logging.getLogger(__name__)

porcupine_instance = None


async def initialize_wake_word_detector():
    global porcupine_instance
    
    try:
        porcupine_instance = pvporcupine.create(
            access_key=settings.PORCUPINE_ACCESS_KEY,
            keywords=["jarvis"],  # Placeholder - would be replaced with actual wake word
        )
        
        logger.info("Wake word detection service initialized successfully")
        return True
    except Exception as error:
        logger.exception("Failed to initialize wake word detection service")
        porcupine_instance = None
        return False


async def detect_wake_word(audio_data: bytes) -> Tuple[bool, float]:
    global porcupine_instance
    
    if porcupine_instance is None:
        detector_initialized = await initialize_wake_word_detector()
        if not detector_initialized:
            raise WakeWordError("Unable to initialize wake word detection service")
    
    try:
        processed_audio = convert_audio_to_pcm(audio_data)
        
        frame_size = porcupine_instance.frame_length
        wake_word_detected = False
        detection_confidence = 0.0
        
        for frame_start in range(0, len(processed_audio) - frame_size, frame_size):
            audio_frame = processed_audio[frame_start:frame_start + frame_size]
            
            if len(audio_frame) < frame_size:
                audio_frame = np.pad(audio_frame, (0, frame_size - len(audio_frame)), 'constant')
            
            detection_result = porcupine_instance.process(audio_frame)
            
            if detection_result >= 0:
                wake_word_detected = True
                detection_confidence = 0.8  # Fixed value since Porcupine doesn't provide confidence
                break
        
        logger.info(f"Wake word detection completed: detected={wake_word_detected}, confidence={detection_confidence}")
        return wake_word_detected, detection_confidence
    except Exception as error:
        logger.exception("Error during wake word detection")
        raise WakeWordError(str(error))


def convert_audio_to_pcm(audio_data: bytes) -> np.ndarray:
    try:
        with io.BytesIO(audio_data) as audio_stream:
            with wave.open(audio_stream, 'rb') as wav_file:
                if wav_file.getnchannels() != 1 or wav_file.getsampwidth() != 2:
                    # Audio format conversion would be implemented here in production
                    pass
                
                pcm_data = np.frombuffer(wav_file.readframes(wav_file.getnframes()), dtype=np.int16)
                return pcm_data
    except Exception as error:
        logger.exception("Failed to convert audio to PCM format")
        raise WakeWordError(f"Audio format conversion error: {str(error)}")


async def check_wake_word_service() -> bool:
    try:
        return await initialize_wake_word_detector()
    except Exception:
        logger.exception("Wake word detection service health check failed")
        return False