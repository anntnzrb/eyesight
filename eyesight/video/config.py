"""Configuration settings for the Eyesight video module."""

import typing

# Interval in seconds between capturing frames/screens
CAPTURE_INTERVAL_SECONDS: float = 1.0

# Thumbnail size for processing images before sending to Gemini
PROCESSING_THUMBNAIL_SIZE: typing.Tuple[int, int] = (1024, 1024)

# Image format for processing
PROCESSING_IMAGE_FORMAT: str = "jpeg"

# MIME type corresponding to the image format
PROCESSING_MIME_TYPE: str = "image/jpeg"
