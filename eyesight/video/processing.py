"""Image processing utilities for the Eyesight application."""

import io
import base64
from typing import Dict

import PIL.Image

from eyesight.video.config import (
    PROCESSING_THUMBNAIL_SIZE,
    PROCESSING_IMAGE_FORMAT,
    PROCESSING_MIME_TYPE,
)


def process_image(img: PIL.Image.Image) -> Dict[str, str]:
    """Process an image and return it in the format expected by Gemini API.

    Args:
        img: The PIL Image to process

    Returns:
        Dictionary with mime_type and base64-encoded image data
    """
    img.thumbnail(PROCESSING_THUMBNAIL_SIZE)

    with io.BytesIO() as image_io:
        img.save(image_io, format=PROCESSING_IMAGE_FORMAT)
        image_io.seek(0)
        image_bytes = image_io.read()

    return {
        "mime_type": PROCESSING_MIME_TYPE,
        "data": base64.b64encode(image_bytes).decode(),
    }
