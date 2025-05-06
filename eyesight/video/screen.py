"""Screen capture functionality for the Eyesight application."""

import io
import asyncio
import logging
from typing import Dict, Optional

import mss
import PIL.Image
import mss.tools

from eyesight.video.processing import process_image
from eyesight.video.config import CAPTURE_INTERVAL_SECONDS

logger = logging.getLogger(__name__)


def get_screen() -> Optional[Dict[str, str]]:
    """Capture the screen and process it.

    Returns:
        Processed screenshot or None if capture failed
    """
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)

            # Use mss.tools.to_png to convert the screenshot to PNG bytes
            image_bytes = mss.tools.to_png(screenshot.rgb, screenshot.size)
            if image_bytes is None:
                logger.error("Failed to convert screenshot to PNG bytes.")
                return None
            img = PIL.Image.open(io.BytesIO(image_bytes))

            return process_image(img)
    except Exception:
        logger.exception("Error capturing or processing screen:")
        return None


async def capture_screen(queue: asyncio.Queue) -> None:
    """Continuously capture screen and add to queue.

    Args:
        queue: Queue to add captured screenshots to
    """
    try:
        while True:
            try:
                # Use the safer approach with context manager for each capture
                frame = await asyncio.to_thread(get_screen)
                if frame is None:
                    # If get_screen returns None, it means an error occurred
                    # and was already logged. We can continue or break.
                    # For now, let's continue to try capturing in the next loop iteration.
                    continue

                await asyncio.sleep(CAPTURE_INTERVAL_SECONDS)
                await queue.put(frame)
            except RuntimeError as e:
                # Check if this is the "cannot schedule new futures after shutdown" error
                if "cannot schedule new futures after shutdown" in str(e):
                    logger.info("Screen capture stopped: executor shutdown")
                    break
                # Re-raise other RuntimeErrors
                raise
            except asyncio.CancelledError:
                # Handle task cancellation gracefully
                logger.info("Screen capture task cancelled during operation")
                break
    except asyncio.CancelledError:
        # Handle task cancellation gracefully
        logger.info("Screen capture task cancelled")
    except Exception:
        logger.exception("Error in screen capture:")
    finally:
        logger.info("Screen capture task exiting")
