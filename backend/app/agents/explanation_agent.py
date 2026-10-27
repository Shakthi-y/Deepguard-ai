"""Explanation Agent — Gemini-backed, grounded strictly in prior agent outputs."""
from app.services.gemini_service import generate_explanation


def run(detection: dict, forensic: dict, verification: dict, confidence: dict) -> dict:
    log = {"agent": "Explanation Agent", "status": "running"}
    try:
        text = generate_explanation(detection, forensic, verification, confidence)
        return {"ok": True, "explanation": text, "log": {**log, "status": "completed", "detail": "generated"}}
    except Exception as e:
        return {
            "ok": True,
            "explanation": "Explanation unavailable due to a service error, but the verdict above is still based on the model and forensic analysis.",
            "log": {**log, "status": "completed", "detail": f"fallback ({e})"},
        }
