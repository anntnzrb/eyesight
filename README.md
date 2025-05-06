# Eyesight

Gemini Live API interaction with audio/video.

## Usage

### Command Line Interface

```bash
# default mode (screen capture)
uv run eyesight

# use camera as video input
uv run eyesight --mode camera

# audio only, no video input
uv run eyesight --mode none
```

### Graphical User Interface

```bash
# launch the GUI
uv run eyesight --gui
```

The GUI allows you to:
- Select the video mode (Camera, Screen, or None)
- Enter your Gemini API key
- Start the application with the selected settings
