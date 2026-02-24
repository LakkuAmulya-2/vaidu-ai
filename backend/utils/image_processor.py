"""
utils/image_processor.py
Upload అయిన images నుండి EXIF/metadata strip చేయి + resize/compress.
Rural patient GPS location, device info leak కాకుండా protect చేయి.
"""
import io
import logging
from PIL import Image

logger = logging.getLogger(__name__)

# Max output image dimension (width or height)
MAX_DIMENSION = 1024
# JPEG quality (1-100, lower = smaller file)
JPEG_QUALITY = 85


def strip_exif(image_bytes: bytes) -> bytes:
    """Remove all EXIF metadata from image."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        clean = io.BytesIO()
        img.save(clean, format="JPEG", exif=b"")
        return clean.getvalue()
    except Exception as e:
        logger.warning(f"EXIF strip failed, using original: {e}")
        return image_bytes


# utils/image_processor.py

MAX_DIMENSION = 768          # Reduce from 1024 to 768
JPEG_QUALITY = 70            # Reduce from 85 to 70 (balances size/readability)

def resize_image(image_bytes: bytes) -> bytes:
    """
    Resize image to MAX_DIMENSION (maintain aspect ratio) and compress.
    Returns new JPEG bytes.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        output = io.BytesIO()
        img.save(output, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        return output.getvalue()
    except Exception as e:
        logger.warning(f"Image resize failed, using original: {e}")
        return image_bytes


def validate_image(image_bytes: bytes) -> bool:
    """Verify image is valid (not corrupt/malicious)."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
        return True
    except Exception as e:
        logger.warning(f"Image validation failed: {e}")
        return False


def process_upload(image_bytes: bytes, max_bytes: int = 10 * 1024 * 1024) -> bytes:
    """
    Complete pipeline: validate → size check → strip EXIF → resize/compress.
    Raises ValueError if invalid or too large.
    """
    if len(image_bytes) > max_bytes:
        raise ValueError(f"File too large. Max {max_bytes // (1024*1024)}MB allowed.")

    if not validate_image(image_bytes):
        raise ValueError("Invalid or corrupt image file.")

    cleaned = strip_exif(image_bytes)
    resized = resize_image(cleaned)          # <-- NEW
    return resized