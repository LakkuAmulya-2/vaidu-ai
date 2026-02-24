"""
utils/config.py
App configuration — environment variables, constants, emergency patterns.
"""
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT    = os.getenv("GOOGLE_CLOUD_PROJECT", "studio-2990104144-2fb17")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

ENDPOINTS = {
    "medgemma_4b": {
        "id":     os.getenv("MEDGEMMA_4B_ENDPOINT"),
        "region": "europe-west4",
    },
    "medgemma_27b": {
        "id":     os.getenv("MEDGEMMA_27B_ENDPOINT"),
        "region": "europe-west4",
    },
    "medasr": {
        "id":     os.getenv("MEDASR_ENDPOINT"),
        "region": "asia-east1",
    },
    "hear": {
        "id":     os.getenv("HEAR_ENDPOINT"),
        "region": "asia-east1",
    },
}

# CORS — comma-separated in .env
# e.g. ALLOWED_ORIGINS=https://vaidu.health,https://app.vaidu.health
ALLOWED_ORIGINS: list[str] = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000"
).split(",")

DISCLAIMER = (
    "\n\n⚠️ AI guidance only. "
    "Please consult a qualified doctor for diagnosis and treatment. "
    "Emergency అయితే వెంటనే 108 call చేయండి."
)

EMERGENCY_PATTERNS = [
    (["chest pain", "breathless"],      "Possible heart attack"),
    (["unconscious"],                    "Patient unconscious"),
    (["snake bite"],                     "Venomous bite"),
    (["pregnancy", "bleeding"],          "Pregnancy emergency"),
    (["seizure"],                        "Seizure"),
    (["stroke", "face drooping"],        "Possible stroke"),
    (["child", "not breathing"],         "Pediatric emergency"),
]

MAX_IMAGE_BYTES = 10 * 1024 * 1024   # 10 MB