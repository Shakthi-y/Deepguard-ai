import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    APP_NAME = "DeepGuard AI"
    VERSION = "1.0.0"

    MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "ml_models" / "model2_skincare.h5"))
    MODEL_INPUT_SIZE = (224, 224)
    FAKE_CLASS_INDEX = 0
    REAL_CLASS_INDEX = 1
    DECISION_THRESHOLD = 0.5

    UPLOAD_DIR = BASE_DIR / "uploads"
    REPORT_DIR = BASE_DIR / "reports"
    HISTORY_FILE = BASE_DIR / "history.json"

    MAX_FILE_SIZE_MB = 10
    ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORT_DIR.mkdir(parents=True, exist_ok=True)
