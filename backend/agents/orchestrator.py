"""
agents/orchestrator.py
Google ADK Master Orchestrator.

Fixes:
    - Session not found: create session before use
    - Removed asyncio.run (deadlock fix)
"""

import logging

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.tools import (
    triage_symptoms,
    analyze_prescription,
    analyze_scan,
    analyze_skin,
    analyze_cough,
    verify_doctor,
    maternal_guidance,
    mental_health_guidance,
    child_health_guidance,
    infectious_disease_guidance,
    govt_schemes,
)
from agents.diabetes_graph import run_diabetes_workflow

logger = logging.getLogger(__name__)

APP_NAME = "vaidu"

SYSTEM_INSTRUCTION = """You are VAIDU, an AI medical assistant for rural India.
You serve 700 million rural Indians who need healthcare guidance.

Route requests to the appropriate tool:
- Symptoms, fever, pain, general illness → triage_symptoms
- Prescription photo → analyze_prescription
- X-ray, CT, MRI, lab report → analyze_scan
- Skin rash, eye/retina, diabetic foot → analyze_skin
- Cough audio → analyze_cough
- Doctor name/registration verification → verify_doctor
- Pregnancy, maternal health → maternal_guidance
- Diabetes, blood sugar, insulin, HbA1c → run_diabetes_workflow
- Mental health (stress, anxiety, depression) → mental_health_guidance
- Child health (infants, children) → child_health_guidance
- Infectious diseases (malaria, typhoid, dengue) → infectious_disease_guidance
- Government health schemes → govt_schemes

ALWAYS:
- Use simple, non-technical language
- Add severity: GREEN (safe) / YELLOW (monitor) / RED (emergency)
- If RED: say "వెంటనే 108 call చేయండి"
- Never make definitive diagnosis
- Never suggest specific drug doses
- Respond in patient's language"""

TOOLS = [
    triage_symptoms,
    analyze_prescription,
    analyze_scan,
    analyze_skin,
    analyze_cough,
    verify_doctor,
    maternal_guidance,
    run_diabetes_workflow,
    mental_health_guidance,
    child_health_guidance,
    infectious_disease_guidance,
    govt_schemes,
]

vaidu_agent = LlmAgent(
    name="vaidu_orchestrator",
    model="gemini-2.0-flash",
    instruction=SYSTEM_INSTRUCTION,
    tools=TOOLS,
    description="VAIDU — AI Medical Assistant for Rural India",
)

session_service = InMemorySessionService()

runner = Runner(
    agent=vaidu_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


async def process_async(
    message: str,
    session_id: str,
    user_id: str = "patient",
) -> str:
    """
    ADK runner — async only.
    Session exist చేయకపోతే create చేస్తుంది.
    """
    try:
        # Session not found fix — create if not exists
        try:
            session_service.get_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id,
            )
        except Exception:
            session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id,
            )

        content = types.Content(
            role="user",
            parts=[types.Part(text=message)],
        )

        final_response = ""
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text

        return final_response or "Unable to process. Please try again."

    except Exception as e:
        logger.error(f"ADK orchestrator error: {e}")
        return "Service temporarily unavailable. Please visit nearest PHC."