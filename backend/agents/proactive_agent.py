"""
Proactive Agent for VAIDU - Handles emergency alerts and proactive interventions.
Production-ready implementation with no mock data.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ProactiveAgent:
    """
    Handles emergency situations and proactive health interventions.
    Triggered by Gemini Live API when critical conditions detected.
    """
    
    def __init__(self):
        self.emergency_log = []
    
    async def handle_red_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle RED severity emergency alert.
        
        Args:
            alert_data: {
                "reason": str - Emergency reason
                "severity": str - CRITICAL or HIGH
                "session_id": str - Session identifier
                "patient_context": dict - Optional patient info
            }
        
        Returns:
            Dictionary with emergency response actions
        """
        try:
            reason = alert_data.get("reason", "Unknown emergency")
            severity = alert_data.get("severity", "HIGH")
            session_id = alert_data.get("session_id", "unknown")
            
            logger.critical(
                f"RED ALERT - Session {session_id}: {severity} - {reason}"
            )
            
            # Log emergency
            self.emergency_log.append({
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "severity": severity,
                "reason": reason,
                "status": "triggered"
            })
            
            # Determine emergency actions based on reason
            actions = self._determine_emergency_actions(reason, severity)
            
            return {
                "success": True,
                "alert_triggered": True,
                "severity": severity,
                "reason": reason,
                "actions": actions,
                "emergency_number": "108",
                "message": self._get_emergency_message(reason, severity)
            }
            
        except Exception as e:
            logger.error(f"Proactive agent error: {e}")
            return {
                "success": False,
                "error": str(e),
                "actions": [
                    {
                        "action": "call_108",
                        "priority": "IMMEDIATE",
                        "message": "Emergency detected. Call 108 immediately."
                    }
                ]
            }
    
    def _determine_emergency_actions(
        self, 
        reason: str, 
        severity: str
    ) -> List[Dict[str, Any]]:
        """
        Determine appropriate emergency actions based on symptoms.
        """
        reason_lower = reason.lower()
        actions = []
        
        # Cardiac emergency
        if any(word in reason_lower for word in [
            "chest pain", "heart attack", "cardiac", "crushing pain"
        ]):
            actions.extend([
                {
                    "action": "call_108",
                    "priority": "IMMEDIATE",
                    "message": "Call 108 immediately - Possible heart attack"
                },
                {
                    "action": "aspirin",
                    "priority": "HIGH",
                    "message": "If available, chew 1 aspirin (300mg) while waiting"
                },
                {
                    "action": "position",
                    "priority": "HIGH",
                    "message": "Sit upright, loosen tight clothing"
                },
                {
                    "action": "monitor",
                    "priority": "MEDIUM",
                    "message": "Stay with patient, monitor breathing"
                }
            ])
        
        # Stroke
        elif any(word in reason_lower for word in [
            "stroke", "face droop", "arm weakness", "speech difficulty", "fast"
        ]):
            actions.extend([
                {
                    "action": "call_108",
                    "priority": "IMMEDIATE",
                    "message": "Call 108 immediately - Possible stroke (FAST symptoms)"
                },
                {
                    "action": "time",
                    "priority": "CRITICAL",
                    "message": "Note exact time symptoms started - critical for treatment"
                },
                {
                    "action": "position",
                    "priority": "HIGH",
                    "message": "Lie patient flat, turn head to side if vomiting"
                },
                {
                    "action": "no_food",
                    "priority": "HIGH",
                    "message": "Do NOT give food, water, or medicines"
                }
            ])
        
        # Severe bleeding
        elif any(word in reason_lower for word in [
            "bleeding", "hemorrhage", "blood loss"
        ]):
            actions.extend([
                {
                    "action": "call_108",
                    "priority": "IMMEDIATE",
                    "message": "Call 108 immediately - Severe bleeding"
                },
                {
                    "action": "pressure",
                    "priority": "CRITICAL",
                    "message": "Apply direct pressure to wound with clean cloth"
                },
                {
                    "action": "elevate",
                    "priority": "HIGH",
                    "message": "Elevate bleeding part above heart level if possible"
                },
                {
                    "action": "monitor",
                    "priority": "HIGH",
                    "message": "Watch for signs of shock (pale, cold, rapid pulse)"
                }
            ])
        
        # Breathing difficulty
        elif any(word in reason_lower for word in [
            "breathing", "dyspnea", "respiratory", "choking", "asthma"
        ]):
            actions.extend([
                {
                    "action": "call_108",
                    "priority": "IMMEDIATE",
                    "message": "Call 108 immediately - Breathing emergency"
                },
                {
                    "action": "position",
                    "priority": "CRITICAL",
                    "message": "Sit patient upright, lean slightly forward"
                },
                {
                    "action": "airway",
                    "priority": "HIGH",
                    "message": "Ensure airway is clear, loosen tight clothing"
                },
                {
                    "action": "inhaler",
                    "priority": "MEDIUM",
                    "message": "If asthma patient, help use inhaler"
                }
            ])
        
        # Unconscious/altered consciousness
        elif any(word in reason_lower for word in [
            "unconscious", "unresponsive", "coma", "seizure", "convulsion"
        ]):
            actions.extend([
                {
                    "action": "call_108",
                    "priority": "IMMEDIATE",
                    "message": "Call 108 immediately - Patient unconscious"
                },
                {
                    "action": "position",
                    "priority": "CRITICAL",
                    "message": "Place in recovery position (on side)"
                },
                {
                    "action": "airway",
                    "priority": "CRITICAL",
                    "message": "Check breathing, clear airway if needed"
                },
                {
                    "action": "protect",
                    "priority": "HIGH",
                    "message": "If seizure, protect head, do NOT restrain"
                }
            ])
        
        # Severe abdominal pain
        elif any(word in reason_lower for word in [
            "abdominal pain", "stomach pain", "appendicitis"
        ]):
            actions.extend([
                {
                    "action": "call_108",
                    "priority": "IMMEDIATE",
                    "message": "Call 108 immediately - Severe abdominal emergency"
                },
                {
                    "action": "position",
                    "priority": "HIGH",
                    "message": "Lie patient down, knees bent if comfortable"
                },
                {
                    "action": "no_food",
                    "priority": "HIGH",
                    "message": "Do NOT give food, water, or pain medicines"
                },
                {
                    "action": "monitor",
                    "priority": "MEDIUM",
                    "message": "Watch for vomiting, fever, or worsening pain"
                }
            ])
        
        # Maternal emergency
        elif any(word in reason_lower for word in [
            "pregnancy", "pregnant", "delivery", "labor", "bleeding pregnant"
        ]):
            actions.extend([
                {
                    "action": "call_108",
                    "priority": "IMMEDIATE",
                    "message": "Call 108 immediately - Pregnancy emergency"
                },
                {
                    "action": "position",
                    "priority": "HIGH",
                    "message": "Lie on left side if possible"
                },
                {
                    "action": "hospital",
                    "priority": "CRITICAL",
                    "message": "Go to nearest hospital with maternity ward"
                },
                {
                    "action": "asha",
                    "priority": "MEDIUM",
                    "message": "Contact ASHA worker if available"
                }
            ])
        
        # Generic critical emergency
        else:
            actions.extend([
                {
                    "action": "call_108",
                    "priority": "IMMEDIATE",
                    "message": "Call 108 immediately - Medical emergency"
                },
                {
                    "action": "stay_calm",
                    "priority": "HIGH",
                    "message": "Stay calm, keep patient comfortable"
                },
                {
                    "action": "monitor",
                    "priority": "HIGH",
                    "message": "Monitor breathing and consciousness"
                },
                {
                    "action": "hospital",
                    "priority": "HIGH",
                    "message": "Go to nearest hospital emergency department"
                }
            ])
        
        return actions
    
    def _get_emergency_message(self, reason: str, severity: str) -> str:
        """
        Get appropriate emergency message in Telugu.
        """
        if severity == "CRITICAL":
            return (
                f"🚨 అత్యవసర పరిస్థితి!\n\n"
                f"కారణం: {reason}\n\n"
                f"వెంటనే 108 కాల్ చేయండి!\n"
                f"రోగిని ఆసుపత్రికి తీసుకెళ్లండి.\n\n"
                f"ప్రాణాలకు ముప్పు ఉండవచ్చు - వెంటనే చర్య తీసుకోండి!"
            )
        else:
            return (
                f"⚠️ తీవ్రమైన వైద్య పరిస్థితి!\n\n"
                f"కారణం: {reason}\n\n"
                f"వెంటనే 108 కాల్ చేయండి లేదా సమీప ఆసుపత్రికి వెళ్లండి.\n"
                f"ఆలస్యం చేయవద్దు!"
            )
    
    def get_emergency_log(self, session_id: str = None) -> List[Dict[str, Any]]:
        """
        Get emergency log for a session or all sessions.
        """
        if session_id:
            return [
                log for log in self.emergency_log 
                if log.get("session_id") == session_id
            ]
        return self.emergency_log
    
    def clear_log(self):
        """Clear emergency log (for testing/maintenance)."""
        self.emergency_log = []


# Singleton instance
proactive_agent = ProactiveAgent()
