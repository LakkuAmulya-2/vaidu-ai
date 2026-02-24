"""
Free Gemini API client - No billing required!
Get API key: https://aistudio.google.com/app/apikey
"""
import os
import logging
import google.generativeai as genai
from PIL import Image
import io

logger = logging.getLogger(__name__)

# Initialize Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("✅ Gemini API initialized (FREE)")
else:
    logger.warning("⚠️ GEMINI_API_KEY not set")


def predict_text_gemini(prompt: str, max_tokens: int = 1024, temperature: float = 0.3) -> str:
    """Text generation using FREE Gemini API."""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            prompt,
            generation_config={
                'max_output_tokens': max_tokens,
                'temperature': temperature,
            }
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise RuntimeError(f"Service temporarily unavailable: {e}")


def predict_image_gemini(image_bytes: bytes, prompt: str) -> str:
    """Image analysis using FREE Gemini API."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        logger.error(f"Gemini image error: {e}")
        raise RuntimeError(f"Image processing failed: {e}")
