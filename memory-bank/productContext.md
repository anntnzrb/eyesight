# Product Context

This file provides a high-level overview of the project and the expected product that will be created. Initially it is based upon projectBrief.md (if provided) and all other available project-related information in the working directory. This file is intended to be updated as the project evolves, and should be used to inform all other modes of the project's goals and context.
2025-05-06 01:55:08 - Added 'Original Motivation and Primary Use Case' section. Log of updates made will be appended as footnotes to the end of this file.

*

## Original Motivation and Primary Use Case

The application was originally conceived to explore the possibility of capturing the user's screen and enabling interactive questioning about the visual content. A primary envisioned use case was to assist in strategy games: by feeding sufficient visual data from the game to the application, the user could ask for real-time information and insights about the game state, potentially gaining a competitive advantage while screen sharing and discussing the ongoing game live.

## Project Goal

*   To create an application, "Eyesight," that facilitates live, interactive sessions with the Google Gemini API by utilizing real-time audio and video stream inputs.

## Key Features

*   Real-time audio capture and streaming.
*   Real-time video capture:
    *   Screen capture.
    *   Camera input.
*   Audio-only mode (no video input).
*   Direct interaction with Google Gemini API for processing audio/video streams.
*   User-friendly Command-Line Interface (CLI) for starting and configuring sessions (e.g., selecting video mode).
*   Graphical User Interface (GUI) for:
    *   Simplified selection of video input mode (Camera, Screen, None).
    *   Secure entry and management of Gemini API key.
    *   Easy initiation of the application.

## Overall Architecture

*   A Python application named "Eyesight".
*   Modular structure with dedicated components for:
    *   Audio handling (`pyaudio`).
    *   Video capture and processing (`opencv-python` for camera, `mss` for screen, `pillow` for image manipulation).
    *   Gemini API communication (`google-genai`).
    *   Command-Line Interface (`eyesight.cli.run_cli` as entry point).
    *   User Interface (details to be confirmed, but likely a Python GUI library).
    *   Configuration management (e.g., API keys via `python-dotenv`).
    *   Core application logic orchestrating these components.
*   Dependencies managed via `pyproject.toml` and `uv`.
