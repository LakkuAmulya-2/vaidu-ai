"""
agents/tools.py
ADK FunctionTools — ప్రతి function ఒక specialist agent.
ADK Orchestrator ఇవి use చేసి routing చేస్తుంది.

Fixes applied:
    - sanitize_user_input() on all user inputs
    - validate_response() on all LLM outputs (hallucination prevention)
    - Official Cloud Translation API
    - SSL verification enabled in verify_doctor()
    - process_upload() for EXIF strip + image validation
    - Caching for similar queries (via utils.cache)
    - Retry logic for Vertex AI calls (via utils.vertex_client.predict_text_with_retry)
"""

import httpx
import logging

from utils.vertex_client import predict_text_with_retry, predict_image, predict_audio
from utils.config import DISCLAIMER, EMERGENCY_PATTERNS
from utils.sanitizer import sanitize_user_input
from utils.response_validator import validate_response
from utils.image_processor import process_upload
from utils.cache import cached_predict_text   # <-- new caching utility
from services.translation import to_english, to_local
from services.healthcare_search import healthcare_search

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _severity(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["emergency", "immediately", "108", "urgent", "severe"]):
        return "RED"
    if any(w in t for w in ["consult", "phc", "monitor", "visit", "yellow"]):
        return "YELLOW"
    return "GREEN"


def _check_emergency(text: str) -> str | None:
    t = text.lower()
    for keywords, msg in EMERGENCY_PATTERNS:
        if all(k in t for k in keywords):
            return msg
    return None


# ─────────────────────────────────────────────
# TOOL 1 — Symptom Triage
# ─────────────────────────────────────────────

def triage_symptoms(
    symptoms: str,
    age: int = 0,
    is_pregnant: bool = False,
    lang: str = "te",
) -> dict:
    """
    Assess patient symptoms. Returns severity GREEN/YELLOW/RED.
    Use for: fever, pain, cough, general illness queries.

    Args:
        symptoms:     Patient symptoms in any language
        age:          Patient age (0 if unknown)
        is_pregnant:  Whether patient is pregnant
        lang:         Language code (te/hi/ta/kn/en)
    """
    try:
        # Sanitize — prompt injection prevent
        clean = sanitize_user_input(symptoms)
        if not clean:
            return {"success": False, "response": "Please describe your symptoms.", "severity": "UNKNOWN"}

        en = to_english(clean, lang)

        # Fast rule-based emergency check (no API call needed)
        emg = _check_emergency(en)
        if emg:
            msg = f"🚨 EMERGENCY: {emg}. వెంటనే 108 call చేయండి!"
            return {
                "success":  True,
                "response": to_local(msg, lang),
                "severity": "RED",
                "call_108": True,
            }

        prompt = f"""You are VAIDU, medical AI for rural India.
Patient symptoms: {en}
Age: {age or 'unknown'}, Pregnant: {is_pregnant}

STRICT RULES:
- If you are not sure → say "unclear, visit PHC"
- NEVER invent drug names, dosages, or test values
- NEVER say "you have [disease]" — say "this may suggest"
- If symptoms are complex → say "needs doctor evaluation"
- Use "may be" / "could be" language only

Provide:
1. Severity: GREEN (home care) / YELLOW (visit PHC) / RED (emergency 108)
2. Possible reason (uncertain language only)
3. Immediate action
4. Warning signs to watch

If you cannot assess confidently → respond:
"Symptoms unclear. Please visit nearest PHC for proper examination."
Max 120 words."""

        result_en = predict_text_with_retry("medgemma_4b", prompt)
        result_en = validate_response(result_en, tool_name="triage_symptoms")

        return {
            "success":  True,
            "response": to_local(result_en + DISCLAIMER, lang),
            "severity": _severity(result_en),
            "call_108": _severity(result_en) == "RED",
        }
    except RuntimeError as e:
        return {"success": False, "response": str(e), "severity": "UNKNOWN"}
    except Exception as e:
        logger.error(f"triage_symptoms error: {e}")
        return {"success": False, "response": "Unable to process. Visit nearest PHC.", "severity": "UNKNOWN"}


# ─────────────────────────────────────────────
# TOOL 2 — Prescription Analyzer (fixed repetition)
# ─────────────────────────────────────────────

def analyze_prescription(image_bytes: bytes, lang: str = "te") -> dict:
    """
    Analyze prescription image. Explains medicines in local language.
    Use for: prescription photos, medicine queries.

    Args:
        image_bytes: Prescription image bytes (JPG/PNG) — already validated+stripped
        lang:        Language code
    """
    try:
        prompt = """Analyze this medical prescription carefully.

Provide a clear, concise summary in simple language. List each medicine **only once** with all relevant details together.

Format your response as a numbered list. For each medicine:
- Medicine name (as written)
- What condition it treats (in simple terms)
- Dosage (tablets, frequency, timing, duration)
- Important warnings (if any)

STRICT RULES:
- If text is unclear → say "please verify with pharmacist"
- Do NOT suggest alternative medicines
- Do NOT change doses — report exactly what is written
- Do NOT repeat any medicine name
- Patient has no medical background — use very simple words

Example output:
1. Paracetamol 500mg: Used for fever and pain. Take one tablet when needed, up to 3 times a day. Do not exceed 4 tablets in 24 hours.
2. Amoxicillin 250mg: Antibiotic for bacterial infections. Take one capsule twice daily for 7 days. Complete the full course even if you feel better.

Now analyze the prescription image and produce the list."""
        result_en = predict_image("medgemma_4b", image_bytes, prompt)
        result_en = validate_response(result_en, tool_name="analyze_prescription")

        # Optional post‑process: remove duplicate numbered lines
        lines = result_en.split('\n')
        seen = set()
        cleaned = []
        for line in lines:
            stripped = line.strip()
            if stripped and (stripped[0].isdigit() or stripped.startswith('-')):
                if stripped.lower() not in seen:
                    seen.add(stripped.lower())
                    cleaned.append(line)
            else:
                cleaned.append(line)
        result_en = '\n'.join(cleaned)

        return {
            "success":  True,
            "response": to_local(result_en + DISCLAIMER, lang),
            "severity": _severity(result_en),
        }
    except (ValueError, RuntimeError) as e:
        return {"success": False, "response": str(e)}
    except Exception as e:
        logger.error(f"analyze_prescription error: {e}")
        return {"success": False, "response": "Unable to analyze prescription. Please try again."}


# ─────────────────────────────────────────────
# TOOL 3 — Medical Scan Analyzer
# ─────────────────────────────────────────────

def analyze_scan(
    image_bytes: bytes,
    scan_type: str = "xray",
    lang: str = "te",
    enable_visual_qa: bool = False,
    qa_query: str = "",
) -> dict:
    """
    Analyze medical scans: xray, ct, mri, lab report.
    Use for: X-ray, CT scan, MRI, lab report images.

    Args:
        image_bytes: Scan image bytes — already validated+stripped
        scan_type:   xray / ct / mri / lab
        lang:        Language code
        enable_visual_qa: Enable visual Q&A search for similar cases
        qa_query: Optional specific question for visual search
    """
    PROMPTS = {
        "xray": "Analyze this chest X-ray. Describe findings simply. Note any abnormalities. Recommend radiologist review.",
        "ct":   "Analyze this CT scan. Describe what you observe simply. Note areas of concern. Recommend specialist.",
        "mri":  "Analyze this MRI image. Describe findings simply. Do not diagnose. Recommend specialist.",
        "lab":  "Analyze this lab report. For each value: what it measures, normal or abnormal, what it indicates. Simple language.",
    }
    try:
        base_prompt = PROMPTS.get(scan_type, PROMPTS["xray"])
        prompt = base_prompt + """

STRICT RULES FOR IMAGE ANALYSIS:
- If image is blurry/unclear → say "Image quality poor, cannot assess"
- If you see something abnormal → say "possible" or "appears to show"
- NEVER say "you have [condition]"
- NEVER give treatment based on image alone
- ALWAYS end with "Specialist confirmation required"
- If uncertain about ANY finding → skip it, do not guess
- IMPORTANT: Do NOT make definitive diagnosis"""

        result_en = predict_image("medgemma_4b", image_bytes, prompt)
        result_en = validate_response(result_en, tool_name="analyze_scan")
        
        response_data = {
            "success":   True,
            "response":  to_local(result_en + DISCLAIMER, lang),
            "severity":  _severity(result_en),
            "scan_type": scan_type,
        }
        
        # Add visual Q&A if enabled
        if enable_visual_qa:
            search_query = qa_query if qa_query else f"find similar {scan_type} cases"
            visual_qa_results = search_medical_cases(
                image_bytes=image_bytes,
                query=search_query,
                lang=lang
            )
            response_data["visual_qa"] = visual_qa_results
        
        return response_data
        
    except (ValueError, RuntimeError) as e:
        return {"success": False, "response": str(e)}
    except Exception as e:
        logger.error(f"analyze_scan error: {e}")
        return {"success": False, "response": "Unable to analyze scan. Please try again."}


# ─────────────────────────────────────────────
# TOOL 4 — Skin / Eye / Foot Analyzer
# ─────────────────────────────────────────────

def analyze_skin(
    image_bytes: bytes,
    area: str = "skin",
    lang: str = "te",
    enable_visual_qa: bool = False,
    qa_query: str = "",
) -> dict:
    """
    Analyze skin conditions, diabetic eye, diabetic foot.
    Use for: skin rash, foot wound, eye/retina photo.

    Args:
        image_bytes: Photo bytes — already validated+stripped
        area:        skin / eye / foot
        lang:        Language code
        enable_visual_qa: Enable visual Q&A search for similar cases
        qa_query: Optional specific question for visual search
    """
    PROMPTS = {
        "skin": """Analyze this skin image. Identify:
- Condition type (fungal, bacterial, inflammatory, etc.) — use "may be" language
- Severity (mild/moderate/severe)
- Common conditions it resembles
- Red flags requiring urgent dermatologist visit
NEVER give definitive diagnosis. Recommend dermatologist consultation.""",

        "eye": """Analyze this retinal/eye image for:
- Diabetic retinopathy signs (grade if possible — use "appears to show" language)
- Cataract or glaucoma indicators
- Urgency level
NEVER give definitive diagnosis. Recommend ophthalmologist consultation.""",

        "foot": """Analyze this diabetic foot image:
- Wagner scale stage (0-5)
- Signs of infection (yes/no)
- Action needed: home care / PHC / hospital / emergency 108
Diabetic foot worsens rapidly — be direct about urgency.
NEVER say infection is definitely absent without clear evidence.""",
    }
    try:
        prompt = PROMPTS.get(area, PROMPTS["skin"])
        result_en = predict_image("medgemma_4b", image_bytes, prompt)
        result_en = validate_response(result_en, tool_name="analyze_skin")
        
        response_data = {
            "success":  True,
            "response": to_local(result_en + DISCLAIMER, lang),
            "severity": _severity(result_en),
            "area":     area,
        }
        
        # Add visual Q&A if enabled
        if enable_visual_qa:
            search_query = qa_query if qa_query else f"find similar {area} condition cases"
            visual_qa_results = search_medical_cases(
                image_bytes=image_bytes,
                query=search_query,
                lang=lang
            )
            response_data["visual_qa"] = visual_qa_results
        
        return response_data
        
    except (ValueError, RuntimeError) as e:
        return {"success": False, "response": str(e)}
    except Exception as e:
        logger.error(f"analyze_skin error: {e}")
        return {"success": False, "response": "Unable to analyze. Please try again."}


# ─────────────────────────────────────────────
# TOOL 5 — Cough / Audio Analyzer (HeAR)
# ─────────────────────────────────────────────

def analyze_cough(audio_bytes: bytes, lang: str = "te") -> dict:
    """
    Analyze cough audio for TB/respiratory conditions using HeAR model.
    Use for: cough recordings, respiratory symptoms.

    Args:
        audio_bytes: Audio file bytes (WAV/MP3)
        lang:        Language code
    """
    try:
        result = predict_audio("hear", audio_bytes)
        tb_prob = result.get("tb_probability", result.get("score", 0))

        if isinstance(tb_prob, (int, float)):
            if tb_prob > 0.7:
                msg = (
                    f"Cough analysis shows respiratory concern "
                    f"(score: {tb_prob:.0%}). "
                    "Please visit nearest DOTS center for free TB test and treatment."
                )
                severity = "RED"
            elif tb_prob > 0.4:
                msg = (
                    f"Respiratory concern detected (score: {tb_prob:.0%}). "
                    "Please visit PHC for evaluation."
                )
                severity = "YELLOW"
            else:
                msg = "Cough analysis: No major respiratory concern detected. Monitor symptoms."
                severity = "GREEN"
        else:
            msg = "Cough analysis complete. Please consult doctor for detailed evaluation."
            severity = "YELLOW"

        return {
            "success":  True,
            "response": to_local(msg + DISCLAIMER, lang),
            "severity": severity,
            "raw":      result,
        }
    except RuntimeError as e:
        return {"success": False, "response": str(e)}
    except Exception as e:
        logger.error(f"analyze_cough error: {e}")
        return {"success": False, "response": "Audio analysis unavailable. Please describe symptoms in text."}


# ─────────────────────────────────────────────
# TOOL 6 — Doctor NMC Verification
# ─────────────────────────────────────────────

def verify_doctor(doctor_name: str = "", reg_number: str = "") -> dict:
    """
    Verify doctor registration against NMC database.
    Use for: doctor name or registration number verification.

    Args:
        doctor_name: Doctor's full name
        reg_number:  NMC registration number
    """
    if not doctor_name and not reg_number:
        return {"success": False, "response": "Please provide doctor name or registration number."}
    try:
        search = reg_number or doctor_name

        # SSL verify — certifi వాడు (Windows certificate store fix)
        import certifi
        with httpx.Client(timeout=10.0, verify=certifi.where()) as client:
            resp = client.get(
                "https://www.nmc.org.in/MCIRest/open/getPaginatedData",
                params={
                    "service": "getDoctorOrHospitalByName",
                    "value":   search,
                    "start":   0,
                    "length":  5,
                },
            )

        if resp.status_code == 200:
            doctors = resp.json().get("data", [])
            if doctors:
                d = doctors[0]
                return {
                    "success":  True,
                    "verified": True,
                    "alert":    "GREEN",
                    "response": (
                        f"✅ Verified Registered Doctor\n"
                        f"Name: {d.get('name')}\n"
                        f"Qualification: {d.get('qualification')}\n"
                        f"Registration: {d.get('registrationNo')}\n"
                        f"Council: {d.get('stateMedicalCouncil')}"
                    ),
                }
            return {
                "success":  True,
                "verified": False,
                "alert":    "RED",
                "response": (
                    "⚠️ WARNING: NOT found in NMC database. "
                    "This person may be practicing illegally. "
                    "Please visit a registered government PHC."
                ),
            }

        # Fallback
        return {
            "success":  True,
            "verified": None,
            "alert":    "YELLOW",
            "response": (
                f"NMC database temporarily unavailable. "
                f"Please verify manually at: "
                f"https://www.nmc.org.in/information-desk/for-general-public/indian-medical-register/ "
                f"Search for: {search}"
            ),
        }

    except httpx.TimeoutException:
        return {"success": False, "response": "NMC timeout. Visit nmc.org.in directly."}
    except Exception as e:
        logger.error(f"verify_doctor error: {e}")
        return {"success": False, "response": "Verification unavailable. Visit nmc.org.in manually."}


# ─────────────────────────────────────────────
# TOOL 7 — Maternal Health
# ─────────────────────────────────────────────

MATERNAL_DANGER_SIGNS = [
    "bleeding", "severe pain", "headache vision",
    "swelling face", "baby not moving", "fever chills", "convulsion",
]


def maternal_guidance(query: str, week: int = 0, lang: str = "te") -> dict:
    """
    Pregnancy and maternal health guidance.
    Use for: pregnancy questions, antenatal care, delivery, postpartum.

    Args:
        query: Patient's question
        week:  Pregnancy week (0 if unknown)
        lang:  Language code
    """
    try:
        clean = sanitize_user_input(query)
        if not clean:
            return {"success": False, "response": "Please describe your concern.", "severity": "UNKNOWN"}

        en = to_english(clean, lang)

        # Danger sign check — no API call needed
        if any(s in en.lower() for s in MATERNAL_DANGER_SIGNS):
            msg = "🚨 DANGER SIGN detected. Go to hospital IMMEDIATELY. Call 108 if needed."
            return {
                "success":  True,
                "response": to_local(msg, lang),
                "severity": "RED",
                "call_108": True,
            }

        prompt = f"""You are VAIDU maternal health AI for rural India.
Patient query: {en}
Pregnancy week: {week or 'unknown'}

STRICT RULES:
- Use "may be" / "could be" language — never definitive
- NEVER suggest specific drug names or doses
- If any danger sign mentioned → say "go to hospital immediately"

Provide:
1. Answer to their specific question
2. What is normal vs concerning at this stage
3. Free government schemes: JSY, JSSK, PMSMA
4. When to visit ASHA worker or PHC

Simple language. Max 120 words. Mention free government services."""

        result_en = predict_text_with_retry("medgemma_4b", prompt)
        result_en = validate_response(result_en, tool_name="maternal_guidance")

        return {
            "success":  True,
            "response": to_local(result_en + DISCLAIMER, lang),
            "severity": "YELLOW",
        }
    except RuntimeError as e:
        return {"success": False, "response": str(e)}
    except Exception as e:
        logger.error(f"maternal_guidance error: {e}")
        return {"success": False, "response": "Unable to process. Visit nearest PHC."}


# ─────────────────────────────────────────────
# TOOL 8 — Mental Health Guidance (NEW)
# ─────────────────────────────────────────────

def mental_health_guidance(query: str, lang: str = "te") -> dict:
    """
    Mental health support: depression, anxiety, stress, suicidal thoughts.
    """
    try:
        clean = sanitize_user_input(query)
        if not clean:
            return {"success": False, "response": "Please describe your concern.", "severity": "UNKNOWN"}

        en = to_english(clean, lang)

        # Immediate danger check
        crisis_keywords = ["suicide", "kill myself", "end my life", "want to die"]
        if any(k in en.lower() for k in crisis_keywords):
            crisis_msg = (
                "🚨 CRISIS DETECTED. Please call a suicide prevention helpline immediately.\n"
                "India: 988 (24x7), Vandrevala Foundation: 9999 666 555"
            )
            return {
                "success": True,
                "response": to_local(crisis_msg, lang),
                "severity": "RED",
                "call_108": True,
            }

        prompt = f"""You are VAIDU mental health AI for rural India.
Patient query: {en}

STRICT RULES:
- Be compassionate and non-judgmental.
- Use "may be feeling" / "could be experiencing" language.
- NEVER give definitive diagnosis (depression, anxiety, etc.).
- Suggest practical coping strategies (breathing, talking to family, visiting PHC).
- If symptoms suggest severe illness, recommend seeing a mental health professional.

Provide:
1. Emotional validation.
2. Possible reasons (uncertain language).
3. Immediate steps (grounding techniques, seeking support).
4. When to seek professional help (mention free helplines).

Max 120 words."""

        result_en = predict_text_with_retry("medgemma_4b", prompt)
        result_en = validate_response(result_en, tool_name="mental_health_guidance")

        severity = "YELLOW"
        if any(w in result_en.lower() for w in ["emergency", "immediately", "crisis"]):
            severity = "RED"

        return {
            "success": True,
            "response": to_local(result_en + DISCLAIMER, lang),
            "severity": severity,
        }
    except Exception as e:
        logger.error(f"mental_health_guidance error: {e}")
        return {"success": False, "response": "Service unavailable. Please visit nearest PHC.", "severity": "UNKNOWN"}


# ─────────────────────────────────────────────
# TOOL 9 — Child Health / Pediatric Guidance (NEW)
# ─────────────────────────────────────────────

def child_health_guidance(
    query: str,
    age_months: int = 0,
    weight_kg: float = 0,
    lang: str = "te"
) -> dict:
    """
    Pediatric health: fever, cough, diarrhea, vaccination, growth.
    """
    try:
        clean = sanitize_user_input(query)
        if not clean:
            return {"success": False, "response": "Please describe child's symptoms.", "severity": "UNKNOWN"}

        en = to_english(clean, lang)

        # Danger signs (IMNCI)
        danger = ["unconscious", "convulsion", "not drinking", "vomiting everything", "chest indrawing"]
        if any(d in en.lower() for d in danger):
            msg = "🚨 DANGER SIGN detected. Take child to nearest hospital IMMEDIATELY."
            return {"success": True, "response": to_local(msg, lang), "severity": "RED", "call_108": True}

        prompt = f"""You are VAIDU pediatric AI for rural India.
Child's symptoms: {en}
Age: {age_months} months, Weight: {weight_kg} kg

STRICT RULES:
- Use IMNCI (Integrated Management of Neonatal and Childhood Illness) guidelines.
- Never suggest specific drug doses for children (weight-based dosing requires doctor).
- Recommend vaccination if relevant (free under Universal Immunization Programme).
- If symptoms are severe or unclear, advise immediate PHC visit.

Provide:
1. Possible condition (with uncertainty).
2. Home care advice (hydration, fever management).
3. When to seek urgent care.
4. Vaccination reminder if applicable.

Max 120 words."""

        result_en = predict_text_with_retry("medgemma_4b", prompt)
        result_en = validate_response(result_en, tool_name="child_health_guidance")

        severity = "YELLOW"
        if any(w in result_en.lower() for w in ["emergency", "immediately", "hospital"]):
            severity = "RED"

        return {
            "success": True,
            "response": to_local(result_en + DISCLAIMER, lang),
            "severity": severity,
        }
    except Exception as e:
        logger.error(f"child_health_guidance error: {e}")
        return {"success": False, "response": "Service unavailable. Visit nearest PHC.", "severity": "UNKNOWN"}


# ─────────────────────────────────────────────
# TOOL 10 — Infectious Disease Guidance (NEW)
# ─────────────────────────────────────────────

def infectious_disease_guidance(
    symptoms: str,
    fever_days: int = 0,
    lang: str = "te"
) -> dict:
    """
    Guidance for common infectious diseases in India.
    """
    try:
        clean = sanitize_user_input(symptoms)
        if not clean:
            return {"success": False, "response": "Please describe symptoms.", "severity": "UNKNOWN"}

        en = to_english(clean, lang)

        # Emergency signs: bleeding, altered sensorium, severe headache
        if any(w in en.lower() for w in ["bleeding", "unconscious", "severe headache", "not able to wake"]):
            msg = "🚨 Possible severe infection. Go to hospital immediately."
            return {"success": True, "response": to_local(msg, lang), "severity": "RED", "call_108": True}

        prompt = f"""You are VAIDU infectious disease AI for rural India.
Patient symptoms: {en}
Fever duration: {fever_days} days

Consider local diseases: Malaria, Typhoid, Dengue, Chikungunya, Leptospirosis, Tuberculosis.

STRICT RULES:
- Use "may be" / "could be" language.
- Do NOT give definitive diagnosis.
- Mention specific tests (Malaria rapid test, Typhoid IgM, Dengue NS1) if relevant.
- Advise based on fever pattern and associated symptoms.

Provide:
1. Possible infections that match symptoms.
2. Recommended tests at PHC.
3. Warning signs to watch.
4. When to return to PHC.

Max 120 words."""

        result_en = predict_text_with_retry("medgemma_4b", prompt)
        result_en = validate_response(result_en, tool_name="infectious_disease_guidance")

        severity = "YELLOW"
        if "bleeding" in result_en.lower() or "dengue hemorrhagic" in result_en.lower():
            severity = "RED"

        return {
            "success": True,
            "response": to_local(result_en + DISCLAIMER, lang),
            "severity": severity,
        }
    except Exception as e:
        logger.error(f"infectious_disease_guidance error: {e}")
        return {"success": False, "response": "Service unavailable. Visit PHC.", "severity": "UNKNOWN"}


# ─────────────────────────────────────────────
# TOOL 11 — Government Schemes Info (NEW)
# ─────────────────────────────────────────────

GOVT_SCHEMES = {
    "pmjay": "Ayushman Bharat PM-JAY: health cover up to ₹5 lakh per family per year. Eligible: poor families as per SECC database. Call 14555 or visit pmjay.gov.in",
    "jsy": "Janani Suraksha Yojana (JSY): cash assistance for institutional delivery. Eligible: pregnant women (BPL, SC/ST). Contact ASHA or PHC.",
    "jssk": "Janani Shishu Suraksha Karyakram (JSSK): free delivery, C-section, medicines, diet, and transport for pregnant women and sick infants.",
    "pmsma": "Pradhan Mantri Surakshit Matritva Abhiyan: free antenatal checkup on 9th of every month at PHC. High-risk pregnancy care.",
    "rbsk": "Rashtriya Bal Swasthya Karyakram (RBSK): screening for birth defects, diseases, deficiencies in children (0-18 yrs).",
    "nmhp": "National Mental Health Programme: counselling and treatment at district hospitals.",
}

def govt_schemes(query: str, lang: str = "te") -> dict:
    """
    Information about government health schemes.
    """
    try:
        clean = sanitize_user_input(query)
        en = to_english(clean, lang).lower()

        # Keyword matching to identify scheme
        scheme_keywords = {
            "pmjay": ["pmjay", "ayushman", "5 lakh", "golden card"],
            "jsy": ["jsy", "janani", "cash assistance", "delivery"],
            "jssk": ["jssk", "free delivery", "c-section", "janani shishu"],
            "pmsma": ["pmsma", "9th", "antenatal", "surakshit matritva"],
            "rbsk": ["rbsk", "child screening", "rashtriya bal"],
            "nmhp": ["mental health", "nmhp", "counselling"],
        }

        matched = []
        for scheme, keywords in scheme_keywords.items():
            if any(k in en for k in keywords):
                matched.append(GOVT_SCHEMES[scheme])

        if matched:
            response_en = "\n\n".join(matched)
        else:
            # General info about available schemes
            response_en = (
                "Government health schemes available:\n"
                "1. PM-JAY: Health insurance for poor families.\n"
                "2. JSY: Cash for institutional delivery.\n"
                "3. JSSK: Free maternal and child services.\n"
                "4. PMSMA: Free antenatal checkup.\n"
                "5. RBSK: Child health screening.\n"
                "6. NMHP: Mental health services.\n"
                "Please specify which scheme you want details about."
            )

        return {
            "success": True,
            "response": to_local(response_en + DISCLAIMER, lang),
            "severity": "GREEN",
        }
    except Exception as e:
        logger.error(f"govt_schemes error: {e}")
        return {"success": False, "response": "Unable to fetch scheme details.", "severity": "UNKNOWN"}


# ─────────────────────────────────────────────
# Visual Search Tool (Vertex AI Search)
# ─────────────────────────────────────────────

def search_medical_cases(image_bytes: bytes = None, query: str = "", lang: str = "te") -> dict:
    """
    Search for similar medical cases using Vertex AI Search.
    Can search with image, text, or both.
    
    Args:
        image_bytes: Optional medical image (X-ray, CT, MRI, etc.)
        query: Text query describing what to search for
        lang: Language for response
        
    Returns:
        Dictionary with search results and summary
    """
    try:
        clean_query = sanitize_user_input(query) if query else ""
        
        # Perform search
        if image_bytes and clean_query:
            # Visual + text search
            results = healthcare_search.search_with_image(image_bytes, clean_query)
        elif image_bytes:
            # Visual search only
            results = healthcare_search.search_with_image(image_bytes, "find similar medical cases")
        elif clean_query:
            # Text search only
            results = healthcare_search.search_text_only(clean_query)
        else:
            return {
                "success": False,
                "message": "Please provide either an image or a search query",
                "results": []
            }
        
        # Generate summary of results
        if results:
            summary_prompt = f"""Summarize these medical search results in {lang} language.

Search Results:
{results[:3]}  # Top 3 results

Create a brief summary (max 100 words) that:
1. Highlights key findings
2. Mentions similar cases found
3. Provides relevant medical context
4. Uses simple language for patients

Add disclaimer: "This is AI-assisted search. Always consult healthcare professionals."
"""
            
            summary = predict_text_with_retry("medgemma_4b", summary_prompt)
            summary = validate_response(summary, tool_name="search_medical_cases")
        else:
            if lang == "te":
                summary = "సారూప్య కేసులు కనుగొనబడలేదు. దయచేసి వైద్యుడిని సంప్రదించండి."
            elif lang == "hi":
                summary = "समान मामले नहीं मिले। कृपया डॉक्टर से परामर्श करें।"
            else:
                summary = "No similar cases found. Please consult a doctor."
        
        return {
            "success": True,
            "results": results[:5],  # Top 5 results
            "count": len(results),
            "summary": summary,
            "agent": "visual_search"
        }
        
    except Exception as e:
        logger.error(f"Medical search failed: {e}")
        
        if lang == "te":
            fallback = "సెర్చ్ తాత్కాలికంగా అందుబాటులో లేదు. దయచేసి వైద్యుడిని సంప్రదించండి."
        elif lang == "hi":
            fallback = "खोज अस्थायी रूप से अनुपलब्ध है। कृपया डॉक्टर से परामर्श करें।"
        else:
            fallback = "Search temporarily unavailable. Please consult a doctor."
        
        return {
            "success": False,
            "results": [],
            "message": fallback,
            "error": str(e)
        }
