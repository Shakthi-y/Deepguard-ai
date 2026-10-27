"""
Calls Gemini API to turn structured analysis results into a plain-language
explanation. Never invents evidence — only summarizes the JSON it's given.
Falls back to a template-based explanation if no API key is configured
or the call fails, so the app always returns something useful.
"""
import os
import json
import requests
from app.config import settings

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
)


def _template_explanation(detection: dict, forensic: dict, verification: dict, confidence: dict) -> str:
    verdict = verification["verdict"]
    parts = []
    if verdict == "LIKELY REAL":
        parts.append(
            f"The detection model estimated a {detection['real_probability']*100:.1f}% probability "
            f"that this image is authentic, above the {detection['threshold_used']} decision threshold."
        )
    elif verdict == "LIKELY FAKE":
        parts.append(
            f"The detection model estimated a {detection['fake_probability']*100:.1f}% probability "
            f"that this image is manipulated or AI-generated."
        )
    else:
        parts.append(
            "The model output and forensic evidence did not agree strongly enough to reach a "
            "confident verdict, so this image is marked as uncertain."
        )

    if forensic.get("flags"):
        parts.append("Forensic checks noted: " + "; ".join(forensic["flags"]) + ".")
    else:
        parts.append("No unusual forensic flags (metadata, compression, or dimension anomalies) were found.")

    parts.append(
        f"Model confidence was {confidence['model_confidence']*100:.1f}%, "
        f"and overall system confidence (model + forensic agreement) was {confidence['system_confidence']*100:.1f}%."
    )
    parts.append("This is an AI-based authenticity assessment and not absolute proof.")
    return " ".join(parts)


def generate_explanation(detection: dict, forensic: dict, verification: dict, confidence: dict) -> str:
    if not settings.GEMINI_API_KEY:
        return _template_explanation(detection, forensic, verification, confidence)

    prompt = f"""You are the Explanation Agent inside DeepGuard AI, a deepfake image detection system.
Using ONLY the structured JSON evidence below, write a clear, honest, 3-5 sentence explanation
for a non-technical user of why the system reached this verdict. Do not invent any evidence that
is not present in the JSON. Do not claim certainty. Mention that this is an AI-based assessment,
not proof.

DETECTION_RESULT: {json.dumps(detection)}
FORENSIC_EVIDENCE: {json.dumps(forensic)}
VERIFICATION_RESULT: {json.dumps(verification)}
CONFIDENCE_RESULT: {json.dumps(confidence)}
"""

    try:
        url = GEMINI_URL.format(model=settings.GEMINI_MODEL, key=settings.GEMINI_API_KEY)
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return text.strip()
    except Exception:
        return _template_explanation(detection, forensic, verification, confidence)


def chat_answer(question: str, context: dict) -> str:
    """Ask DeepGuard chat — answers questions grounded in the last analysis context only."""
    if not settings.GEMINI_API_KEY:
        return (
            "I can only answer based on the analysis results shown. "
            "Configure GEMINI_API_KEY in your .env for richer conversational answers. "
            f"Current verdict on record: {context.get('verdict', 'no analysis yet')}."
        )

    prompt = f"""You are "Ask DeepGuard", a helpful assistant embedded in the DeepGuard AI deepfake
detection tool. Answer the user's question using ONLY this analysis context (do not invent facts
outside it). If the question is unrelated to the analysis, answer generally but stay honest that
you are not infallible.

CONTEXT: {json.dumps(context)}
QUESTION: {question}
"""
    try:
        url = GEMINI_URL.format(model=settings.GEMINI_MODEL, key=settings.GEMINI_API_KEY)
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return "I couldn't reach the Gemini API right now. Please check your API key and try again."
