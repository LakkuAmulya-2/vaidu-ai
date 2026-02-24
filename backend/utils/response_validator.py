"""
utils/response_validator.py
AI response ని patient కి పంపే ముందు validate చేయి.
Hallucination లేదా dangerous content ఉంటే sanitize చేయి.
"""

# Definitive diagnoses LLM చేయకూడదు — replace with warning
DANGEROUS_MEDICAL_CLAIMS = [
    ("you have cancer",           "Please visit a doctor for proper diagnosis."),
    ("you have diabetes",         "Please get a blood sugar test at your nearest PHC."),
    ("you have tuberculosis",     "Please visit DOTS center for free TB test."),
    ("you have hiv",              "Please visit PHC for confidential testing."),
    ("you have heart disease",    "Please visit a cardiologist for proper evaluation."),
    ("you have kidney failure",   "Please visit a doctor immediately for evaluation."),
    ("you are diabetic",          "Please get a blood sugar test at your nearest PHC."),
]

# Specific drug dosages — hallucination red flag
DOSAGE_PATTERNS = [
    "mg twice daily",
    "mg once daily",
    "mg three times",
    "inject insulin",
    "take 500mg",
    "take 250mg",
    "take 1000mg",
]

# Responses MUST have uncertainty language for clinical assessments
REQUIRED_UNCERTAINTY_PHRASES = [
    "consult", "doctor", "phc", "may", "could", "possible",
    "suggest", "visit", "check", "monitor", "unclear",
]

# Tools that require uncertainty language check
CLINICAL_TOOLS = [
    "triage_symptoms",
    "analyze_scan",
    "node_risk_screen",
    "analyze_skin",
    "maternal_guidance",
]


def _check_hallucination_risk(text: str) -> bool:
    """
    LLM overconfident గా ఉందా check చేయి.

    Input:  LLM response text
    Output: True = hallucination risk detected
    """
    overconfident = [
        "you definitely have",
        "you certainly have",
        "100% sure",
        "guaranteed",
        "no doubt",
        "i am certain",
        "confirmed diagnosis",
    ]
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in overconfident)


def validate_response(text: str, tool_name: str = "") -> str:
    """
    Input:  Raw LLM response string
    Output: Validated, safe response string

    Changes made:
    - Definitive diagnoses → appends warning note
    - Specific drug dosages → appends dosage warning
    - Overconfident language → replace with safe fallback
    - No uncertainty language in clinical tool → append reminder

    Usage:
        result_en = predict_text("medgemma_27b", prompt)
        result_en = validate_response(result_en, tool_name="triage_symptoms")
    """
    if not text or len(text.strip()) < 10:
        return "Unable to assess. Please visit nearest PHC for proper examination."

    text_lower = text.lower()
    warnings = []

    # Check overconfident hallucination — replace entirely
    if _check_hallucination_risk(text):
        return (
            "Based on the information provided, a proper medical assessment "
            "is needed. Please visit your nearest PHC or qualified doctor. "
            "If this is an emergency, call 108 immediately."
        )

    # Flag dangerous definitive claims
    for claim, replacement in DANGEROUS_MEDICAL_CLAIMS:
        if claim in text_lower:
            warnings.append(f"⚠️ Note: {replacement}")

    # Flag specific dosage hallucinations
    for pattern in DOSAGE_PATTERNS:
        if pattern in text_lower:
            warnings.append(
                "⚠️ Dosage shown is AI-generated. "
                "Always follow your doctor's prescription for exact dosage."
            )
            break  # One dosage warning enough

    # Ensure uncertainty language in clinical responses
    if tool_name in CLINICAL_TOOLS and len(text) > 100:
        has_uncertainty = any(p in text_lower for p in REQUIRED_UNCERTAINTY_PHRASES)
        if not has_uncertainty:
            warnings.append(
                "⚠️ This is AI guidance only. "
                "Please confirm with a qualified doctor before taking any action."
            )

    if warnings:
        text = text + "\n\n" + "\n".join(warnings)

    return text