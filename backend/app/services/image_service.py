import os
import uuid
from pathlib import Path
from PIL import Image
from app.config import settings


def safe_filename(original_name: str) -> str:
    ext = Path(original_name).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        ext = ".jpg"
    return f"{uuid.uuid4().hex}{ext}"


def validate_file(content: bytes, mime_type: str, filename: str) -> dict:
    errors = []
    size_mb = len(content) / (1024 * 1024)

    if size_mb > settings.MAX_FILE_SIZE_MB:
        errors.append(f"File too large ({size_mb:.1f}MB). Max is {settings.MAX_FILE_SIZE_MB}MB.")

    if mime_type not in settings.ALLOWED_MIME_TYPES:
        errors.append(f"Unsupported MIME type: {mime_type}")

    ext = Path(filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        errors.append(f"Unsupported file extension: {ext}")

    return {"valid": len(errors) == 0, "errors": errors, "size_mb": round(size_mb, 3)}


def save_upload(content: bytes, original_name: str) -> str:
    fname = safe_filename(original_name)
    path = settings.UPLOAD_DIR / fname
    with open(path, "wb") as f:
        f.write(content)
    return str(path)


def verify_image_integrity(path: str) -> bool:
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception:
        return False


def extract_metadata(path: str) -> dict:
    info = {
        "dimensions": "unknown",
        "format": "unknown",
        "color_mode": "unknown",
        "has_exif": False,
        "exif_summary": {},
        "aspect_ratio": 0.0,
    }
    try:
        with Image.open(path) as img:
            w, h = img.size
            info["dimensions"] = f"{w}x{h}"
            info["format"] = img.format or "unknown"
            info["color_mode"] = img.mode
            info["aspect_ratio"] = round(w / h, 3) if h else 0.0

            exif = getattr(img, "_getexif", lambda: None)()
            if exif:
                info["has_exif"] = True
                keys = ["Make", "Model", "Software", "DateTime"]
                from PIL.ExifTags import TAGS
                tag_map = {TAGS.get(k, k): v for k, v in exif.items()}
                for k in keys:
                    if k in tag_map:
                        info["exif_summary"][k] = str(tag_map[k])
    except Exception:
        pass
    return info
