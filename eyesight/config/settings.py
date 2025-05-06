"""Configuration settings for the Eyesight application."""

import os
import enum
from dataclasses import dataclass
from pathlib import Path

import pyaudio
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env")


@dataclass
class AudioConfig:
    """Audio configuration parameters."""

    format: int = pyaudio.paInt16
    channels: int = 1
    send_sample_rate: int = 16000
    receive_sample_rate: int = 24000
    chunk_size: int = 1024


@dataclass
class GeminiConfig:
    """Gemini API configuration."""

    model: str = "models/gemini-2.0-flash-live-001"
    voice_name: str = "Puck"
    api_version: str = "v1beta"

    @property
    def client(self) -> genai.Client:
        """Initialize and return the Gemini client."""
        return genai.Client(
            http_options={"api_version": self.api_version},
            api_key=os.environ.get("GEMINI_API_KEY"),
        )

    @property
    def live_config(self) -> types.LiveConnectConfig:
        """Create and return the LiveConnectConfig."""
        return types.LiveConnectConfig(
            response_modalities=["audio"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=self.voice_name
                    )
                )
            ),
        )


class VideoMode(enum.Enum):
    """Available video input modes."""

    CAMERA = "camera"
    SCREEN = "screen"
    NONE = "none"

    @classmethod
    def from_string(cls, value: str) -> "VideoMode":
        """Convert string to VideoMode enum."""
        try:
            return cls(value)
        except ValueError:
            return cls.SCREEN  # default mode


# Initialize global configurations
AUDIO_CONFIG = AudioConfig()
GEMINI_CONFIG = GeminiConfig()
DEFAULT_MODE = VideoMode.SCREEN
