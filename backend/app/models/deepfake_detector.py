"""
Loads model2_skincare.h5 and runs inference.
Falls back to a deterministic simulated-inference mode (clearly flagged)
if TensorFlow or the model file isn't available, so the rest of the
pipeline / demo still works end-to-end.
"""
import os
import hashlib
import numpy as np
from PIL import Image
from app.config import settings

_model = None
_model_load_error = None
_using_simulation = False


def _try_load_model():
    global _model, _model_load_error, _using_simulation
    if _model is not None or _model_load_error is not None:
        return
    try:
        if not os.path.exists(settings.MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {settings.MODEL_PATH}")
        import tensorflow as tf
        _model = tf.keras.models.load_model(settings.MODEL_PATH)
    except Exception as e:  # noqa
        _model_load_error = str(e)
        _using_simulation = True


def is_model_available() -> bool:
    _try_load_model()
    return _model is not None


def get_model_status() -> dict:
    _try_load_model()
    return {
        "model_loaded": _model is not None,
        "simulation_mode": _using_simulation,
        "error": _model_load_error,
        "model_path": settings.MODEL_PATH,
    }


def _preprocess(image_path: str) -> np.ndarray:
    img = Image.open(image_path).convert("RGB")
    img = img.resize(settings.MODEL_INPUT_SIZE)
    arr = np.array(img).astype("float32") / 255.0
    arr = np.expand_dims(arr, axis=0)
    return arr


def _simulated_prediction(image_path: str) -> float:
    """
    Deterministic pseudo-inference used ONLY when the real .h5 model
    can't be loaded, so the pipeline is demoable. Clearly not a real
    prediction — the caller must set simulation flags on the response.
    """
    with open(image_path, "rb") as f:
        data = f.read()
    h = hashlib.sha256(data).hexdigest()
    val = int(h[:8], 16) / 0xFFFFFFFF
    return float(val)


def predict(image_path: str) -> dict:
    """
    Returns dict with fake_probability, real_probability, predicted_label,
    model_confidence, simulation_mode
    """
    _try_load_model()

    if _model is not None:
        x = _preprocess(image_path)
        raw = _model.predict(x, verbose=0)
        raw = np.array(raw).flatten()

        if raw.size == 1:
            real_prob = float(raw[0])
            fake_prob = 1.0 - real_prob
        else:
            fake_prob = float(raw[settings.FAKE_CLASS_INDEX])
            real_prob = float(raw[settings.REAL_CLASS_INDEX])
            total = fake_prob + real_prob
            if total > 0:
                fake_prob, real_prob = fake_prob / total, real_prob / total

        simulation = False
    else:
        real_prob = _simulated_prediction(image_path)
        fake_prob = 1.0 - real_prob
        simulation = True

    predicted_label = "real" if real_prob >= settings.DECISION_THRESHOLD else "fake"
    model_confidence = max(real_prob, fake_prob)

    return {
        "fake_probability": round(fake_prob, 4),
        "real_probability": round(real_prob, 4),
        "predicted_label": predicted_label,
        "model_confidence": round(model_confidence, 4),
        "threshold_used": settings.DECISION_THRESHOLD,
        "simulation_mode": simulation,
    }
