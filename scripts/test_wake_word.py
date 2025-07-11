import asyncio
import logging
import argparse
import os
import sys
import wave
import pyaudio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.wake_word.detector import detect_wake_word, initialize_wake_word_detector
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

AUDIO_CHUNK_SIZE = 1024
AUDIO_FORMAT = pyaudio.paInt16
AUDIO_CHANNELS = 1
SAMPLE_RATE = 16000
RECORDING_DURATION = 3


async def record_audio_from_microphone():
    logger.info("Recording audio sample for wake word testing...")
    
    audio_interface = pyaudio.PyAudio()
    
    audio_stream = audio_interface.open(
        format=AUDIO_FORMAT,
        channels=AUDIO_CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=AUDIO_CHUNK_SIZE,
    )
    
    audio_frames = []
    
    total_chunks = int(SAMPLE_RATE / AUDIO_CHUNK_SIZE * RECORDING_DURATION)
    for _ in range(0, total_chunks):
        chunk_data = audio_stream.read(AUDIO_CHUNK_SIZE)
        audio_frames.append(chunk_data)
    
    logger.info("Audio recording completed")
    
    audio_stream.stop_stream()
    audio_stream.close()
    audio_interface.terminate()
    
    complete_audio_data = b"".join(audio_frames)
    
    output_filename = "test_audio.wav"
    with wave.open(output_filename, "wb") as wave_file:
        wave_file.setnchannels(AUDIO_CHANNELS)
        wave_file.setsampwidth(audio_interface.get_sample_size(AUDIO_FORMAT))
        wave_file.setframerate(SAMPLE_RATE)
        wave_file.writeframes(complete_audio_data)
    
    logger.info(f"Audio saved to {output_filename}")
    return complete_audio_data


async def main():
    argument_parser = argparse.ArgumentParser(description="Test wake word detection for ASP Bot")
    argument_parser.add_argument(
        "--file",
        type=str,
        help="Path to audio file to test (WAV format)",
    )
    parsed_args = argument_parser.parse_args()
    
    try:
        await initialize_wake_word_detector()
        
        if parsed_args.file:
            audio_file_path = parsed_args.file
            logger.info(f"Using audio file: {audio_file_path}")
            with open(audio_file_path, "rb") as audio_file:
                audio_data = audio_file.read()
        else:
            audio_data = await record_audio_from_microphone()
        
        wake_word_detected, detection_confidence = await detect_wake_word(audio_data)
        
        if wake_word_detected:
            logger.info(f"✓ Wake word detected with confidence {detection_confidence:.2f}")
        else:
            logger.info(f"✗ Wake word not detected (confidence: {detection_confidence:.2f})")
    except Exception as error:
        logger.exception(f"Wake word detection test failed: {str(error)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())