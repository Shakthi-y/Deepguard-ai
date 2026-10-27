"""Deepfake Detection Agent — runs model2_skincare.h5 inference"""
from app.models.deepfake_detector import predict, get_model_status


def run(image_path: str) -> dict:
    log = {"agent": "Deepfake Detection Agent", "status": "running"}
    try:
        result = predict(image_path)
        status = get_model_status()
        note = " (SIMULATED — model file unavailable)" if result["simulation_mode"] else ""
        return {
            "ok": True,
            "result": result,
            "model_status": status,
            "log": {**log, "status": "completed",
                    "detail": f"predicted={result['predicted_label']}{note}"},
        }
    except Exception as e:
        return {
            "ok": False,
            "errors": [f"Model inference failed: {e}"],
            "log": {**log, "status": "failed", "detail": str(e)},
        }
