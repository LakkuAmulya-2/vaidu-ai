"""
agents/diabetes_graph.py
LangGraph stateful workflow for diabetes patient journey.
State machine: Risk → Eye → Foot → Diet → Summary

Fixes applied:
    - sanitize_user_input() on all user inputs
    - validate_response() on all LLM outputs
    - Hallucination-resistant prompts
"""

import logging
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, START, END

from utils.vertex_client import predict_text, predict_image
from utils.config import DISCLAIMER
from utils.sanitizer import sanitize_user_input
from utils.response_validator import validate_response
from services.translation import to_english, to_local
from agents.amie_diagnostic import amie_agent

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# State Schema
# ─────────────────────────────────────────────

class DiabetesState(TypedDict):
    query:        str
    lang:         str
    age:          int
    image_bytes:  Optional[bytes]
    check_type:   str           # risk / retinopathy / foot / diet / full / diagnostic
    risk_result:  str
    eye_result:   str
    foot_result:  str
    diet_result:  str
    final:        str
    severity:     str
    error:        str
    # AMIE diagnostic fields
    amie_session_id: Optional[str]
    amie_state:   Optional[dict]
    diagnostic_mode: bool


# ─────────────────────────────────────────────
# Graph Nodes
# ─────────────────────────────────────────────

def node_risk_screen(state: DiabetesState) -> dict:
    """Step 1: Diabetes risk screening."""
    try:
        clean = sanitize_user_input(state["query"])
        en = to_english(clean, state["lang"])

        prompt = f"""Diabetes risk screening for rural India patient.
Patient info: {en}, Age: {state.get('age', 'unknown')}

STRICT RULES:
- Use "may suggest" / "could indicate" — never definitive
- NEVER say "you have diabetes"
- NEVER suggest specific insulin doses
- If unclear → say "please get blood sugar test at PHC"

Assess risk: LOW / MEDIUM / HIGH
Consider: family history, weight, thirst, urination, fatigue.
Recommend: NPCDCS free screening if MEDIUM/HIGH.
Max 80 words."""

        result = predict_text("medgemma_4b", prompt, max_tokens=300)
        result = validate_response(result, tool_name="node_risk_screen")

        severity = (
            "RED"    if "high"   in result.lower() else
            "YELLOW" if "medium" in result.lower() else
            "GREEN"
        )
        return {"risk_result": result, "severity": severity}

    except Exception as e:
        logger.error(f"node_risk_screen: {e}")
        return {
            "risk_result": "Risk screening unavailable. Please visit PHC for blood sugar test.",
            "severity":    "UNKNOWN",
            "error":       str(e),
        }


def node_eye_check(state: DiabetesState) -> dict:
    """Step 2: Diabetic retinopathy check (if image provided)."""
    try:
        if state.get("image_bytes") and state.get("check_type") in ["retinopathy", "full"]:
            prompt = """Analyze this retinal image for diabetic retinopathy.

STRICT RULES:
- If image quality poor → say "cannot assess, better image needed"
- Use "appears to show" / "possible" language
- NEVER give definitive grading without clear image
- Grade only if confident: No DR / Mild / Moderate / Severe / Proliferative

Describe: What you observe, urgency of ophthalmologist visit.
Simple language for rural patient."""

            result = predict_image("medgemma_4b", state["image_bytes"], prompt)
            result = validate_response(result, tool_name="node_eye_check")
        else:
            result = (
                "Eye photo not provided. "
                "Recommend annual retinal screening for all diabetic patients. "
                "Visit PHC or eye camp for free screening."
            )
        return {"eye_result": result}

    except Exception as e:
        logger.error(f"node_eye_check: {e}")
        return {"eye_result": "Eye analysis unavailable.", "error": str(e)}


def node_foot_check(state: DiabetesState) -> dict:
    """Step 3: Diabetic foot assessment (if image provided)."""
    try:
        if state.get("image_bytes") and state.get("check_type") in ["foot", "full"]:
            prompt = """Analyze this diabetic foot image.

STRICT RULES:
- Wagner scale (0-5) — state if uncertain
- Infection signs: look carefully, do not assume absent
- Be direct about urgency — diabetic foot worsens rapidly
- Action: home care / PHC / hospital / emergency 108

If image quality is poor → say "cannot assess clearly, visit PHC immediately to be safe"."""

            result = predict_image("medgemma_4b", state["image_bytes"], prompt)
            result = validate_response(result, tool_name="node_foot_check")
        else:
            result = (
                "Foot photo not provided. "
                "Daily foot inspection recommended for all diabetic patients. "
                "Check for: cuts, blisters, redness, swelling, numbness."
            )
        return {"foot_result": result}

    except Exception as e:
        logger.error(f"node_foot_check: {e}")
        return {"foot_result": "Foot analysis unavailable.", "error": str(e)}


def node_diet_advice(state: DiabetesState) -> dict:
    """Step 4: India-specific diabetes diet advice."""
    try:
        clean = sanitize_user_input(state["query"])
        en = to_english(clean, state["lang"])

        prompt = f"""Diabetes diet advice for Telugu/Indian rural patient.
Query context: {en}

STRICT RULES:
- Practical, affordable Indian foods only
- NEVER suggest supplements or specific medicine doses
- Keep advice realistic for rural household budget

Guidance:
- Eat more: ragi, vegetables, bitter gourd, drumstick
- Reduce: white rice, sugar, maida, fried food
- Simple affordable meal plan example
- Local foods that help control blood sugar
Max 80 words."""

        result = predict_text("medgemma_4b", prompt, max_tokens=300)
        result = validate_response(result, tool_name="node_diet_advice")
        return {"diet_result": result}

    except Exception as e:
        logger.error(f"node_diet_advice: {e}")
        return {"diet_result": "Diet advice unavailable.", "error": str(e)}


def node_amie_diagnostic(state: DiabetesState) -> dict:
    """AMIE diagnostic conversation node for complex cases."""
    try:
        if not state.get("diagnostic_mode", False):
            return {}  # Skip if not in diagnostic mode
        
        # Check if continuing existing session
        if state.get("amie_session_id"):
            # This would be called with patient answers
            # For now, just return existing state
            return {"amie_state": state.get("amie_state")}
        
        # Start new AMIE diagnostic conversation
        patient_context = {
            "age": state.get("age", 0),
            "medical_history": "Diabetes patient",
            "current_symptoms": state.get("query", "")
        }
        
        amie_state = amie_agent.start_diagnostic_conversation(
            initial_complaint=state.get("query", ""),
            patient_context=patient_context,
            lang=state.get("lang", "te")
        )
        
        return {
            "amie_session_id": amie_state.get("session_id"),
            "amie_state": amie_state
        }
        
    except Exception as e:
        logger.error(f"node_amie_diagnostic: {e}")
        return {"error": f"AMIE diagnostic error: {str(e)}"}


def node_summarize(state: DiabetesState) -> dict:
    """Step 5: Combine all results into final response."""
    parts = []
    
    # Check if AMIE diagnostic mode
    if state.get("diagnostic_mode") and state.get("amie_state"):
        # Return AMIE diagnostic summary
        summary = amie_agent.get_diagnostic_summary(
            state.get("amie_session_id"),
            state.get("lang", "te")
        )
        return {
            "final": summary,
            "severity": state.get("amie_state", {}).get("urgency", "MEDIUM")
        }
    
    # Regular diabetes workflow summary
    if state.get("risk_result"):
        parts.append(f"**Risk Assessment:**\n{state['risk_result']}")
    if state.get("eye_result"):
        parts.append(f"**Eye Health:**\n{state['eye_result']}")
    if state.get("foot_result"):
        parts.append(f"**Foot Health:**\n{state['foot_result']}")
    if state.get("diet_result"):
        parts.append(f"**Diet Guidance:**\n{state['diet_result']}")

    combined_en = "\n\n".join(parts) if parts else "Unable to complete assessment."
    combined_en += DISCLAIMER

    lang = state.get("lang", "te")
    final = to_local(combined_en, lang)

    # Severity escalation — check combined text for emergency keywords
    severity = state.get("severity", "GREEN")
    if any(w in combined_en.lower() for w in ["proliferative", "stage 4", "stage 5", "emergency"]):
        severity = "RED"

    return {"final": final, "severity": severity}


# ─────────────────────────────────────────────
# Routing Function
# ─────────────────────────────────────────────

def route_after_risk(state: DiabetesState) -> str:
    """
    Risk assessment తర్వాత ఏ node కి వెళ్ళాలో decide చేయి.

    "full" check_type:
        eye_check → foot_check → diet_advice → summarize
        (hardcoded edges handle foot+diet after eye — router only decides first branch)

    "retinopathy": eye_check → foot_check → diet_advice → summarize
    "foot":        foot_check → diet_advice → summarize
    "diet":        diet_advice → summarize
    default:       summarize
    """
    ct = state.get("check_type", "general")
    if ct in ["retinopathy", "full"]:
        return "eye_check"
    if ct == "foot":
        return "foot_check"
    if ct == "diet":
        return "diet_advice"
    return "summarize"


# ─────────────────────────────────────────────
# Build Graph
# ─────────────────────────────────────────────

def _build_diabetes_graph() -> StateGraph:
    g = StateGraph(DiabetesState)

    g.add_node("risk_screen",  node_risk_screen)
    g.add_node("eye_check",    node_eye_check)
    g.add_node("foot_check",   node_foot_check)
    g.add_node("diet_advice",  node_diet_advice)
    g.add_node("amie_diagnostic", node_amie_diagnostic)
    g.add_node("summarize",    node_summarize)

    g.add_edge(START, "risk_screen")

    g.add_conditional_edges(
        "risk_screen",
        route_after_risk,
        {
            "eye_check":   "eye_check",
            "foot_check":  "foot_check",
            "diet_advice": "diet_advice",
            "summarize":   "summarize",
        },
    )

    # Fixed pipeline after eye_check (covers "full" and "retinopathy")
    g.add_edge("eye_check",   "foot_check")
    g.add_edge("foot_check",  "diet_advice")
    g.add_edge("diet_advice", "amie_diagnostic")
    g.add_edge("amie_diagnostic", "summarize")
    g.add_edge("summarize",   END)

    return g.compile()


# Singleton — server start లో ఒకసారి build చేసి reuse చేయి
diabetes_graph = _build_diabetes_graph()


def run_diabetes_workflow(
    query: str,
    lang: str = "te",
    age: int = 0,
    image_bytes: bytes = None,
    check_type: str = "general",
    diagnostic_mode: bool = False,
    amie_session_id: str = None,
    amie_answers: dict = None,
) -> dict:
    """
    LangGraph diabetes workflow entry point.

    Args:
        query:       Patient question/symptoms
        lang:        Language code (te/hi/en etc.)
        age:         Patient age
        image_bytes: Optional retinal or foot photo
        check_type:  general / risk / retinopathy / foot / diet / full / diagnostic
        diagnostic_mode: Enable AMIE diagnostic conversation
        amie_session_id: Continue existing AMIE session
        amie_answers: Patient answers for AMIE questions

    Returns:
        {success, response, severity, agent, amie_state}
    """
    try:
        initial_state = {
            "query":       query,
            "lang":        lang,
            "age":         age,
            "image_bytes": image_bytes,
            "check_type":  check_type,
            "risk_result": "",
            "eye_result":  "",
            "foot_result": "",
            "diet_result": "",
            "final":       "",
            "severity":    "GREEN",
            "error":       "",
            "diagnostic_mode": diagnostic_mode,
            "amie_session_id": amie_session_id,
            "amie_state": None,
        }
        
        # If continuing AMIE conversation
        if amie_session_id and amie_answers:
            amie_state = amie_agent.continue_diagnostic_conversation(
                amie_session_id,
                amie_answers,
                lang
            )
            initial_state["amie_state"] = amie_state
        
        result = diabetes_graph.invoke(initial_state)
        
        response_data = {
            "success":  True,
            "response": result.get("final", ""),
            "severity": result.get("severity", "GREEN"),
            "agent":    "diabetes_langgraph",
        }
        
        # Include AMIE state if in diagnostic mode
        if diagnostic_mode and result.get("amie_state"):
            response_data["amie_state"] = result.get("amie_state")
            response_data["amie_session_id"] = result.get("amie_session_id")
        
        return response_data
        
    except Exception as e:
        logger.error(f"diabetes_graph error: {e}")
        return {
            "success":  False,
            "response": "Diabetes assessment unavailable. Please try again.",
            "agent":    "diabetes_langgraph",
        }
