"""Forensic Analysis Agent — metadata, MIME, dimension, compression checks. Never invents evidence."""
import os
from app.services.image_service import extract_metadata


def run(image_path: str, mime_type: str) -> dict:
    log = {"agent": "Forensic Analysis Agent", "status": "running"}
    meta = extract_metadata(image_path)
    file_size_kb = round(os.path.getsize(image_path) / 1024, 2)

    flags = []

    if not meta["has_exif"]:
        flags.append("No EXIF metadata present (common in screenshots, edited, or AI-generated images)")

    if meta["aspect_ratio"] and (meta["aspect_ratio"] == 1.0):
        flags.append("Perfectly square aspect ratio (common output shape for generative models)")

    if file_size_kb < 30:
        flags.append("Unusually small file size relative to typical camera photos")

    compression = "high" if file_size_kb < 100 else ("moderate" if file_size_kb < 500 else "low")

    evidence = {
        "mime_type": mime_type,
        "file_size_kb": file_size_kb,
        "dimensions": meta["dimensions"],
        "format": meta["format"],
        "has_exif": meta["has_exif"],
        "exif_summary": meta["exif_summary"],
        "estimated_compression": compression,
        "aspect_ratio": meta["aspect_ratio"],
        "color_mode": meta["color_mode"],
        "flags": flags,
    }

    return {
        "ok": True,
        "evidence": evidence,
        "log": {**log, "status": "completed", "detail": f"{len(flags)} flag(s) noted"},
    }
