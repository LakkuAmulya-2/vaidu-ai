"""
Bill analysis agent using MedGemma for medical bill extraction and analysis.
"""
import json
import logging
from typing import Dict, List, Any
from utils.vertex_client import predict_image, predict_text_with_retry

logger = logging.getLogger(__name__)


def extract_bill_items(image_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Extract line items from a medical bill using MedGemma.
    
    Args:
        image_bytes: Image of the medical bill
        
    Returns:
        List of extracted items with details
    """
    prompt = """You are a medical billing expert. Analyze this medical bill image and extract all line items.

For each item, identify:
1. Item name (procedure, test, medicine, or service)
2. Quantity
3. Unit price
4. Total price
5. Item type (procedure/test/medicine/consultation/hospital_charge)
6. Date (if available)

Return ONLY valid JSON in this exact format:
{
  "hospital_name": "Hospital Name",
  "bill_number": "Bill Number",
  "bill_date": "DD/MM/YYYY",
  "patient_name": "Patient Name",
  "items": [
    {
      "name": "Item name",
      "quantity": 1,
      "unit_price": 100.0,
      "total_price": 100.0,
      "item_type": "procedure",
      "is_procedure": true
    }
  ],
  "subtotal": 1000.0,
  "tax": 100.0,
  "total": 1100.0
}

If you cannot read certain fields, use "Not available" for strings and 0 for numbers.
"""
    
    try:
        result = predict_image("medgemma_4b", image_bytes, prompt)
        
        # Try to parse JSON
        try:
            data = json.loads(result)
            return data
        except json.JSONDecodeError:
            # Try to extract JSON from text
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data
            else:
                logger.error(f"Could not parse JSON from response: {result}")
                return {
                    "hospital_name": "Not available",
                    "bill_number": "Not available",
                    "bill_date": "Not available",
                    "patient_name": "Not available",
                    "items": [],
                    "subtotal": 0,
                    "tax": 0,
                    "total": 0,
                    "error": "Could not extract bill information"
                }
    except Exception as e:
        logger.error(f"Error extracting bill items: {e}")
        return {
            "hospital_name": "Not available",
            "bill_number": "Not available",
            "bill_date": "Not available",
            "patient_name": "Not available",
            "items": [],
            "subtotal": 0,
            "tax": 0,
            "total": 0,
            "error": str(e)
        }


def compare_with_cghs(items: List[Dict[str, Any]], cghs_rates: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Compare bill items with CGHS rates to identify overcharges.
    
    Args:
        items: List of bill items
        cghs_rates: CGHS rate card dictionary
        
    Returns:
        List of overcharge details
    """
    overcharges = []
    
    for item in items:
        item_name = item.get("name", "").strip()
        charged_price = float(item.get("total_price", 0))
        
        # Try to find matching CGHS rate
        cghs_match = None
        for cghs_key, cghs_data in cghs_rates.items():
            if cghs_key.lower() in item_name.lower() or item_name.lower() in cghs_key.lower():
                cghs_match = cghs_data
                break
        
        if cghs_match:
            cghs_rate = float(cghs_match.get("cghs_rate", 0))
            quantity = int(item.get("quantity", 1))
            expected_price = cghs_rate * quantity
            
            if charged_price > expected_price:
                overcharge_amount = charged_price - expected_price
                overcharge_percentage = (overcharge_amount / expected_price) * 100 if expected_price > 0 else 0
                
                overcharges.append({
                    "item_name": item_name,
                    "charged_price": charged_price,
                    "cghs_rate": cghs_rate,
                    "expected_price": expected_price,
                    "overcharge_amount": overcharge_amount,
                    "overcharge_percentage": round(overcharge_percentage, 2),
                    "quantity": quantity,
                    "category": cghs_match.get("category", "Unknown")
                })
    
    return overcharges


def compare_medicine_prices(items: List[Dict[str, Any]], medicine_mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Compare medicine prices with NPPA rates and suggest generic alternatives.
    
    Args:
        items: List of bill items
        medicine_mapping: Medicine brand to generic mapping
        
    Returns:
        List of medicine price comparisons
    """
    medicine_comparisons = []
    
    for item in items:
        if item.get("item_type") != "medicine":
            continue
            
        item_name = item.get("name", "").strip()
        charged_price = float(item.get("unit_price", 0))
        quantity = int(item.get("quantity", 1))
        
        # Try to find matching medicine
        medicine_match = None
        for brand_name, medicine_data in medicine_mapping.items():
            if brand_name.lower() in item_name.lower():
                medicine_match = medicine_data
                medicine_match["brand_name"] = brand_name
                break
        
        if medicine_match:
            nppa_rate = float(medicine_match.get("nppa_rate", 0))
            generic_name = medicine_match.get("generic", "")
            
            if charged_price > nppa_rate:
                savings = (charged_price - nppa_rate) * quantity
                
                medicine_comparisons.append({
                    "brand_name": medicine_match.get("brand_name", item_name),
                    "generic_name": generic_name,
                    "charged_price": charged_price,
                    "nppa_rate": nppa_rate,
                    "quantity": quantity,
                    "total_charged": charged_price * quantity,
                    "total_nppa": nppa_rate * quantity,
                    "potential_savings": savings,
                    "category": medicine_match.get("category", "Unknown")
                })
    
    return medicine_comparisons


def generate_bill_summary(bill_data: Dict[str, Any], overcharges: List[Dict[str, Any]], 
                         medicine_comparisons: List[Dict[str, Any]], lang: str = "te") -> str:
    """
    Generate a human-readable summary of the bill analysis.
    
    Args:
        bill_data: Extracted bill data
        overcharges: List of overcharges
        medicine_comparisons: List of medicine price comparisons
        lang: Language code (te/hi/en)
        
    Returns:
        Summary text in requested language
    """
    total_overcharge = sum(item["overcharge_amount"] for item in overcharges)
    total_medicine_savings = sum(item["potential_savings"] for item in medicine_comparisons)
    total_potential_savings = total_overcharge + total_medicine_savings
    
    prompt = f"""Generate a clear, empathetic summary of this medical bill analysis in {lang} language.

Bill Details:
- Hospital: {bill_data.get('hospital_name', 'Not available')}
- Total Amount: ₹{bill_data.get('total', 0)}
- Number of items: {len(bill_data.get('items', []))}

Overcharges Found: {len(overcharges)}
Total Overcharge Amount: ₹{total_overcharge:.2f}

Medicine Savings Possible: {len(medicine_comparisons)}
Total Medicine Savings: ₹{total_medicine_savings:.2f}

Total Potential Savings: ₹{total_potential_savings:.2f}

Create a summary that:
1. Explains the findings in simple language
2. Highlights the most significant overcharges
3. Suggests generic medicine alternatives
4. Provides actionable next steps
5. Is empathetic and supportive

Keep it concise (max 200 words) and use simple language suitable for rural patients.
"""
    
    try:
        summary = predict_text_with_retry("medgemma_4b", prompt)
        return summary
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        if lang == "te":
            return "బిల్లు విశ్లేషణ పూర్తయింది. దయచేసి వివరాలను చూడండి."
        elif lang == "hi":
            return "बिल विश्लेषण पूर्ण हुआ। कृपया विवरण देखें।"
        else:
            return "Bill analysis completed. Please review the details."
