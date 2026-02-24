"""
utils/vertex_client.py
Vertex AI endpoint calls — MedGemma text, image, HeAR audio.
Also includes Gemini API fallback for gemini-1.5-flash.

MedGemma 1.5 image format discovery:
    - "image" key          → ❌ Unexpected keyword argument
    - "messages" key       → ❌ Unexpected keyword argument  
    - "content/inline_data"→ ❌ missing required field 'prompt'
    - "prompt" only        → ✅ text works
    
    Solution: Embed image as base64 data URI inside prompt string
    using Gemma chat template with <image> token.
"""
import base64
import logging
import os

from google.cloud import aiplatform
from google.api_core.exceptions import GoogleAPIError, ResourceExhausted, ServiceUnavailable
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from utils.config import PROJECT, ENDPOINTS, GEMINI_KEY

logger = logging.getLogger(__name__)

# Import free Gemini client as fallback
try:
    from utils.gemini_client import predict_text_gemini, predict_image_gemini
    GEMINI_FALLBACK = True
    logger.info("✅ Free Gemini API available as fallback")
except ImportError:
    GEMINI_FALLBACK = False
    logger.warning("⚠️ Gemini fallback not available")

_endpoints: dict[str, aiplatform.Endpoint] = {}

# Gemini API client (for gemini-1.5-flash)
_gemini_client = None

def init_endpoints() -> None:
    """Server startup లో ఒకసారి call చేయి."""
    global _gemini_client
    
    # Initialize Vertex AI endpoints
    for model_name, cfg in ENDPOINTS.items():
        if not cfg.get("id"):
            logger.warning(f"[{model_name}] Endpoint ID not set in .env — skipping.")
            continue
        try:
            aiplatform.init(project=PROJECT, location=cfg["region"])
            _endpoints[model_name] = aiplatform.Endpoint(
                f"projects/{PROJECT}/locations/{cfg['region']}/endpoints/{cfg['id']}"
            )
            logger.info(f"[{model_name}] Initialized @ {cfg['region']}")
        except Exception as e:
            logger.error(f"[{model_name}] Init failed: {e}")
    
    # Initialize Gemini API client
    if GEMINI_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_KEY)
            _gemini_client = genai
            logger.info("[gemini-1.5-flash] Gemini API initialized")
        except Exception as e:
            logger.error(f"[gemini-1.5-flash] Gemini API init failed: {e}")
    else:
        logger.warning("[gemini-1.5-flash] GEMINI_API_KEY not set — Gemini API unavailable")


def _get_endpoint(model_name: str) -> aiplatform.Endpoint:
    if model_name not in _endpoints:
        raise RuntimeError(
            f"{model_name} endpoint not available. "
            "Check .env endpoint IDs and startup logs."
        )
    return _endpoints[model_name]


def _extract_text(raw) -> str:
    """Vertex AI response నుండి clean text తీసుకో."""
    if isinstance(raw, dict):
        text = (raw.get("output")
                or raw.get("text")
                or raw.get("generated_text")
                or raw.get("content")
                or str(raw))
    else:
        text = str(raw)
    if "Output:" in text:
        text = text.split("Output:", 1)[-1].strip()
    return text.strip()


def predict_text(
    model_name: str,
    prompt: str,
    max_tokens: int = 1024,
    temperature: float = 0.3,
) -> str:
    """Text generation via MedGemma or Gemini API."""
    # Try free Gemini API first if billing is disabled
    if GEMINI_FALLBACK and model_name in ["medgemma_4b", "medgemma_27b"]:
        try:
            logger.info(f"Using FREE Gemini API instead of {model_name}")
            return predict_text_gemini(prompt, max_tokens, temperature)
        except Exception as e:
            logger.warning(f"Gemini fallback failed: {e}, trying Vertex AI...")
    
    # Check if this is a Gemini API model
    if model_name == "gemini-1.5-flash" and _gemini_client:
        try:
            model = _gemini_client.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(
                prompt,
                generation_config={
                    'max_output_tokens': max_tokens,
                    'temperature': temperature,
                }
            )
            return response.text
        except Exception as e:
            logger.error(f"[{model_name}] Gemini API error: {e}")
            raise RuntimeError(f"{model_name} temporarily unavailable. Please try again.")
    
    # Vertex AI endpoint
    try:
        endpoint = _get_endpoint(model_name)
        resp = endpoint.predict(instances=[{
            "prompt":      prompt,
            "max_tokens":  max_tokens,
            "temperature": temperature,
        }])
        return _extract_text(resp.predictions[0])
    except GoogleAPIError as e:
        logger.error(f"[{model_name}] GoogleAPIError: {e}")
        
        # Try Gemini fallback if billing error
        if GEMINI_FALLBACK and "BILLING_DISABLED" in str(e):
            logger.info("Billing disabled, using FREE Gemini API")
            return predict_text_gemini(prompt, max_tokens, temperature)
        
        raise RuntimeError(f"{model_name} temporarily unavailable. Please try again.")
    except Exception as e:
        logger.error(f"[{model_name}] Unexpected error: {e}")
        
        # Try Gemini fallback
        if GEMINI_FALLBACK:
            logger.info("Error occurred, using FREE Gemini API")
            return predict_text_gemini(prompt, max_tokens, temperature)
        
        raise RuntimeError("Service error. Please try again.")


# Retry wrapper for transient errors
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ResourceExhausted, ServiceUnavailable)),
)
def predict_text_with_retry(model_name: str, prompt: str, **kwargs) -> str:
    """
    Call predict_text with automatic retry on quota exhaustion or service unavailability.
    Use this in tools for better resilience.
    """
    return predict_text(model_name, prompt, **kwargs)


def predict_image(model_name: str, image_bytes: bytes, prompt: str) -> str:
    """
    Image analysis via MedGemma 1.5 or Gemini API.

    This endpoint only accepts 'prompt' field.
    Image is embedded as base64 data URI inside prompt
    using Gemma multimodal chat template format.
    """
    if len(image_bytes) > 10 * 1024 * 1024:
        raise ValueError("Image too large. Please upload under 10MB.")

    # Check if this is a Gemini API model
    if model_name == "gemini-1.5-flash" and _gemini_client:
        try:
            from PIL import Image
            import io
            
            image = Image.open(io.BytesIO(image_bytes))
            model = _gemini_client.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            logger.error(f"[{model_name}] Gemini API image error: {e}")
            raise RuntimeError("Image processing failed. Please try again.")

    # Vertex AI endpoint
    endpoint = _get_endpoint(model_name)
    b64 = base64.b64encode(image_bytes).decode()

    # Format 1: Gemma chat template with inline image token
    # <start_of_turn>user\n<image>\n{prompt}<end_of_turn>\n<start_of_turn>model\n
    gemma_prompt = (
        f"<start_of_turn>user\n"
        f"<img src=\"data:image/jpeg;base64,{b64}\">\n"
        f"{prompt}"
        f"<end_of_turn>\n"
        f"<start_of_turn>model\n"
    )

    instance = {
        "prompt":      gemma_prompt,
        "max_tokens":  1024,
        "temperature": 0.2,
    }

    try:
        resp = endpoint.predict(instances=[instance])
        result = _extract_text(resp.predictions[0])
        logger.info(f"[{model_name}] Image success, length: {len(result)}")
        return result

    except Exception as e:
        full_err = str(e)
        logger.error(f"[{model_name}] Format1 failed: {full_err[:300]}")

        # Format 2: Plain prompt with base64 embedded — simpler fallback
        try:
            simple_instance = {
                "prompt": f"Image data: data:image/jpeg;base64,{b64}\n\n{prompt}",
                "max_tokens":  1024,
                "temperature": 0.2,
            }
            resp2 = endpoint.predict(instances=[simple_instance])
            result2 = _extract_text(resp2.predictions[0])
            logger.info(f"[{model_name}] Format2 success, length: {len(result2)}")
            return result2

        except Exception as e2:
            logger.error(f"[{model_name}] Format2 also failed: {str(e2)[:300]}")
            raise RuntimeError("Image processing failed. Please try again.")


def predict_audio(model_name: str, audio_bytes: bytes) -> dict:
    """Audio analysis via HeAR model."""
    try:
        endpoint = _get_endpoint(model_name)
        resp = endpoint.predict(instances=[{
            "audio": {"bytesBase64Encoded": base64.b64encode(audio_bytes).decode()},
        }])
        return resp.predictions[0] if resp.predictions else {}
    except Exception as e:
        logger.error(f"[{model_name}] Audio error: {e}")
        raise RuntimeError("Audio analysis temporarily unavailable.")