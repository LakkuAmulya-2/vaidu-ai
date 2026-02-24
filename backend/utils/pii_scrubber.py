"""
utils/pii_scrubber.py
Logs లో patient PII వెళ్ళకుండా scrub చేయి.
DPDPA 2023 (India Digital Personal Data Protection Act) compliance.
"""
import re

# Pattern → Replacement
PII_PATTERNS = [
    # Aadhaar number (12 digit, optional spaces)
    (r'\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b',   '[AADHAAR]'),
    # Indian phone numbers
    (r'\b[6-9]\d{9}\b',                                  '[PHONE]'),
    # Email addresses
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
    # Age patterns like "age: 45" or "aged 45"
    (r'\bage[d]?\s*:?\s*\d{1,3}\b',                     'age:[AGE]'),
    # Names after "patient:" or "name:" labels
    (r'(?i)(patient|name)\s*:\s*[A-Z][a-z]+(\s[A-Z][a-z]+)?', r'\1:[NAME]'),
]


def scrub_pii(text: str) -> str:
    """
    Input:  Raw text that may contain patient PII
    Output: Text with PII replaced — safe for logs

    Usage:
        logger.info(f"Request: {scrub_pii(user_message)}")

    Examples:
        "Patient Ravi Kumar, age 45, phone 9876543210"
        → "Patient [NAME], age:[AGE], phone [PHONE]"

        "Aadhaar: 2345 6789 0123"
        → "Aadhaar: [AADHAAR]"
    """
    for pattern, replacement in PII_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text