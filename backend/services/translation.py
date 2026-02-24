"""
services/translation.py
Language translation with two-tier fallback:
  1. Google Cloud Translation API (official) — if enabled in GCP
  2. deep-translator (free, no httpx conflict) — fallback

deep-translator వాడాం because:
  - googletrans==4.0.0rc1 httpx 0.13.3 install చేస్తుంది (google-adk break అవుతుంది)
  - deep-translator కి httpx dependency లేదు — safe
"""
import logging

logger = logging.getLogger(__name__)

SUPPORTED = {
    "te": "Telugu",  "hi": "Hindi",  "ta": "Tamil",
    "kn": "Kannada", "ml": "Malayalam", "bn": "Bengali",
    "mr": "Marathi", "en": "English",
}

# Language code mapping for deep-translator
LANG_MAP = {
    "te": "telugu",  "hi": "hindi",   "ta": "tamil",
    "kn": "kannada", "ml": "malayalam","bn": "bengali",
    "mr": "marathi", "en": "english",
}


def _cloud_translate(text: str, source: str, target: str) -> str:
    """Official Google Cloud Translation API."""
    from google.cloud import translate_v2 as translate
    client = translate.Client()
    result = client.translate(text, source_language=source, target_language=target)
    return result["translatedText"]


def _free_translate(text: str, source: str, target: str) -> str:
    """deep-translator free fallback — no httpx conflict."""
    from deep_translator import GoogleTranslator
    src = LANG_MAP.get(source, source)
    tgt = LANG_MAP.get(target, target)
    return GoogleTranslator(source=src, target=tgt).translate(text)


def _translate(text: str, source: str, target: str) -> str:
    """Try official API first, fall back to deep-translator."""
    try:
        return _cloud_translate(text, source, target)
    except Exception as e:
        if "SERVICE_DISABLED" in str(e) or "403" in str(e):
            logger.debug("Cloud Translation API not enabled, using free fallback")
        else:
            logger.warning(f"Cloud Translation failed: {e}, trying free fallback")

    # Free fallback
    try:
        return _free_translate(text, source, target)
    except Exception as e:
        logger.warning(f"Free translation also failed: {e}")
        raise


def to_english(text: str, lang: str) -> str:
    if lang == "en" or not text.strip():
        return text
    try:
        return _translate(text, lang, "en")
    except Exception as e:
        logger.warning(f"Translation {lang}→en failed: {e}")
        return text


def to_local(text: str, lang: str) -> str:
    if lang == "en" or not text.strip():
        return text
    try:
        return _translate(text, "en", lang)
    except Exception as e:
        logger.warning(f"Translation en→{lang} failed: {e}")
        return text