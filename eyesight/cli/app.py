"""Command-line interface for the Eyesight application."""

import asyncio
import argparse

from eyesight.config import VideoMode, DEFAULT_MODE
from eyesight.core.app import EyesightApp


from eyesight.config.settings import GEMINI_CONFIG


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Gemini Live API interaction with audio/video"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default=DEFAULT_MODE.value,
        help="Source for video streaming",
        choices=[mode.value for mode in VideoMode],
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the graphical user interface",
    )
    return parser.parse_args()


async def main(video_mode: VideoMode) -> None:
    """Main application entry point.

    Args:
        video_mode: The video mode to use
    """
    app = EyesightApp(gemini_config=GEMINI_CONFIG, video_mode=video_mode)
    await app.run()


def run_cli():
    """Entry point for the CLI."""
    args = parse_arguments()

    if args.gui:
        # Import here to avoid circular imports
        from eyesight.ui import run_gui

        run_gui()
    else:
        # Run in CLI mode
        video_mode = VideoMode.from_string(args.mode)
        asyncio.run(main(video_mode))
