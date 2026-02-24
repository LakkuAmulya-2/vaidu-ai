"""
utils/sanitizer.py
User input sanitization — prompt injection + XSS + overflow prevention.
"""
import re

# Prompt injection patterns
INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|prior)\s+instructions?",
    r"you\s+are\s+now\s+a",
    r"act\s+as\s+(a|an)",
    r"forget\s+(everything|all|previous)",
    r"new\s+system\s+prompt",
    r"jailbreak",
    r"dan\s+mode",
    r"<\s*script",
    r"javascript\s*:",
    r"data\s*:",
    r"\{\{.*?\}\}",
    r"__import__",
    r"eval\s*\(",
    r"exec\s*\(",
]


def sanitize_user_input(text: str, max_len: int = 1000) -> str:
    """
    Input:  Raw user text from form/API
    Output: Clean, safe text for LLM prompt

    Usage:
        clean = sanitize_user_input(raw_symptoms)
    """
    if not text:
        return ""

    # Length limit
    text = text[:max_len]

    # Remove injection patterns (case insensitive)
    for pattern in INJECTION_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # Remove null bytes and control characters (keep newlines)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    # Collapse excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def sanitize_image_metadata(filename: str) -> str:
    """
    Filename లో path traversal prevent చేయి.

    Input:  "../../etc/passwd.jpg"
    Output: "______etc_passwd.jpg"
    """
    return re.sub(r'[^a-zA-Z0-9._-]', '_', filename)[:100]