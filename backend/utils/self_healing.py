"""
Self-healing auditor for medical data validation and error correction.
Implements multi-stage validation pipeline with fallback mechanisms.
"""
import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class MedicalAuditor:
    """
    Auditor for validating and correcting medical data extraction results.
    """
    
    def __init__(self):
        self.fallback_responses = {
            "structural": "Doctor review recommended due to unclear information.",
            "hallucination": "This suggestion may not be accurate. Please verify with your doctor.",
            "incomplete": "Some information could not be extracted. Please verify manually.",
            "confidence_low": "Low confidence in analysis. Please consult healthcare professional."
        }
        
        # Overconfident phrases that indicate potential hallucination
        self.overconfident_phrases = [
            "definitely", "100%", "guaranteed", "certainly", "absolutely",
            "without doubt", "for sure", "no question", "undoubtedly"
        ]
        
        # Medical terms that should be present in valid medical data
        self.medical_indicators = [
            "patient", "diagnosis", "treatment", "procedure", "medicine",
            "test", "hospital", "doctor", "consultation", "surgery"
        ]
    
    def audit_extraction(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main audit pipeline for extracted medical data.
        
        Args:
            extracted_data: Data extracted by AI models
            
        Returns:
            Validated and corrected data with audit metadata
        """
        audit_results = {
            "original_data": extracted_data,
            "validation_passed": True,
            "issues_found": [],
            "corrections_applied": [],
            "confidence_score": 1.0
        }
        
        # Stage 1: Structural validation
        structural_valid, structural_issues = self._validate_structure(extracted_data)
        if not structural_valid:
            audit_results["validation_passed"] = False
            audit_results["issues_found"].extend(structural_issues)
            audit_results["confidence_score"] *= 0.5
            
            # Try to repair structure
            extracted_data = self._repair_structure(extracted_data, structural_issues)
            audit_results["corrections_applied"].append("structural_repair")
        
        # Stage 2: Hallucination detection
        hallucination_detected, hallucination_issues = self._detect_hallucination(extracted_data)
        if hallucination_detected:
            audit_results["validation_passed"] = False
            audit_results["issues_found"].extend(hallucination_issues)
            audit_results["confidence_score"] *= 0.7
            
            # Repair hallucinations
            extracted_data = self._repair_hallucination(extracted_data)
            audit_results["corrections_applied"].append("hallucination_repair")
        
        # Stage 3: Completeness check
        completeness_score, missing_fields = self._check_completeness(extracted_data)
        if completeness_score < 0.7:
            audit_results["issues_found"].append(f"Incomplete data: {missing_fields}")
            audit_results["confidence_score"] *= completeness_score
        
        # Stage 4: Consistency check
        consistency_valid, consistency_issues = self._check_consistency(extracted_data)
        if not consistency_valid:
            audit_results["issues_found"].extend(consistency_issues)
            audit_results["confidence_score"] *= 0.8
        
        # Stage 5: Add disclaimers based on confidence
        extracted_data = self._add_disclaimers(extracted_data, audit_results["confidence_score"])
        
        # Prepare final output
        audit_results["validated_data"] = extracted_data
        audit_results["status"] = "valid" if audit_results["validation_passed"] else "partial"
        
        return audit_results
    
    def _validate_structure(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate data structure against expected schema.
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Check if data is a dictionary
        if not isinstance(data, dict):
            issues.append("Data is not a dictionary")
            return False, issues
        
        # Check for required fields based on data type
        if "items" in data:
            # Bill data
            required_fields = ["items", "total"]
            for field in required_fields:
                if field not in data or data[field] is None:
                    issues.append(f"Missing required field: {field}")
        
        # Check if items is a list
        if "items" in data and not isinstance(data.get("items"), list):
            issues.append("'items' field is not a list")
        
        # Check for empty critical fields
        if "items" in data and len(data.get("items", [])) == 0:
            issues.append("No items extracted")
        
        return len(issues) == 0, issues
    
    def _detect_hallucination(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Detect potential hallucinations in the data.
        
        Returns:
            (hallucination_detected, list_of_issues)
        """
        issues = []
        data_str = str(data).lower()
        
        # Check for overconfident language
        for phrase in self.overconfident_phrases:
            if phrase in data_str:
                issues.append(f"Overconfident language detected: '{phrase}'")
        
        # Check for unrealistic values
        if "items" in data:
            for item in data.get("items", []):
                # Check for unrealistic prices
                price = item.get("total_price", 0)
                if isinstance(price, (int, float)) and price > 1000000:
                    issues.append(f"Unrealistic price detected: ₹{price}")
                
                # Check for negative prices
                if isinstance(price, (int, float)) and price < 0:
                    issues.append(f"Negative price detected: ₹{price}")
        
        # Check for total amount consistency
        if "items" in data and "total" in data:
            items_total = sum(item.get("total_price", 0) for item in data.get("items", []))
            declared_total = data.get("total", 0)
            
            if abs(items_total - declared_total) > declared_total * 0.2:  # 20% tolerance
                issues.append(f"Total mismatch: items sum to ₹{items_total} but total is ₹{declared_total}")
        
        return len(issues) > 0, issues
    
    def _check_completeness(self, data: Dict[str, Any]) -> tuple[float, List[str]]:
        """
        Check data completeness.
        
        Returns:
            (completeness_score, list_of_missing_fields)
        """
        missing_fields = []
        total_fields = 0
        present_fields = 0
        
        # Define expected fields based on data type
        if "items" in data:
            # Bill data
            expected_fields = ["hospital_name", "bill_number", "bill_date", "items", "total"]
            total_fields = len(expected_fields)
            
            for field in expected_fields:
                if field in data and data[field] not in [None, "", "Not available", []]:
                    present_fields += 1
                else:
                    missing_fields.append(field)
        
        elif "policy_number" in data:
            # Insurance policy data
            expected_fields = ["policy_number", "insurance_company", "sum_insured"]
            total_fields = len(expected_fields)
            
            for field in expected_fields:
                if field in data and data[field] not in [None, "", "Not available"]:
                    present_fields += 1
                else:
                    missing_fields.append(field)
        
        else:
            # Generic data
            total_fields = len(data)
            present_fields = sum(1 for v in data.values() if v not in [None, "", "Not available", []])
        
        completeness_score = present_fields / total_fields if total_fields > 0 else 0.0
        return completeness_score, missing_fields
    
    def _check_consistency(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Check internal consistency of data.
        
        Returns:
            (is_consistent, list_of_issues)
        """
        issues = []
        
        # Check date format consistency
        if "bill_date" in data:
            date_str = str(data.get("bill_date", ""))
            if date_str and date_str != "Not available":
                # Check if date matches common formats
                date_patterns = [
                    r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
                    r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                    r'\d{2}-\d{2}-\d{4}'   # DD-MM-YYYY
                ]
                if not any(re.match(pattern, date_str) for pattern in date_patterns):
                    issues.append(f"Invalid date format: {date_str}")
        
        # Check numeric consistency
        if "items" in data:
            for idx, item in enumerate(data.get("items", [])):
                quantity = item.get("quantity", 1)
                unit_price = item.get("unit_price", 0)
                total_price = item.get("total_price", 0)
                
                # Check if total = quantity * unit_price (with tolerance)
                expected_total = quantity * unit_price
                if abs(total_price - expected_total) > 1:  # ₹1 tolerance
                    issues.append(f"Item {idx}: Price inconsistency (qty={quantity}, unit={unit_price}, total={total_price})")
        
        return len(issues) == 0, issues
    
    def _repair_structure(self, data: Dict[str, Any], issues: List[str]) -> Dict[str, Any]:
        """
        Attempt to repair structural issues.
        """
        # Ensure items is a list
        if "items" in data and not isinstance(data.get("items"), list):
            data["items"] = []
        
        # Add missing required fields with default values
        if "items" in data and "total" not in data:
            data["total"] = sum(item.get("total_price", 0) for item in data.get("items", []))
        
        return data
    
    def _repair_hallucination(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove or flag hallucinated content.
        """
        data_str = str(data)
        
        # Remove overconfident phrases from string fields
        for key, value in data.items():
            if isinstance(value, str):
                for phrase in self.overconfident_phrases:
                    value = value.replace(phrase, "likely")
                    value = value.replace(phrase.capitalize(), "Likely")
                data[key] = value
        
        return data
    
    def _add_disclaimers(self, data: Dict[str, Any], confidence_score: float) -> Dict[str, Any]:
        """
        Add appropriate disclaimers based on confidence score.
        """
        if confidence_score < 0.5:
            data["disclaimer"] = "⚠️ Low confidence analysis. Please verify all information with a healthcare professional."
            data["confidence_level"] = "low"
        elif confidence_score < 0.7:
            data["disclaimer"] = "⚠️ This is AI-assisted analysis. Please confirm important details with your doctor."
            data["confidence_level"] = "medium"
        else:
            data["disclaimer"] = "ℹ️ This is AI-assisted analysis. Always consult healthcare professionals for medical decisions."
            data["confidence_level"] = "high"
        
        data["confidence_score"] = round(confidence_score, 2)
        
        return data
    
    def _trigger_fallback(self, reason: str) -> Dict[str, Any]:
        """
        Trigger fallback response when validation fails critically.
        """
        return {
            "status": "failed",
            "message": self.fallback_responses.get(reason, "Analysis failed. Please consult a healthcare professional."),
            "reason": reason,
            "validated_data": None
        }


# Singleton instance
auditor = MedicalAuditor()
