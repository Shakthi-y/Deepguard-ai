"""Confidence Agent — separates model confidence from overall system confidence."""


def run(detection: dict, verification: dict) -> dict:
    log = {"agent": "Confidence Agent", "status": "running"}

    model_confidence = detection["model_confidence"]
    consistency_bonus = 0.10 if verification["consistent"] else -0.15
    system_confidence = max(0.05, min(0.97, model_confidence + consistency_bonus))

    if system_confidence >= 0.80:
        band = "High"
    elif system_confidence >= 0.55:
        band = "Moderate"
    else:
        band = "Low"

    result = {
        "model_confidence": round(model_confidence, 4),
        "system_confidence": round(system_confidence, 4),
        "confidence_band": band,
    }

    return {
        "ok": True,
        "confidence": result,
        "log": {**log, "status": "completed", "detail": f"{band} ({system_confidence*100:.1f}%)"},
    }
