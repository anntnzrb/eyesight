"""Audio capture functionality for the Eyesight application."""

import asyncio


from eyesight.audio.manager import AudioManager, _run_audio_task


async def capture_audio(queue: asyncio.Queue):
    """
    Captures audio from the microphone using the AudioManager and puts the
    audio data onto the provided queue.

    This function runs indefinitely until cancelled.
    """
    async with AudioManager() as audio_manager:

        async def _capture_and_put():
            data = await audio_manager.capture_chunk()
            await queue.put({"data": data, "mime_type": "audio/pcm"})

        return await _run_audio_task(
            audio_manager,
            audio_manager.open_input_stream,
            _capture_and_put,
            "Audio capture task cancelled.",
        )
