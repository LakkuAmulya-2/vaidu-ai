"""
Action agent using Gemini for generating dispute letters and consumer forum guidance.
"""
import json
import logging
from typing import Dict, Any, List
from utils.vertex_client import predict_text_with_retry

logger = logging.getLogger(__name__)


def generate_dispute_letter(overcharge_items: List[Dict[str, Any]], 
                           hospital_name: str, 
                           patient_name: str,
                           bill_number: str,
                           bill_date: str,
                           lang: str = "te") -> str:
    """
    Generate a formal dispute letter for overcharges.
    
    Args:
        overcharge_items: List of overcharged items
        hospital_name: Name of the hospital
        patient_name: Patient's name
        bill_number: Bill number
        bill_date: Bill date
        lang: Language for letter
        
    Returns:
        Formatted dispute letter
    """
    total_overcharge = sum(item.get("overcharge_amount", 0) for item in overcharge_items)
    
    prompt = f"""Write a formal but polite dispute letter in {lang} language to the hospital billing department.

Hospital: {hospital_name}
Patient: {patient_name}
Bill Number: {bill_number}
Bill Date: {bill_date}

Overcharged Items:
{json.dumps(overcharge_items, indent=2)}

Total Overcharge: ₹{total_overcharge:.2f}

The letter should:
1. Be professional and respectful
2. Clearly state the overcharges with reference to CGHS rates
3. Request a revised bill or refund within 15 days
4. Mention willingness to escalate to consumer forum if not resolved
5. Include patient rights under Consumer Protection Act
6. Be firm but not aggressive
7. Use simple, clear language

Format as a proper business letter with:
- Date
- Hospital address section
- Subject line
- Body paragraphs
- Closing
- Signature line

Keep it concise (max 300 words).
"""
    
    try:
        letter = predict_text_with_retry("medgemma_4b", prompt)
        return letter
    except Exception as e:
        logger.error(f"Error generating dispute letter: {e}")
        
        if lang == "te":
            return f"""తేదీ: {bill_date}

ప్రతి,
బిల్లింగ్ విభాగం
{hospital_name}

విషయం: బిల్లు నంబర్ {bill_number} - అధిక ఛార్జీల గురించి

గౌరవనీయులు,

నేను {patient_name}, మీ ఆసుపత్రిలో చికిత్స పొందిన రోగిని. బిల్లు నంబర్ {bill_number}లో కొన్ని అధిక ఛార్జీలు గమనించాను.

CGHS రేట్ల ప్రకారం, మొత్తం అధిక ఛార్జీ: ₹{total_overcharge:.2f}

దయచేసి 15 రోజుల్లో సవరించిన బిల్లు లేదా రీఫండ్ అందించండి. లేకపోతే వినియోగదారుల ఫోరమ్‌కు వెళ్లవలసి ఉంటుంది.

ధన్యవాదాలు,
{patient_name}
"""
        elif lang == "hi":
            return f"""दिनांक: {bill_date}

सेवा में,
बिलिंग विभाग
{hospital_name}

विषय: बिल नंबर {bill_number} - अधिक शुल्क के बारे में

महोदय/महोदया,

मैं {patient_name}, आपके अस्पताल में इलाज कराने वाला मरीज हूं। बिल नंबर {bill_number} में कुछ अधिक शुल्क देखे गए हैं।

CGHS दरों के अनुसार, कुल अधिक शुल्क: ₹{total_overcharge:.2f}

कृपया 15 दिनों में संशोधित बिल या रिफंड प्रदान करें। अन्यथा उपभोक्ता फोरम में जाना होगा।

धन्यवाद,
{patient_name}
"""
        else:
            return f"""Date: {bill_date}

To,
Billing Department
{hospital_name}

Subject: Regarding Bill Number {bill_number} - Overcharges

Dear Sir/Madam,

I am {patient_name}, a patient treated at your hospital. I have noticed overcharges in Bill Number {bill_number}.

As per CGHS rates, Total Overcharge: ₹{total_overcharge:.2f}

Please provide a revised bill or refund within 15 days. Otherwise, I will be compelled to approach the consumer forum.

Thank you,
{patient_name}
"""


def generate_consumer_forum_guidance(case_details: Dict[str, Any], lang: str = "te") -> Dict[str, Any]:
    """
    Generate guidance for filing a consumer forum complaint.
    
    Args:
        case_details: Details of the case
        lang: Language for guidance
        
    Returns:
        Consumer forum guidance
    """
    prompt = f"""Provide step-by-step guidance for filing a consumer forum complaint in India in {lang} language.

Case Details:
{json.dumps(case_details, indent=2)}

Return ONLY valid JSON:
{{
  "eligibility": "Is this case eligible for consumer forum?",
  "appropriate_forum": "District/State/National - based on claim amount",
  "required_documents": ["Document 1", "Document 2"],
  "filing_process": ["Step 1", "Step 2"],
  "estimated_timeline": "Timeline estimate",
  "filing_fee": "Fee amount",
  "tips": ["Tip 1", "Tip 2"],
  "sample_complaint_format": "Brief format outline",
  "legal_provisions": ["Relevant sections of Consumer Protection Act"],
  "success_probability": "high/medium/low with explanation"
}}

Use simple language. Focus on practical, actionable steps.
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
                raise ValueError("Could not parse consumer forum guidance")
    except Exception as e:
        logger.error(f"Error generating consumer forum guidance: {e}")
        
        if lang == "te":
            message = "వినియోగదారుల ఫోరమ్ మార్గదర్శకత్వం రూపొందించడంలో లోపం. దయచేసి స్థానిక న్యాయ సహాయ కేంద్రాన్ని సంప్రదించండి."
        elif lang == "hi":
            message = "उपभोक्ता फोरम मार्गदर्शन बनाने में त्रुटि। कृपया स्थानीय कानूनी सहायता केंद्र से संपर्क करें।"
        else:
            message = "Error generating consumer forum guidance. Please contact local legal aid center."
        
        return {
            "eligibility": message,
            "appropriate_forum": "",
            "required_documents": [],
            "filing_process": [],
            "estimated_timeline": "",
            "filing_fee": "",
            "tips": [],
            "sample_complaint_format": "",
            "legal_provisions": [],
            "success_probability": "unknown",
            "error": str(e)
        }


def generate_negotiation_script(overcharge_amount: float, hospital_name: str, 
                               patient_leverage: Dict[str, Any], lang: str = "te") -> str:
    """
    Generate a negotiation script for discussing bill with hospital.
    
    Args:
        overcharge_amount: Total overcharge amount
        hospital_name: Hospital name
        patient_leverage: Patient's leverage points (insurance, CGHS rates, etc.)
        lang: Language for script
        
    Returns:
        Negotiation script
    """
    prompt = f"""Create a negotiation script in {lang} language for a patient to discuss bill overcharges with hospital billing department.

Overcharge Amount: ₹{overcharge_amount:.2f}
Hospital: {hospital_name}
Patient Leverage: {json.dumps(patient_leverage, indent=2)}

The script should:
1. Start with a polite, non-confrontational opening
2. Present facts clearly (CGHS rates, overcharges)
3. Show willingness to understand hospital's perspective
4. Propose reasonable solutions (revised bill, payment plan, partial refund)
5. Mention escalation options only as last resort
6. Use empathetic, respectful language
7. Be culturally appropriate for Indian context

Format as a conversation guide with:
- Opening statement
- Key points to make
- Questions to ask
- Responses to common objections
- Closing statement

Keep it practical and easy to follow (max 250 words).
"""
    
    try:
        script = predict_text_with_retry("medgemma_4b", prompt)
        return script
    except Exception as e:
        logger.error(f"Error generating negotiation script: {e}")
        
        if lang == "te":
            return f"""చర్చల స్క్రిప్ట్:

1. ప్రారంభం:
"నమస్కారం, నేను {hospital_name}లో చికిత్స పొందిన రోగిని. బిల్లు గురించి మాట్లాడాలనుకుంటున్నాను."

2. ముఖ్య అంశాలు:
- CGHS రేట్లతో పోల్చితే ₹{overcharge_amount:.2f} అధికంగా ఉంది
- సవరించిన బిల్లు అవసరం
- చెల్లింపు ప్రణాళిక సాధ్యమేనా?

3. ముగింపు:
"మీ సహకారం కోసం ధన్యవాదాలు. త్వరలో పరిష్కారం కోసం ఎదురు చూస్తున్నాను."
"""
        elif lang == "hi":
            return f"""बातचीत स्क्रिप्ट:

1. शुरुआत:
"नमस्ते, मैं {hospital_name} में इलाज कराने वाला मरीज हूं। बिल के बारे में बात करना चाहता हूं।"

2. मुख्य बिंदु:
- CGHS दरों की तुलना में ₹{overcharge_amount:.2f} अधिक है
- संशोधित बिल की आवश्यकता
- भुगतान योजना संभव है?

3. समापन:
"आपके सहयोग के लिए धन्यवाद। जल्द समाधान की उम्मीद है।"
"""
        else:
            return f"""Negotiation Script:

1. Opening:
"Hello, I am a patient treated at {hospital_name}. I'd like to discuss the bill."

2. Key Points:
- Compared to CGHS rates, there's an overcharge of ₹{overcharge_amount:.2f}
- Need for revised bill
- Is a payment plan possible?

3. Closing:
"Thank you for your cooperation. Looking forward to a resolution soon."
"""


def generate_rights_awareness(lang: str = "te") -> Dict[str, Any]:
    """
    Generate patient rights awareness content.
    
    Args:
        lang: Language for content
        
    Returns:
        Patient rights information
    """
    prompt = f"""Create patient rights awareness content in {lang} language for medical billing in India.

Return ONLY valid JSON:
{{
  "key_rights": [
    "Right 1 with brief explanation",
    "Right 2 with brief explanation"
  ],
  "what_to_do_if_overcharged": ["Step 1", "Step 2"],
  "red_flags": ["Warning sign 1", "Warning sign 2"],
  "resources": [
    {{"name": "Resource name", "description": "What it does", "contact": "How to reach"}}
  ],
  "common_myths": [
    {{"myth": "Common myth", "reality": "Actual fact"}}
  ]
}}

Focus on empowering patients with knowledge. Use simple, clear language.
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
                raise ValueError("Could not parse rights awareness content")
    except Exception as e:
        logger.error(f"Error generating rights awareness: {e}")
        return {
            "key_rights": [],
            "what_to_do_if_overcharged": [],
            "red_flags": [],
            "resources": [],
            "common_myths": [],
            "error": str(e)
        }
