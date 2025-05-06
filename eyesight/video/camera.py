"""Camera capture functionality for the Eyesight application.

This module is untested and may not work as expected.
"""

import asyncio
from typing import Optional, Dict
import logging

import cv2  # type: ignore
from PIL import Image  # type: ignore

from eyesight.video.processing import process_image
from eyesight.video.config import CAPTURE_INTERVAL_SECONDS

logger = logging.getLogger(__name__)


async def get_frame(cap) -> Optional[Dict[str, str]]:
    """Capture a frame from the camera and process it.

    Args:
        cap: OpenCV VideoCapture object

    Returns:
        Processed frame or None if capture failed
    """
    ret, frame = cap.read()
    if not ret:
        return None

    # Convert BGR to RGB color space
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    return process_image(img)


async def capture_frames(queue: asyncio.Queue) -> None:
    """Continuously capture frames from camera and add to queue.

    Args:
        queue: Queue to add captured frames to
    """
    cap = None
    try:
        cap = await asyncio.to_thread(cv2.VideoCapture, 0)

        while True:
            try:
                frame = await asyncio.to_thread(get_frame, cap)
                if frame is None:
                    break

                await asyncio.sleep(CAPTURE_INTERVAL_SECONDS)
                await queue.put(frame)
            except RuntimeError as e:
                # Check if this is the "cannot schedule new futures after shutdown" error
                if "cannot schedule new futures after shutdown" in str(e):
                    logger.info("Camera capture stopped: executor shutdown")
                    break
                # Re-raise other RuntimeErrors
                raise
    except asyncio.CancelledError:
        # Handle task cancellation gracefully
        logger.info("Camera capture task cancelled")
        raise
    except Exception:
        logger.exception("Error in camera capture:")
        raise
    finally:
        # Ensure camera is released even if an exception occurs
        if cap is not None:
            cap.release()
