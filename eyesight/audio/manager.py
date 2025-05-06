import asyncio
import logging
import pyaudio
from typing import Callable, Optional, Coroutine

from eyesight.config import AUDIO_CONFIG


class AudioManager:
    """
    Manages the PyAudio instance and provides methods for opening, closing,
    capturing from, and playing to audio streams.

    This class centralizes PyAudio operations and resource management.
    """

    def __init__(self, config=AUDIO_CONFIG):
        """
        Initializes the PyAudio instance and stores the audio configuration.
        """
        self._pya = pyaudio.PyAudio()
        self._config = config
        self._input_stream: Optional[pyaudio.Stream] = None
        self._output_stream: Optional[pyaudio.Stream] = None

    async def open_input_stream(self) -> pyaudio.Stream:
        """
        Opens the default input audio stream.

        If an input stream is already open, it will be closed before opening a new one.
        """
        if self._input_stream is not None:
            self.close_input_stream()

        mic_info = await asyncio.to_thread(
            self._pya.get_default_input_device_info
        )
        self._input_stream = await asyncio.to_thread(
            self._pya.open,
            format=self._config.format,
            channels=self._config.channels,
            rate=self._config.send_sample_rate,
            input=True,
            input_device_index=int(mic_info["index"]),
            frames_per_buffer=self._config.chunk_size,
        )
        return self._input_stream

    async def open_output_stream(self) -> pyaudio.Stream:
        """
        Opens the default output audio stream.

        If an output stream is already open, it will be closed before opening a new one.
        """
        if self._output_stream is not None:
            self.close_output_stream()

        self._output_stream = await asyncio.to_thread(
            self._pya.open,
            format=self._config.format,
            channels=self._config.channels,
            rate=self._config.receive_sample_rate,
            output=True,
        )
        return self._output_stream

    async def capture_chunk(self) -> bytes:
        """
        Reads a chunk of audio data from the opened input stream.

        Raises:
            RuntimeError: If the input stream is not open.
        """
        if self._input_stream is None:
            raise RuntimeError("Input stream is not open.")

        kwargs = {"exception_on_overflow": False} if __debug__ else {}
        data = await asyncio.to_thread(
            self._input_stream.read, self._config.chunk_size, **kwargs
        )
        return data

    async def play_chunk(self, data: bytes):
        """
        Writes a chunk of audio data to the opened output stream.

        Args:
            data: The bytes containing the audio data to play.

        Raises:
            RuntimeError: If the output stream is not open.
        """
        if self._output_stream is None:
            raise RuntimeError("Output stream is not open.")

        await asyncio.to_thread(self._output_stream.write, data)

    def close_input_stream(self):
        """
        Closes the input audio stream if it is currently open.
        """
        if self._input_stream is not None:
            self._input_stream.stop_stream()
            self._input_stream.close()
            self._input_stream = None

    def close_output_stream(self):
        """
        Closes the output audio stream if it is currently open.
        """
        if self._output_stream is not None:
            self._output_stream.stop_stream()
            self._output_stream.close()
            self._output_stream = None

    def terminate(self):
        """
        Closes any open audio streams and terminates the PyAudio instance.
        This should be called when the AudioManager is no longer needed.
        """
        self.close_input_stream()
        self.close_output_stream()
        if self._pya is not None:
            self._pya.terminate()

    async def __aenter__(self):
        """
        Enters the async context.

        Returns:
            The AudioManager instance.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the async context, ensuring all resources are terminated.
        """
        self.terminate()


async def _run_audio_task(
    audio_manager: AudioManager,
    open_stream_method: Callable[[], Coroutine[None, None, pyaudio.Stream]],
    task_coroutine: Callable[[], Coroutine[None, None, None]],
    cancel_message: str,
):
    """
    Generic worker function to run audio capture or playback tasks.

    Handles stream opening, the main loop, and cancellation.
    """
    stream = await open_stream_method()
    try:
        while True:
            await task_coroutine()
    except asyncio.CancelledError:
        logging.info(cancel_message)
    return stream  # Return the opened stream
