"""
AMIE (Articulate Medical Intelligence Explorer) Diagnostic Agent
Implements iterative diagnostic conversation with differential diagnosis tracking.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from utils.vertex_client import predict_text_with_retry

logger = logging.getLogger(__name__)


class AMIEDiagnosticAgent:
    """
    AMIE-style diagnostic conversation agent.
    Implements iterative questioning and differential diagnosis.
    """
    
    def __init__(self):
        self.conversation_states = {}
    
    def start_diagnostic_conversation(self, 
                                     initial_complaint: str,
                                     patient_context: Dict[str, Any],
                                     lang: str = "te") -> Dict[str, Any]:
        """
        Start a new diagnostic conversation.
        
        Args:
            initial_complaint: Patient's initial complaint
            patient_context: Age, gender, medical history, etc.
            lang: Language for conversation
            
        Returns:
            Diagnostic state with questions and differential diagnoses
        """
        session_id = f"amie_{hash(initial_complaint)}_{patient_context.get('age', 0)}"
        
        prompt = f"""You are an expert diagnostic physician using the AMIE approach.

Patient Context:
- Age: {patient_context.get('age', 'Unknown')}
- Gender: {patient_context.get('gender', 'Unknown')}
- Pregnant: {patient_context.get('is_pregnant', False)}
- Medical History: {patient_context.get('medical_history', 'None provided')}

Initial Complaint: {initial_complaint}

Your task:
1. Generate a differential diagnosis list (top 5 most likely conditions)
2. For each diagnosis, assign a probability (0-100%)
3. Identify the most critical questions to ask next (3-5 questions)
4. Determine urgency level (LOW/MEDIUM/HIGH/CRITICAL)

Return ONLY valid JSON:
{{
  "differential_diagnoses": [
    {{
      "condition": "Condition name",
      "probability": 75,
      "reasoning": "Why this is likely",
      "red_flags": ["Red flag 1", "Red flag 2"],
      "typical_presentation": "How it typically presents"
    }}
  ],
  "next_questions": [
    {{
      "question_english": "Question in English",
      "question_telugu": "ప్రశ్న తెలుగులో",
      "question_hindi": "हिंदी में सवाल",
      "purpose": "Why asking this",
      "expected_answers": ["Option 1", "Option 2"]
    }}
  ],
  "urgency": "MEDIUM",
  "reasoning": "Overall diagnostic reasoning",
  "recommended_tests": ["Test 1", "Test 2"],
  "immediate_actions": ["Action 1 if urgent"]
}}

Use Indian medical context and guidelines (IMNCI, WHO India).
"""
        
        try:
            result = predict_text_with_retry("medgemma_4b", prompt)
            
            # Parse JSON
            try:
                diagnostic_state = json.loads(result)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    diagnostic_state = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse diagnostic response")
            
            # Store state
            diagnostic_state["session_id"] = session_id
            diagnostic_state["conversation_history"] = [
                {"role": "patient", "message": initial_complaint}
            ]
            diagnostic_state["iteration"] = 1
            
            self.conversation_states[session_id] = diagnostic_state
            
            return diagnostic_state
            
        except Exception as e:
            logger.error(f"Error starting diagnostic conversation: {e}")
            return self._fallback_diagnostic_state(initial_complaint, lang)
    
    def continue_diagnostic_conversation(self,
                                        session_id: str,
                                        answers: Dict[str, str],
                                        lang: str = "te") -> Dict[str, Any]:
        """
        Continue diagnostic conversation with patient's answers.
        
        Args:
            session_id: Session identifier
            answers: Patient's answers to previous questions
            lang: Language
            
        Returns:
            Updated diagnostic state
        """
        if session_id not in self.conversation_states:
            return {"error": "Session not found"}
        
        state = self.conversation_states[session_id]
        
        # Add answers to history
        for question, answer in answers.items():
            state["conversation_history"].append({
                "role": "physician",
                "message": question
            })
            state["conversation_history"].append({
                "role": "patient",
                "message": answer
            })
        
        # Update differential diagnosis
        prompt = f"""You are continuing a diagnostic conversation.

Previous State:
{json.dumps(state, indent=2)}

New Information (Patient's Answers):
{json.dumps(answers, indent=2)}

Based on the new information:
1. Update differential diagnosis probabilities
2. Add or remove diagnoses as needed
3. Generate next set of questions (if diagnosis not clear)
4. If diagnosis is clear (>80% confidence), provide final diagnosis
5. Update urgency level

Return ONLY valid JSON with same structure as before, plus:
{{
  "diagnosis_clear": true/false,
  "final_diagnosis": "Diagnosis if clear",
  "confidence": 0-100,
  "treatment_plan": "Treatment if diagnosis clear",
  ...rest of previous structure...
}}
"""
        
        try:
            result = predict_text_with_retry("medgemma_4b", prompt)
            
            try:
                updated_state = json.loads(result)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    updated_state = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse diagnostic response")
            
            # Merge with existing state
            updated_state["session_id"] = session_id
            updated_state["conversation_history"] = state["conversation_history"]
            updated_state["iteration"] = state["iteration"] + 1
            
            self.conversation_states[session_id] = updated_state
            
            return updated_state
            
        except Exception as e:
            logger.error(f"Error continuing diagnostic conversation: {e}")
            return state
    
    def get_diagnostic_summary(self, session_id: str, lang: str = "te") -> str:
        """
        Generate a summary of the diagnostic conversation.
        
        Args:
            session_id: Session identifier
            lang: Language for summary
            
        Returns:
            Summary text
        """
        if session_id not in self.conversation_states:
            return "Session not found"
        
        state = self.conversation_states[session_id]
        
        prompt = f"""Generate a clear, empathetic diagnostic summary in {lang} language.

Diagnostic State:
{json.dumps(state, indent=2)}

Create a summary that:
1. Explains the most likely diagnosis in simple terms
2. Lists key symptoms that led to this conclusion
3. Explains recommended tests/treatment
4. Provides reassurance and next steps
5. Mentions when to seek immediate care

Keep it under 200 words, use simple language suitable for rural patients.
"""
        
        try:
            summary = predict_text_with_retry("medgemma_4b", prompt)
            return summary
        except Exception as e:
            logger.error(f"Error generating diagnostic summary: {e}")
            
            if lang == "te":
                return "రోగ నిర్ధారణ సారాంశం రూపొందించడంలో లోపం. దయచేసి వైద్యుడిని సంప్రదించండి."
            elif lang == "hi":
                return "निदान सारांश बनाने में त्रुटि। कृपया डॉक्टर से परामर्श करें।"
            else:
                return "Error generating diagnostic summary. Please consult a doctor."
    
    def _fallback_diagnostic_state(self, complaint: str, lang: str) -> Dict[str, Any]:
        """Fallback diagnostic state when AI fails."""
        
        if lang == "te":
            message = "రోగ నిర్ధారణ ప్రారంభించడంలో లోపం. దయచేసి వైద్యుడిని సంప్రదించండి."
        elif lang == "hi":
            message = "निदान शुरू करने में त्रुटि। कृपया डॉक्टर से परामर्श करें।"
        else:
            message = "Error starting diagnostic conversation. Please consult a doctor."
        
        return {
            "error": message,
            "differential_diagnoses": [],
            "next_questions": [],
            "urgency": "MEDIUM",
            "recommended_tests": [],
            "immediate_actions": ["Consult a healthcare provider"]
        }


# Singleton instance
amie_agent = AMIEDiagnosticAgent()
