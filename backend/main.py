"""
main.py - FastAPI entry point with thread pool for image processing.
"""
import logging
import time
import uuid
import asyncio
import base64
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from agents.orchestrator import process_async
from agents.tools import (
    triage_symptoms, analyze_prescription, analyze_scan, analyze_skin,
    verify_doctor, maternal_guidance, mental_health_guidance,
    child_health_guidance, infectious_disease_guidance, govt_schemes
)
from agents.diabetes_graph import run_diabetes_workflow
from agents.bill_agent import extract_bill_items, compare_with_cghs, compare_medicine_prices, generate_bill_summary
from agents.necessity_agent import batch_verify_procedures, generate_necessity_report
from agents.insurance_agent import insurance_navigator
from agents.action_agent import generate_dispute_letter, generate_consumer_forum_guidance, generate_negotiation_script, generate_rights_awareness
from agents.live_agent import live_consultation_handler
from services.healthcare_search import healthcare_search
from utils.config import ALLOWED_ORIGINS, MAX_IMAGE_BYTES
from utils.sanitizer import sanitize_user_input
from utils.image_processor import process_upload
from utils.voice_processor import transcribe_audio, synthesize_speech
from utils.self_healing import auditor

executor = ThreadPoolExecutor(max_workers=4)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    from utils.vertex_client import init_endpoints
    init_endpoints()
    
    # Load CGHS rates and medicine mapping
    import json
    global cghs_rates, medicine_mapping
    try:
        with open("data/cghs_rates.json", "r", encoding="utf-8") as f:
            cghs_rates = json.load(f)
        with open("data/medicine_mapping.json", "r", encoding="utf-8") as f:
            medicine_mapping = json.load(f)
        logger.info("CGHS rates and medicine mapping loaded successfully.")
    except Exception as e:
        logger.warning(f"Could not load data files: {e}")
        cghs_rates = {}
        medicine_mapping = {}
    
    logger.info("VAIDU startup complete — Vertex AI endpoints initialized.")
    yield
    executor.shutdown(wait=True)
    logger.info("Thread pool shut down.")

# Global data stores
cghs_rates = {}
medicine_mapping = {}

app = FastAPI(title="VAIDU Medical AI", version="1.0.0", lifespan=lifespan)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"success": False, "response": "Too many requests. Please wait a moment and try again."})
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_methods=["POST", "GET"], allow_headers=["Content-Type"], allow_credentials=False)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        if request.url.path in ("/docs", "/redoc", "/openapi.json"):
            response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https://fastapi.tiangolo.com; connect-src 'self' https://cdn.jsdelivr.net"
        else:
            response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"
        return response
app.add_middleware(SecurityHeadersMiddleware)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    rid = str(uuid.uuid4())[:8]
    t0 = time.time()
    logger.info(f"[{rid}] → {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"[{rid}] ← {response.status_code} ({time.time() - t0:.2f}s)")
    return response

@app.exception_handler(Exception)
async def global_handler(req: Request, exc: Exception):
    logger.error(f"Unhandled: {exc}")
    return JSONResponse(status_code=500, content={"success": False, "response": "Service temporarily unavailable. Please try again."})

@app.get("/health")
def health():
    return {"status": "healthy", "service": "VAIDU Medical AI 🏥"}

@app.post("/chat")
@limiter.limit("15/minute")
async def chat(request: Request, message: str = Form(...), session_id: str = Form(None), lang: str = Form("te"), age: int = Form(0), is_pregnant: bool = Form(False)):
    clean_message = sanitize_user_input(message)
    if not clean_message:
        raise HTTPException(400, "Message cannot be empty.")
    if len(clean_message) > 2000:
        raise HTTPException(400, "Message too long. Max 2000 characters.")
    sid = session_id or str(uuid.uuid4())
    full_msg = f"[lang:{lang}][age:{age}][pregnant:{is_pregnant}] {clean_message}"
    response = await process_async(full_msg, session_id=sid)
    return {"success": True, "response": response, "session_id": sid}

@app.post("/triage")
@limiter.limit("10/minute")
async def triage(request: Request, symptoms: str = Form(...), lang: str = Form("te"), age: int = Form(0), is_pregnant: bool = Form(False)):
    clean = sanitize_user_input(symptoms)
    if not clean:
        raise HTTPException(400, "Please describe your symptoms.")
    return triage_symptoms(clean, age, is_pregnant, lang)

@app.post("/analyze/prescription")
@limiter.limit("10/minute")
async def prescription(request: Request, file: UploadFile = File(...), lang: str = Form("te")):
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(400, "Only JPG/PNG images allowed.")
    try:
        content = await asyncio.get_event_loop().run_in_executor(executor, process_upload, await file.read(), MAX_IMAGE_BYTES)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return analyze_prescription(content, lang)

@app.post("/analyze/scan")
@limiter.limit("10/minute")
async def scan(request: Request, 
               file: UploadFile = File(...), 
               scan_type: str = Form("xray"), 
               lang: str = Form("te"),
               enable_visual_qa: bool = Form(False),
               qa_query: str = Form("")):
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(400, "Only JPG/PNG images allowed.")
    try:
        content = await asyncio.get_event_loop().run_in_executor(executor, process_upload, await file.read(), MAX_IMAGE_BYTES)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return analyze_scan(content, scan_type, lang, enable_visual_qa, qa_query)

@app.post("/analyze/skin")
@limiter.limit("10/minute")
async def skin(request: Request, 
               file: UploadFile = File(...), 
               area: str = Form("skin"), 
               lang: str = Form("te"),
               enable_visual_qa: bool = Form(False),
               qa_query: str = Form("")):
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(400, "Only JPG/PNG images allowed.")
    try:
        content = await asyncio.get_event_loop().run_in_executor(executor, process_upload, await file.read(), MAX_IMAGE_BYTES)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return analyze_skin(content, area, lang, enable_visual_qa, qa_query)

@app.post("/diabetes")
@limiter.limit("5/minute")
async def diabetes(request: Request, query: str = Form(...), lang: str = Form("te"), age: int = Form(0), check_type: str = Form("general"), file: UploadFile = File(None)):
    clean_query = sanitize_user_input(query)
    if not clean_query:
        raise HTTPException(400, "Please describe your concern.")
    image_bytes = None
    if file:
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            raise HTTPException(400, "Only JPG/PNG images allowed.")
        try:
            image_bytes = await asyncio.get_event_loop().run_in_executor(executor, process_upload, await file.read(), MAX_IMAGE_BYTES)
        except ValueError as e:
            raise HTTPException(400, str(e))
    return run_diabetes_workflow(clean_query, lang, age, image_bytes, check_type)

@app.get("/verify/doctor")
@limiter.limit("20/minute")
async def verify(request: Request, name: str = None, reg: str = None):
    if not name and not reg:
        raise HTTPException(400, "Provide doctor name or registration number.")
    safe_name = sanitize_user_input(name or "", max_len=100)
    safe_reg = sanitize_user_input(reg or "", max_len=50)
    return verify_doctor(doctor_name=safe_name, reg_number=safe_reg)

@app.post("/maternal")
@limiter.limit("10/minute")
async def maternal(request: Request, query: str = Form(...), lang: str = Form("te"), week: int = Form(0)):
    clean = sanitize_user_input(query)
    if not clean:
        raise HTTPException(400, "Please describe your concern.")
    return maternal_guidance(clean, week, lang)

# Additional endpoints for new tools
@app.post("/mental-health")
@limiter.limit("10/minute")
async def mental_health(request: Request, query: str = Form(...), lang: str = Form("te")):
    clean = sanitize_user_input(query)
    if not clean:
        raise HTTPException(400, "Please describe your concern.")
    return mental_health_guidance(clean, lang)

@app.post("/child-health")
@limiter.limit("10/minute")
async def child_health(request: Request, query: str = Form(...), age_months: int = Form(0), weight_kg: float = Form(0), lang: str = Form("te")):
    clean = sanitize_user_input(query)
    if not clean:
        raise HTTPException(400, "Please describe child's symptoms.")
    return child_health_guidance(clean, age_months, weight_kg, lang)

@app.post("/infectious")
@limiter.limit("10/minute")
async def infectious(request: Request, symptoms: str = Form(...), fever_days: int = Form(0), lang: str = Form("te")):
    clean = sanitize_user_input(symptoms)
    if not clean:
        raise HTTPException(400, "Please describe symptoms.")
    return infectious_disease_guidance(clean, fever_days, lang)

@app.post("/govt-schemes")
@limiter.limit("20/minute")
async def govt_schemes_endpoint(request: Request, query: str = Form(...), lang: str = Form("te")):
    clean = sanitize_user_input(query)
    return govt_schemes(clean, lang)


# Voice endpoints
@app.post("/transcribe")
@limiter.limit("20/minute")
async def transcribe(request: Request, file: UploadFile = File(...), lang: str = Form("te")):
    """
    Convert audio to text using Google Cloud Speech-to-Text
    """
    if file.content_type not in ["audio/webm", "audio/wav", "audio/mp3", "audio/mpeg", "audio/ogg"]:
        raise HTTPException(400, "Only audio files allowed (webm, wav, mp3, ogg)")
    
    try:
        audio_bytes = await file.read()
        if len(audio_bytes) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(400, "Audio file too large. Max 10MB.")
        
        transcript = transcribe_audio(audio_bytes, lang)
        
        if not transcript:
            return {"success": False, "text": "", "message": "No speech detected"}
        
        return {"success": True, "text": transcript}
        
    except RuntimeError as e:
        logger.error(f"Transcription error: {e}")
        return {"success": False, "text": "", "message": str(e)}
    except Exception as e:
        logger.error(f"Transcribe endpoint error: {e}")
        raise HTTPException(500, "Transcription service unavailable")


@app.post("/synthesize")
@limiter.limit("30/minute")
async def synthesize(request: Request, text: str = Form(...), lang: str = Form("te")):
    """
    Convert text to speech using Google Cloud Text-to-Speech
    Returns base64-encoded MP3 audio
    """
    if not text or len(text) > 5000:
        raise HTTPException(400, "Text must be between 1 and 5000 characters")
    
    try:
        audio_bytes = synthesize_speech(text, lang)
        
        # Convert to base64 for JSON response
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        return {
            "success": True,
            "audio": audio_base64,
            "format": "mp3"
        }
        
    except RuntimeError as e:
        logger.error(f"Synthesis error: {e}")
        return {"success": False, "message": str(e)}
    except Exception as e:
        logger.error(f"Synthesize endpoint error: {e}")
        raise HTTPException(500, "Speech synthesis service unavailable")


# ============================================================================
# BillSaathi Endpoints
# ============================================================================

@app.post("/analyze-bill")
@limiter.limit("10/minute")
async def analyze_bill_endpoint(
    request: Request,
    file: UploadFile = File(...),
    diagnosis: str = Form(""),
    patient_name: str = Form(""),
    lang: str = Form("te")
):
    """
    Analyze medical bill for overcharges and medical necessity.
    """
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(400, "Only JPG/PNG images allowed.")
    
    try:
        # Process image
        content = await asyncio.get_event_loop().run_in_executor(
            executor, process_upload, await file.read(), MAX_IMAGE_BYTES
        )
        
        # Extract bill items
        bill_data = extract_bill_items(content)
        
        # Check for overcharges
        overcharges = compare_with_cghs(bill_data.get("items", []), cghs_rates)
        
        # Check medicine prices
        medicine_comparisons = compare_medicine_prices(bill_data.get("items", []), medicine_mapping)
        
        # Verify medical necessity for procedures
        procedures = [item for item in bill_data.get("items", []) if item.get("is_procedure", False)]
        necessity_results = []
        if procedures:
            necessity_results = batch_verify_procedures(
                procedures,
                diagnosis=sanitize_user_input(diagnosis),
                patient_context=f"Patient: {sanitize_user_input(patient_name)}",
                lang=lang
            )
        
        # Generate summary
        summary = generate_bill_summary(bill_data, overcharges, medicine_comparisons, lang)
        
        # Audit the results
        result = {
            "bill_data": bill_data,
            "overcharges": overcharges,
            "medicine_comparisons": medicine_comparisons,
            "necessity_results": necessity_results,
            "summary": summary,
            "total_potential_savings": sum(o.get("overcharge_amount", 0) for o in overcharges) + 
                                      sum(m.get("potential_savings", 0) for m in medicine_comparisons)
        }
        
        audited = auditor.audit_extraction(result)
        
        return {
            "success": True,
            "data": audited.get("validated_data", result),
            "confidence_score": audited.get("confidence_score", 1.0),
            "issues": audited.get("issues_found", [])
        }
        
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Bill analysis error: {e}")
        raise HTTPException(500, "Bill analysis service unavailable")


@app.post("/insurance-navigate")
@limiter.limit("10/minute")
async def insurance_navigate_endpoint(
    request: Request,
    policy_file: UploadFile = File(...),
    bill_data: str = Form(...),
    patient_name: str = Form(""),
    diagnosis: str = Form(""),
    lang: str = Form("te")
):
    """
    Navigate insurance coverage and generate claim documents.
    """
    if policy_file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(400, "Only JPG/PNG images allowed for policy document.")
    
    try:
        # Process policy image
        policy_content = await asyncio.get_event_loop().run_in_executor(
            executor, process_upload, await policy_file.read(), MAX_IMAGE_BYTES
        )
        
        # Parse bill data
        import json
        bill_dict = json.loads(bill_data)
        
        # Patient info
        patient_info = {
            "name": sanitize_user_input(patient_name),
            "diagnosis": sanitize_user_input(diagnosis)
        }
        
        # Run insurance navigation
        result = insurance_navigator(policy_content, bill_dict, patient_info, lang)
        
        return {
            "success": True,
            "data": result
        }
        
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid bill data format")
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Insurance navigation error: {e}")
        raise HTTPException(500, "Insurance navigation service unavailable")


@app.post("/dispute-letter")
@limiter.limit("10/minute")
async def dispute_letter_endpoint(
    request: Request,
    overcharge_items: str = Form(...),
    hospital_name: str = Form(""),
    patient_name: str = Form(""),
    bill_number: str = Form(""),
    bill_date: str = Form(""),
    lang: str = Form("te")
):
    """
    Generate dispute letter for overcharges.
    """
    try:
        import json
        overcharges = json.loads(overcharge_items)
        
        letter = generate_dispute_letter(
            overcharges,
            sanitize_user_input(hospital_name),
            sanitize_user_input(patient_name),
            sanitize_user_input(bill_number),
            sanitize_user_input(bill_date),
            lang
        )
        
        return {
            "success": True,
            "letter": letter
        }
        
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid overcharge items format")
    except Exception as e:
        logger.error(f"Dispute letter generation error: {e}")
        raise HTTPException(500, "Dispute letter service unavailable")


@app.post("/consumer-forum-guidance")
@limiter.limit("10/minute")
async def consumer_forum_endpoint(
    request: Request,
    case_details: str = Form(...),
    lang: str = Form("te")
):
    """
    Get consumer forum filing guidance.
    """
    try:
        import json
        case_dict = json.loads(case_details)
        
        guidance = generate_consumer_forum_guidance(case_dict, lang)
        
        return {
            "success": True,
            "guidance": guidance
        }
        
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid case details format")
    except Exception as e:
        logger.error(f"Consumer forum guidance error: {e}")
        raise HTTPException(500, "Consumer forum guidance service unavailable")


@app.post("/negotiation-script")
@limiter.limit("10/minute")
async def negotiation_script_endpoint(
    request: Request,
    overcharge_amount: float = Form(...),
    hospital_name: str = Form(""),
    leverage_points: str = Form("{}"),
    lang: str = Form("te")
):
    """
    Generate negotiation script for bill discussion.
    """
    try:
        import json
        leverage = json.loads(leverage_points)
        
        script = generate_negotiation_script(
            overcharge_amount,
            sanitize_user_input(hospital_name),
            leverage,
            lang
        )
        
        return {
            "success": True,
            "script": script
        }
        
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid leverage points format")
    except Exception as e:
        logger.error(f"Negotiation script generation error: {e}")
        raise HTTPException(500, "Negotiation script service unavailable")


@app.get("/patient-rights")
@limiter.limit("20/minute")
async def patient_rights_endpoint(request: Request, lang: str = "te"):
    """
    Get patient rights awareness information.
    """
    try:
        rights_info = generate_rights_awareness(lang)
        
        return {
            "success": True,
            "rights": rights_info
        }
        
    except Exception as e:
        logger.error(f"Patient rights generation error: {e}")
        raise HTTPException(500, "Patient rights service unavailable")


@app.post("/visual-qa")
@limiter.limit("10/minute")
async def visual_qa_endpoint(
    request: Request,
    file: UploadFile = File(...),
    query: str = Form(...)
):
    """
    Visual Q&A using Vertex AI Search.
    """
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(400, "Only JPG/PNG images allowed.")
    
    try:
        content = await asyncio.get_event_loop().run_in_executor(
            executor, process_upload, await file.read(), MAX_IMAGE_BYTES
        )
        
        clean_query = sanitize_user_input(query)
        if not clean_query:
            raise HTTPException(400, "Query cannot be empty")
        
        results = healthcare_search.search_with_image(content, clean_query)
        
        return {
            "success": True,
            "results": results,
            "search_available": healthcare_search.is_available()
        }
        
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Visual Q&A error: {e}")
        raise HTTPException(500, "Visual Q&A service unavailable")


# WebSocket endpoint for live consultation
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/live-consult/{session_id}")
async def live_consult_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for Gemini Live consultation.
    """
    await live_consultation_handler.handle_websocket(websocket, session_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
