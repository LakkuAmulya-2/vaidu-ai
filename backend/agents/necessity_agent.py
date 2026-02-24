"""
Medical necessity verification agent using MedGemma.
Verifies if medical procedures are clinically justified based on standard guidelines.
"""
import json
import logging
from typing import Dict, Any
from utils.vertex_client import predict_image, predict_text_with_retry

logger = logging.getLogger(__name__)


def verify_medical_necessity(procedure_name: str, diagnosis: str = "", 
                            patient_context: str = "", lang: str = "te") -> Dict[str, Any]:
    """
    Verify if a medical procedure is clinically necessary based on diagnosis and guidelines.
    
    Args:
        procedure_name: Name of the procedure/test
        diagnosis: Patient's diagnosis (if known)
        patient_context: Additional patient context (age, symptoms, etc.)
        lang: Language for explanation
        
    Returns:
        Dictionary with necessity assessment
    """
    prompt = f"""You are a medical necessity expert following Indian clinical guidelines (IMNCI, WHO India, ICMR).

Procedure: {procedure_name}
Diagnosis: {diagnosis or "Not specified"}
Patient Context: {patient_context or "Not specified"}

Evaluate if this procedure is medically necessary based on:
1. Standard clinical guidelines
2. Evidence-based medicine
3. Cost-effectiveness
4. Availability of alternatives

Guidelines to consider:
- CT/MRI for headache: Only if red flags (sudden severe onset, neurological deficit, trauma) or failed conservative treatment
- ICU admission: Required only if organ support needed (ventilation, vasopressors), not for routine monitoring
- Multiple similar tests: Check for redundancy (e.g., multiple CT scans within short period)
- Expensive tests: Should have clear clinical indication, not "just to be safe"
- Antibiotics: Only for confirmed/suspected bacterial infections, not viral
- Imaging for minor injuries: X-ray sufficient in most cases, CT/MRI only if fracture suspected

Return ONLY valid JSON:
{{
  "is_necessary": true/false,
  "confidence": 0.0-1.0,
  "necessity_level": "essential/recommended/optional/unnecessary",
  "explanation_english": "Clear explanation in English",
  "explanation_telugu": "తెలుగులో వివరణ",
  "explanation_hindi": "हिंदी में स्पष्टीकरण",
  "guideline_reference": "Specific guideline reference",
  "alternatives": ["Alternative 1", "Alternative 2"],
  "red_flags": ["Any concerning findings that justify the procedure"],
  "cost_benefit": "Brief cost-benefit analysis"
}}

Be conservative but fair. If genuinely necessary, say so. If questionable, explain why.
"""
    
    try:
        result = predict_text_with_retry("medgemma_4b", prompt)
        
        # Parse JSON response
        try:
            data = json.loads(result)
            
            # Select explanation based on language
            if lang == "te":
                data["explanation"] = data.get("explanation_telugu", data.get("explanation_english", ""))
            elif lang == "hi":
                data["explanation"] = data.get("explanation_hindi", data.get("explanation_english", ""))
            else:
                data["explanation"] = data.get("explanation_english", "")
            
            return data
        except json.JSONDecodeError:
            # Try to extract JSON from text
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                if lang == "te":
                    data["explanation"] = data.get("explanation_telugu", data.get("explanation_english", ""))
                elif lang == "hi":
                    data["explanation"] = data.get("explanation_hindi", data.get("explanation_english", ""))
                else:
                    data["explanation"] = data.get("explanation_english", "")
                return data
            else:
                raise ValueError("Could not parse JSON response")
                
    except Exception as e:
        logger.error(f"Error verifying medical necessity: {e}")
        
        # Return safe fallback
        if lang == "te":
            explanation = "వైద్య అవసరతను నిర్ధారించలేకపోయాము. దయచేసి మీ వైద్యుడిని సంప్రదించండి."
        elif lang == "hi":
            explanation = "चिकित्सा आवश्यकता की पुष्टि नहीं कर सके। कृपया अपने डॉक्टर से परामर्श करें।"
        else:
            explanation = "Could not verify medical necessity. Please consult your doctor."
        
        return {
            "is_necessary": None,
            "confidence": 0.0,
            "necessity_level": "unknown",
            "explanation": explanation,
            "explanation_english": "Could not verify medical necessity. Please consult your doctor.",
            "explanation_telugu": "వైద్య అవసరతను నిర్ధారించలేకపోయాము. దయచేసి మీ వైద్యుడిని సంప్రదించండి.",
            "explanation_hindi": "चिकित्सा आवश्यकता की पुष्टि नहीं कर सके। कृपया अपने डॉक्टर से परामर्श करें।",
            "guideline_reference": "Unable to assess",
            "alternatives": [],
            "red_flags": [],
            "cost_benefit": "Unable to assess",
            "error": str(e)
        }


def batch_verify_procedures(procedures: list, diagnosis: str = "", 
                           patient_context: str = "", lang: str = "te") -> list:
    """
    Verify multiple procedures at once.
    
    Args:
        procedures: List of procedure names
        diagnosis: Patient's diagnosis
        patient_context: Additional context
        lang: Language for explanations
        
    Returns:
        List of necessity assessments
    """
    results = []
    
    for procedure in procedures:
        if isinstance(procedure, dict):
            procedure_name = procedure.get("name", "")
        else:
            procedure_name = str(procedure)
        
        if procedure_name:
            result = verify_medical_necessity(procedure_name, diagnosis, patient_context, lang)
            result["procedure_name"] = procedure_name
            results.append(result)
    
    return results


def generate_necessity_report(necessity_results: list, lang: str = "te") -> str:
    """
    Generate a summary report of all necessity checks.
    
    Args:
        necessity_results: List of necessity check results
        lang: Language for report
        
    Returns:
        Summary report text
    """
    essential_count = sum(1 for r in necessity_results if r.get("necessity_level") == "essential")
    recommended_count = sum(1 for r in necessity_results if r.get("necessity_level") == "recommended")
    optional_count = sum(1 for r in necessity_results if r.get("necessity_level") == "optional")
    unnecessary_count = sum(1 for r in necessity_results if r.get("necessity_level") == "unnecessary")
    
    prompt = f"""Generate a clear summary report of medical necessity verification in {lang} language.

Total Procedures Checked: {len(necessity_results)}
- Essential: {essential_count}
- Recommended: {recommended_count}
- Optional: {optional_count}
- Unnecessary: {unnecessary_count}

Create a brief report (max 150 words) that:
1. Summarizes the findings
2. Highlights any unnecessary procedures
3. Explains the implications for the patient
4. Suggests what questions to ask the doctor
5. Uses simple, empathetic language

Focus on empowering the patient to have informed conversations with their healthcare provider.
"""
    
    try:
        report = predict_text_with_retry("medgemma_4b", prompt)
        return report
    except Exception as e:
        logger.error(f"Error generating necessity report: {e}")
        if lang == "te":
            return "వైద్య అవసరత నివేదిక రూపొందించడంలో లోపం. దయచేసి వ్యక్తిగత ఫలితాలను చూడండి."
        elif lang == "hi":
            return "चिकित्सा आवश्यकता रिपोर्ट बनाने में त्रुटि। कृपया व्यक्तिगत परिणाम देखें।"
        else:
            return "Error generating necessity report. Please review individual results."
