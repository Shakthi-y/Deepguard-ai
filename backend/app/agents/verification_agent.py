"""Verification Agent — cross-checks model result against forensic evidence."""


def run(detection: dict, forensic: dict) -> dict:
    log = {"agent": "Verification Agent", "status": "running"}

    model_says_fake = detection["predicted_label"] == "fake"
    strong_model = detection["model_confidence"] >= 0.65

    forensic_suspicious = len(forensic["flags"]) >= 2

    if strong_model and model_says_fake and forensic_suspicious:
        verdict, consistent = "LIKELY FAKE", True
        reasoning = "Model strongly predicts fake and forensic evidence supports it."
    elif strong_model and not model_says_fake and not forensic_suspicious:
        verdict, consistent = "LIKELY REAL", True
        reasoning = "Model strongly predicts real and no significant forensic red flags were found."
    elif strong_model and model_says_fake and not forensic_suspicious:
        verdict, consistent = "LIKELY FAKE", False
        reasoning = "Model predicts fake but forensic evidence is inconclusive — leaning on model result."
    elif strong_model and not model_says_fake and forensic_suspicious:
        verdict, consistent = "UNCERTAIN", False
        reasoning = "Model predicts real but forensic checks raised flags — conflicting evidence."
    else:
        verdict, consistent = "UNCERTAIN", False
        reasoning = "Model confidence is too low to reach a reliable verdict on its own."

    return {
        "ok": True,
        "verification": {"verdict": verdict, "consistent": consistent, "reasoning": reasoning},
        "log": {**log, "status": "completed", "detail": verdict},
    }
