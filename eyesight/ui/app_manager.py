"""Manages the lifecycle of the Eyesight application."""

import asyncio
import threading
import os

from eyesight.core.app import EyesightApp
from eyesight.config import (
    VideoMode,
    GEMINI_CONFIG,
)


class AppLifecycleManager:
    """Manages the lifecycle (start, stop, thread, loop) of the EyesightApp."""

    def __init__(self, on_status_update=None, on_error=None, on_stopped=None):
        """Initialize the AppLifecycleManager.

        Args:
            on_status_update: Callback function for status updates.
            on_error: Callback function for errors.
            on_stopped: Callback function when the app stops.
        """
        self._app = None
        self._app_loop = None
        self._app_thread = None
        self._is_running = False

        # Callbacks for UI updates
        self._on_status_update = on_status_update
        self._on_error = on_error
        self._on_stopped = on_stopped

    def start(self, api_key: str, video_mode: VideoMode):
        """Start the Eyesight application in a separate thread.

        Args:
            api_key: The Gemini API key (set in environment).
            video_mode: The selected video mode.
        """
        if self._is_running:
            print("App is already running.")
            return

        # Set the API key in environment for the core app to pick up
        os.environ["GEMINI_API_KEY"] = api_key

        self._is_running = True
        self._app_thread = threading.Thread(
            target=self._run_app_thread, args=(video_mode,)
        )
        self._app_thread.daemon = (
            True  # Allow main thread to exit even if this thread is running
        )
        self._app_thread.start()
        self._report_status(f"Starting with mode: {video_mode.value}")

    def stop(self):
        """Stop the Eyesight application."""
        if not self._is_running:
            print("App is not running.")
            return

        self._report_status("Stopping application...")
        # Signal the running thread to stop
        if self._app_loop and not self._app_loop.is_closed():
            # Schedule a coroutine to cancel tasks and stop the loop
            asyncio.run_coroutine_threadsafe(
                self._stop_asyncio_loop(), self._app_loop
            )

    async def _stop_asyncio_loop(self):
        """Coroutine to stop the asyncio loop gracefully."""
        if not self._app_loop or self._app_loop.is_closed():
            print("Asyncio loop is not available or already closed.")
            return

        print("Attempting to stop asyncio loop...")
        tasks_to_cancel = [
            t for t in asyncio.all_tasks(self._app_loop) if not t.done()
        ]

        if tasks_to_cancel:
            print(f"Cancelling {len(tasks_to_cancel)} tasks...")
            # Cancel tasks and give them a moment to finish
            for task in tasks_to_cancel:
                task.cancel()
            # Wait for tasks to complete with a timeout
            await asyncio.wait(
                tasks_to_cancel, timeout=2.0, return_when=asyncio.ALL_COMPLETED
            )

        # Stop the loop
        if self._app_loop.is_running():
            self._app_loop.stop()
            print("Asyncio loop stopped.")

    def _run_app_thread(self, video_mode: VideoMode):
        """Run the Eyesight app within a separate thread."""
        try:
            # Create the app and event loop
            # Pass the imported GEMINI_CONFIG
            self._app = EyesightApp(
                gemini_config=GEMINI_CONFIG, video_mode=video_mode
            )

            # Create a new event loop for this thread
            policy = asyncio.get_event_loop_policy()
            self._app_loop = policy.new_event_loop()
            asyncio.set_event_loop(self._app_loop)

            # Run the app until complete or stopped
            self._app_loop.run_until_complete(self._app.run())

        except asyncio.CancelledError:
            print("Application run was cancelled.")
        except Exception as e:
            print(f"Error during application run: {e}")
            self._report_error(str(e))
        finally:
            print("Application thread finished.")
            self._cleanup_resources()
            self._report_stopped()

    def _cleanup_resources(self):
        """Clean up resources (audio streams, PyAudio, event loop)."""
        print("Cleaning up resources...")
        # Close audio streams safely
        if self._app:
            for stream_name in ["audio_stream", "playback_stream"]:
                stream = getattr(self._app, stream_name, None)
                if stream:
                    try:
                        stream.close()
                        print(f"{stream_name.replace('_', ' ')} closed")
                    except Exception as e:
                        print(
                            f"Error closing {stream_name.replace('_', ' ')}: {e}"
                        )
            self._app = None  # Dereference the app

        # Close the event loop safely
        # PyAudio instances should be terminated when their AudioManager context managers exit
        if self._app_loop and not self._app_loop.is_closed():
            try:
                self._app_loop.close()
                print("Event loop closed.")
            except Exception as e:
                print(f"Error closing event loop: {e}")
            self._app_loop = None  # Dereference the loop

        self._is_running = False
        print("Resource cleanup complete.")

    def _report_status(self, message):
        """Report status update via callback."""
        if self._on_status_update:
            # Use root.after to update GUI from a different thread
            # Assuming the callback handles being called from a different thread (e.g., using root.after)
            self._on_status_update(message)

    def _report_error(self, error_message):
        """Report error via callback."""
        if self._on_error:
            # Use root.after to update GUI from a different thread
            self._on_error(error_message)

    def _report_stopped(self):
        """Report app stopped via callback."""
        if self._on_stopped:
            # Use root.after to update GUI from a different thread
            self._on_stopped()

    def is_running(self):
        """Check if the application is currently running."""
        return self._is_running
