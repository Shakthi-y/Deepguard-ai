"""Intake / Image Validation Agent"""
from app.services.image_service import validate_file, save_upload, verify_image_integrity


def run(content: bytes, mime_type: str, filename: str) -> dict:
    log = {"agent": "Image Validation Agent", "status": "running"}

    validation = validate_file(content, mime_type, filename)
    if not validation["valid"]:
        return {
            "ok": False,
            "errors": validation["errors"],
            "log": {**log, "status": "failed", "detail": "; ".join(validation["errors"])},
        }

    path = save_upload(content, filename)

    if not verify_image_integrity(path):
        return {
            "ok": False,
            "errors": ["File is not a valid, decodable image."],
            "log": {**log, "status": "failed", "detail": "Image failed integrity check"},
        }

    return {
        "ok": True,
        "path": path,
        "size_mb": validation["size_mb"],
        "log": {**log, "status": "completed", "detail": f"Validated ({validation['size_mb']}MB)"},
    }
