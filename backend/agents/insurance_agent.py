"""
Insurance navigator agent using Gemini.
Helps patients understand insurance coverage and file claims.
"""
import json
import logging
from typing import Dict, Any, List
from utils.vertex_client import predict_text_with_retry, predict_image

logger = logging.getLogger(__name__)


def extract_policy_details(image_bytes: bytes) -> Dict[str, Any]:
    """
    Extract insurance policy details from policy document image.
    
    Args:
        image_bytes: Image of insurance policy document
        
    Returns:
        Dictionary with policy details
    """
    prompt = """Extract insurance policy details from this document.

Return ONLY valid JSON:
{
  "policy_number": "Policy number",
  "policy_holder": "Name",
  "insurance_company": "Company name",
  "policy_type": "Health/Mediclaim/etc",
  "sum_insured": 500000,
  "coverage_details": {
    "hospitalization": true,
    "pre_hospitalization_days": 30,
    "post_hospitalization_days": 60,
    "ambulance": true,
    "day_care_procedures": true,
    "room_rent_limit": 5000,
    "icu_limit": 10000
  },
  "exclusions": ["Pre-existing for 2 years", "Cosmetic surgery"],
  "copay_percentage": 10,
  "deductible": 0,
  "network_hospitals": "List or 'Network available'",
  "claim_process": "Cashless/Reimbursement"
}

If information is not visible, use null or empty values.
"""
    
    try:
        result = predict_image("medgemma_4b", image_bytes, prompt)
        
        try:
            data = json.loads(result)
            return data
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("Could not parse policy details")
    except Exception as e:
        logger.error(f"Error extracting policy details: {e}")
        return {
            "policy_number": "Not available",
            "policy_holder": "Not available",
            "insurance_company": "Not available",
            "policy_type": "Not available",
            "sum_insured": 0,
            "coverage_details": {},
            "exclusions": [],
            "copay_percentage": 0,
            "deductible": 0,
            "network_hospitals": "Not available",
            "claim_process": "Not available",
            "error": str(e)
        }


def check_coverage(policy_details: Dict[str, Any], bill_items: List[Dict[str, Any]], 
                   diagnosis: str = "", lang: str = "te") -> Dict[str, Any]:
    """
    Check if bill items are covered under the insurance policy.
    
    Args:
        policy_details: Extracted policy details
        bill_items: List of bill items
        diagnosis: Patient diagnosis
        lang: Language for explanation
        
    Returns:
        Coverage analysis
    """
    prompt = f"""You are an insurance claim expert for Indian health insurance policies.

Policy Details:
{json.dumps(policy_details, indent=2)}

Bill Items:
{json.dumps(bill_items, indent=2)}

Diagnosis: {diagnosis or "Not specified"}

Analyze coverage for each item and return ONLY valid JSON:
{{
  "overall_coverage": "covered/partially_covered/not_covered",
  "covered_amount": 50000.0,
  "patient_liability": 10000.0,
  "items_analysis": [
    {{
      "item_name": "Item name",
      "billed_amount": 5000.0,
      "covered": true,
      "covered_amount": 4500.0,
      "reason": "Explanation",
      "copay_applied": 10,
      "room_rent_limit_applied": false
    }}
  ],
  "exclusions_triggered": ["Any exclusions that apply"],
  "coverage_summary_english": "Summary in English",
  "coverage_summary_telugu": "తెలుగులో సారాంశం",
  "coverage_summary_hindi": "हिंदी में सारांश",
  "recommendations": ["Recommendation 1", "Recommendation 2"]
}}

Consider:
1. Policy limits (room rent, ICU, procedures)
2. Copay/deductible
3. Exclusions (pre-existing, waiting periods)
4. Sub-limits for specific procedures
5. Network vs non-network hospital
"""
    
    try:
        result = predict_text_with_retry("medgemma_4b", prompt)
        
        try:
            data = json.loads(result)
            
            # Select summary based on language
            if lang == "te":
                data["coverage_summary"] = data.get("coverage_summary_telugu", 
                                                    data.get("coverage_summary_english", ""))
            elif lang == "hi":
                data["coverage_summary"] = data.get("coverage_summary_hindi", 
                                                    data.get("coverage_summary_english", ""))
            else:
                data["coverage_summary"] = data.get("coverage_summary_english", "")
            
            return data
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                if lang == "te":
                    data["coverage_summary"] = data.get("coverage_summary_telugu", 
                                                        data.get("coverage_summary_english", ""))
                elif lang == "hi":
                    data["coverage_summary"] = data.get("coverage_summary_hindi", 
                                                        data.get("coverage_summary_english", ""))
                else:
                    data["coverage_summary"] = data.get("coverage_summary_english", "")
                return data
            else:
                raise ValueError("Could not parse coverage analysis")
    except Exception as e:
        logger.error(f"Error checking coverage: {e}")
        
        if lang == "te":
            summary = "కవరేజ్ విశ్లేషణ విఫలమైంది. దయచేసి బీమా కంపెనీని సంప్రదించండి."
        elif lang == "hi":
            summary = "कवरेज विश्लेषण विफल रहा। कृपया बीमा कंपनी से संपर्क करें।"
        else:
            summary = "Coverage analysis failed. Please contact insurance company."
        
        return {
            "overall_coverage": "unknown",
            "covered_amount": 0,
            "patient_liability": 0,
            "items_analysis": [],
            "exclusions_triggered": [],
            "coverage_summary": summary,
            "recommendations": [],
            "error": str(e)
        }


def generate_claim_documents(policy_details: Dict[str, Any], bill_data: Dict[str, Any],
                            coverage_analysis: Dict[str, Any], patient_info: Dict[str, Any],
                            lang: str = "te") -> Dict[str, str]:
    """
    Generate claim form and supporting letter.
    
    Args:
        policy_details: Policy details
        bill_data: Bill information
        coverage_analysis: Coverage analysis results
        patient_info: Patient information
        lang: Language for documents
        
    Returns:
        Dictionary with claim letter and checklist
    """
    prompt = f"""Generate insurance claim documents in {lang} language.

Policy: {policy_details.get('policy_number', 'N/A')}
Insurance Company: {policy_details.get('insurance_company', 'N/A')}
Patient: {patient_info.get('name', 'N/A')}
Hospital: {bill_data.get('hospital_name', 'N/A')}
Total Bill: ₹{bill_data.get('total', 0)}
Covered Amount: ₹{coverage_analysis.get('covered_amount', 0)}

Generate:
1. A formal claim letter that:
   - States policy number and patient details
   - Describes the medical condition and treatment
   - Lists all covered expenses
   - Requests timely processing
   - Is polite and professional
   - Minimizes rejection risk by addressing common issues

2. A document checklist

Return as JSON:
{{
  "claim_letter": "Full letter text",
  "document_checklist": [
    "Document 1",
    "Document 2"
  ],
  "submission_instructions": "How to submit",
  "follow_up_tips": ["Tip 1", "Tip 2"]
}}
"""
    
    try:
        result = predict_text_with_retry("medgemma_4b", prompt)
        
        try:
            data = json.loads(result)
            return data
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("Could not parse claim documents")
    except Exception as e:
        logger.error(f"Error generating claim documents: {e}")
        
        if lang == "te":
            letter = "క్లెయిమ్ లేఖ రూపొందించడంలో లోపం. దయచేసి బీమా కంపెనీ వెబ్‌సైట్ నుండి ఫారమ్ డౌన్‌లోడ్ చేయండి."
        elif lang == "hi":
            letter = "दावा पत्र बनाने में त्रुटि। कृपया बीमा कंपनी की वेबसाइट से फॉर्म डाउनलोड करें।"
        else:
            letter = "Error generating claim letter. Please download form from insurance company website."
        
        return {
            "claim_letter": letter,
            "document_checklist": [],
            "submission_instructions": "",
            "follow_up_tips": [],
            "error": str(e)
        }


def insurance_navigator(policy_image: bytes, bill_data: Dict[str, Any], 
                       patient_info: Dict[str, Any], lang: str = "te") -> Dict[str, Any]:
    """
    Complete insurance navigation workflow.
    
    Args:
        policy_image: Image of insurance policy
        bill_data: Bill analysis data
        patient_info: Patient information
        lang: Language preference
        
    Returns:
        Complete insurance navigation results
    """
    # Extract policy details
    policy_details = extract_policy_details(policy_image)
    
    # Check coverage
    coverage_analysis = check_coverage(
        policy_details, 
        bill_data.get("items", []),
        patient_info.get("diagnosis", ""),
        lang
    )
    
    # Generate claim documents
    claim_documents = generate_claim_documents(
        policy_details,
        bill_data,
        coverage_analysis,
        patient_info,
        lang
    )
    
    return {
        "policy_details": policy_details,
        "coverage_analysis": coverage_analysis,
        "claim_documents": claim_documents,
        "estimated_reimbursement": coverage_analysis.get("covered_amount", 0),
        "patient_liability": coverage_analysis.get("patient_liability", 0)
    }
