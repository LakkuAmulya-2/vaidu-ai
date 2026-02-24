"""
utils/voice_processor.py
Voice processing utilities for speech-to-text and text-to-speech
"""
import logging
import base64
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech

logger = logging.getLogger(__name__)

# Language mapping for Google Cloud APIs
LANG_MAP = {
    "te": "te-IN",
    "hi": "hi-IN",
    "ta": "ta-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "bn": "bn-IN",
    "mr": "mr-IN",
    "en": "en-US"
}

def transcribe_audio(audio_bytes: bytes, lang: str = "te") -> str:
    """
    Convert audio to text using Google Cloud Speech-to-Text
    
    Args:
        audio_bytes: Audio file bytes (WAV, MP3, etc.)
        lang: Language code (te, hi, en, etc.)
    
    Returns:
        Transcribed text
    """
    try:
        client = speech.SpeechClient()
        
        language_code = LANG_MAP.get(lang, "te-IN")
        
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code=language_code,
            enable_automatic_punctuation=True,
            model="default",
        )
        
        response = client.recognize(config=config, audio=audio)
        
        if not response.results:
            return ""
        
        # Get the first result's transcript
        transcript = response.results[0].alternatives[0].transcript
        logger.info(f"Transcribed: {transcript[:50]}...")
        return transcript
        
    except Exception as e:
        logger.error(f"Speech-to-text error: {e}")
        raise RuntimeError(f"Transcription failed: {str(e)}")


def synthesize_speech(text: str, lang: str = "te") -> bytes:
    """
    Convert text to speech using Google Cloud Text-to-Speech
    
    Args:
        text: Text to convert to speech
        lang: Language code (te, hi, en, etc.)
    
    Returns:
        Audio bytes (MP3 format)
    """
    try:
        client = texttospeech.TextToSpeechClient()
        
        language_code = LANG_MAP.get(lang, "te-IN")
        
        # Set the text input
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Build the voice request
        # Use Standard-A for female voice, Standard-B for male
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=f"{language_code}-Standard-A",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        
        # Select audio format
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.95,  # Slightly slower for clarity
            pitch=0.0
        )
        
        # Perform the text-to-speech request
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        logger.info(f"Synthesized {len(response.audio_content)} bytes of audio")
        return response.audio_content
        
    except Exception as e:
        logger.error(f"Text-to-speech error: {e}")
        raise RuntimeError(f"Speech synthesis failed: {str(e)}")
