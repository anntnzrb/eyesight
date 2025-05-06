"""Gemini API interaction and session management for the Eyesight application.

This module provides the core functionality for creating and managing interactive
sessions with the Google Gemini API.
"""

from .session import (
    create_session,
    send_text,
    send_realtime,
    receive_responses,
    GeminiLiveSession,
)

__all__ = [
    "create_session",
    "send_text",
    "send_realtime",
    "receive_responses",
    "GeminiLiveSession",
]
