"""Eyesight - Gemini Live API interaction with audio/video."""

from eyesight.core.app import EyesightApp
from eyesight.config import VideoMode, AUDIO_CONFIG, GEMINI_CONFIG
from eyesight.ui import run_gui

__version__ = "0.1.0"
__all__ = [
    "EyesightApp",
    "VideoMode",
    "AUDIO_CONFIG",
    "GEMINI_CONFIG",
    "run_gui",
]
