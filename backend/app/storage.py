"""Simple JSON-file based history store (keeps things dependency-light)."""
import json
import threading
from app.config import settings

_lock = threading.Lock()


def _load() -> dict:
    if not settings.HISTORY_FILE.exists():
        return {}
    try:
        with open(settings.HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_analysis(analysis: dict):
    with _lock:
        data = _load()
        data[analysis["id"]] = analysis
        with open(settings.HISTORY_FILE, "w") as f:
            json.dump(data, f, indent=2)


def get_analysis(analysis_id: str):
    return _load().get(analysis_id)


def list_history(limit: int = 50):
    data = _load()
    items = sorted(data.values(), key=lambda x: x["timestamp"], reverse=True)
    return items[:limit]
