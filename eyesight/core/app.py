"""Main application class for the Eyesight application."""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

import pyaudio

from eyesight.config import VideoMode, DEFAULT_MODE
from eyesight.config.settings import GeminiConfig
from eyesight.audio.capture import capture_audio
from eyesight.audio.playback import play_audio
from eyesight.video.camera import capture_frames
from eyesight.video.screen import capture_screen
from eyesight.gemini.session import (
    send_text,
    send_realtime,
    receive_responses,
)

logger = logging.getLogger(__name__)


@dataclass
class EyesightApp:
    """Main application class for handling audio/video interaction with Gemini API."""

    gemini_config: GeminiConfig
    video_mode: VideoMode = DEFAULT_MODE
    audio_in_queue: asyncio.Queue = field(
        default_factory=asyncio.Queue
    )  # Initialize queue
    out_queue: asyncio.Queue = field(
        default_factory=lambda: asyncio.Queue(maxsize=5)
    )  # Initialize queue with maxsize
    session: Any = None
    audio_stream: pyaudio.Stream | None = None
    playback_stream: pyaudio.Stream | None = None

    async def run(self) -> None:
        """Main execution loop."""
        try:
            # Use injected Gemini configuration
            gemini = self.gemini_config

            logger.info("Connecting to Gemini API...")

            async with (
                gemini.client.aio.live.connect(
                    model=gemini.model, config=gemini.live_config
                ) as session,
                asyncio.TaskGroup() as tg,
            ):
                logger.info("Connected to Gemini API successfully")
                self.session = session

                # Start background tasks
                audio_capture_task, playback_task, send_text_task = (
                    self._start_background_tasks(tg, self.session)
                )

                # Wait for user to exit
                await send_text_task

                # Store audio streams for cleanup
                # These tasks return the stream objects upon completion/cancellation
                self.audio_stream = await audio_capture_task
                self.playback_stream = await playback_task

                logger.info("User requested exit. Shutting down...")
                raise asyncio.CancelledError("User requested exit")

        except asyncio.CancelledError:
            logger.info("Application cancelled. Cleaning up...")
            # This is expected during normal shutdown
            pass
        except RuntimeError as e:
            if "cannot schedule new futures after shutdown" in str(e):
                # This is an expected error during shutdown
                logger.info("Application shutdown: executor already closed")
            else:
                logger.exception("Runtime error occurred:")
        except ExceptionGroup:
            logger.exception("Exception group caught:")
        except Exception:
            logger.exception("Unexpected error:")
        finally:
            # Final cleanup of audio streams if they weren't closed earlier
            if hasattr(self, "audio_stream") and self.audio_stream:
                try:
                    self.audio_stream.close()
                    logger.info("Audio input stream closed")
                except Exception as e:
                    logger.error(f"Error closing audio input stream: {str(e)}")

            if hasattr(self, "playback_stream") and self.playback_stream:
                try:
                    self.playback_stream.close()
                    logger.info("Audio playback stream closed")
                except Exception as e:
                    logger.error(
                        f"Error closing audio playback stream: {str(e)}"
                    )

            logger.info("Application shutdown complete.")

    def _start_background_tasks(self, tg: asyncio.TaskGroup, session: Any):
        """Starts all background tasks within the task group."""
        logger.info("Starting text input handler...")
        send_text_task = tg.create_task(send_text(session))

        logger.info("Starting realtime data handler...")
        tg.create_task(send_realtime(session, self.out_queue))

        logger.info("Starting audio capture...")
        audio_capture_task = tg.create_task(capture_audio(self.out_queue))

        # Start video capture based on selected mode
        if self.video_mode == VideoMode.CAMERA:
            logger.info("Starting camera capture...")
            tg.create_task(capture_frames(self.out_queue))
        elif self.video_mode == VideoMode.SCREEN:
            logger.info("Starting screen capture...")
            tg.create_task(capture_screen(self.out_queue))
        else:
            logger.info("No video capture selected")

        logger.info("Starting response handler...")
        tg.create_task(receive_responses(session, self.audio_in_queue))

        logger.info("Starting audio playback...")
        playback_task = tg.create_task(play_audio(self.audio_in_queue))

        logger.info("All systems ready. You can now interact with Gemini.")
        logger.info("Type your messages at the 'message > ' prompt.")
        logger.info("Type '/q' to quit.")

        return audio_capture_task, playback_task, send_text_task
