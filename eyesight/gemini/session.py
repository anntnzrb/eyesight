"""Gemini API session management for the Eyesight application."""

import asyncio
from typing import Any

from google.genai import types

from eyesight.config import GEMINI_CONFIG


async def send_text(session: Any) -> None:
    """Handle text input from user and send to Gemini.

    Args:
        session: Gemini API session

    Returns:
        None when user exits
    """
    while True:
        text = await asyncio.to_thread(input, "message > ")
        if text.lower() == "/q":
            break
        await session.send_client_content(
            turns=types.Content(
                role="user", parts=[types.Part(text=text or ".")]
            ),
            turn_complete=True,
        )


async def send_realtime(session: Any, queue: asyncio.Queue) -> None:
    """Send queued messages to Gemini API.

    Args:
        session: Gemini API session
        queue: Queue containing messages to send
    """
    while True:
        msg = await queue.get()
        if "mime_type" in msg:
            await session.send_realtime_input(media=msg)


async def receive_responses(session: Any, audio_queue: asyncio.Queue) -> None:
    """Read responses from Gemini API and process them.

    Args:
        session: Gemini API session
        audio_queue: Queue to add audio responses to
    """
    while True:
        turn = session.receive()
        async for response in turn:
            if data := response.data:
                audio_queue.put_nowait(data)
                continue
            if text := response.text:
                print(text, end="")

        # Clear queue on interruption for better responsiveness
        while not audio_queue.empty():
            audio_queue.get_nowait()


async def create_session() -> Any:
    """Create and return a Gemini API session.

    Returns:
        Gemini API session
    """
    gemini = GEMINI_CONFIG
    return await gemini.client.aio.live.connect(
        model=gemini.model, config=gemini.live_config
    )
