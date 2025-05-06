"""Audio playback functionality for the Eyesight application."""

import asyncio


from eyesight.audio.manager import AudioManager, _run_audio_task


async def play_audio(queue: asyncio.Queue):
    """
    Plays audio data from the provided queue using the AudioManager.

    This function runs indefinitely until cancelled.
    """
    async with AudioManager() as audio_manager:

        async def _get_and_play():
            bytestream = await queue.get()
            await audio_manager.play_chunk(bytestream)

        return await _run_audio_task(
            audio_manager,
            audio_manager.open_output_stream,
            _get_and_play,
            "Audio playback task cancelled.",
        )
