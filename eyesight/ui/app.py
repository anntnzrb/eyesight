"""Graphical user interface for the Eyesight application."""

import os
import tkinter as tk
from tkinter import ttk, messagebox
import signal
import threading

from eyesight.config import VideoMode
from eyesight.ui.app_manager import AppLifecycleManager


class EyesightGUI:
    """GUI for the Eyesight application."""

    def __init__(self, root):
        """Initialize the GUI.

        Args:
            root: The tkinter root window
        """
        self.root = root
        self.root.title("Eyesight - Gemini Live API")
        self.root.geometry("600x450")
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # UI variables
        self.video_mode = tk.StringVar(value=VideoMode.SCREEN.value)
        self.api_key = tk.StringVar(
            value=os.environ.get("GEMINI_API_KEY", "")
        )  # Populate from env directly
        self.status_var = tk.StringVar(value="Ready to start")
        self.show_key = tk.BooleanVar(value=False)

        # App lifecycle manager
        self._app_manager = AppLifecycleManager(
            on_status_update=lambda msg: self.root.after(
                0, self._handle_status_update, msg
            ),
            on_error=lambda err: self.root.after(0, self._handle_error, err),
            on_stopped=lambda: self.root.after(0, self._handle_stopped),
        )

        # Create UI
        self._create_ui()

    # Remove _load_api_key method - handled by settings and direct env access

    def _create_ui(self):
        """Create the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(
            main_frame,
            text="Eyesight - Gemini Live API",
            font=("Arial", 16, "bold"),
        ).pack(pady=(0, 20))

        # Left and right frames
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Build UI sections
        self._build_mode_frame(left_frame)
        self._build_api_frame(left_frame)
        self._build_instructions_frame(right_frame)
        self._build_control_button(main_frame)
        self._build_status_bar(main_frame)

    def _build_mode_frame(self, parent_frame):
        """Build the video mode selection frame."""
        mode_frame = ttk.LabelFrame(parent_frame, text="Video Mode", padding=10)
        mode_frame.pack(fill=tk.X, pady=10)

        for mode in VideoMode:
            ttk.Radiobutton(
                mode_frame,
                text=mode.value.capitalize(),
                value=mode.value,
                variable=self.video_mode,
            ).pack(anchor=tk.W, pady=5)

    def _build_api_frame(self, parent_frame):
        """Build the API key input frame."""
        api_frame = ttk.LabelFrame(
            parent_frame, text="Gemini API Key", padding=10
        )
        api_frame.pack(fill=tk.X, pady=10)

        self.api_entry = ttk.Entry(
            api_frame, textvariable=self.api_key, width=30, show="*"
        )
        self.api_entry.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(
            api_frame,
            text="Show API Key",
            variable=self.show_key,
            command=self._toggle_api_key_visibility,
        ).pack(anchor=tk.W)

    def _build_instructions_frame(self, parent_frame):
        """Build the instructions frame."""
        instructions_frame = ttk.LabelFrame(
            parent_frame, text="Instructions", padding=10
        )
        instructions_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        instructions_text = """1. Enter your Gemini API Key
2. Select a video mode:
   • Camera: Uses your webcam
   • Screen: Captures your screen
   • None: Audio only
3. Click 'Start Eyesight'
4. Interact with Gemini in the console
5. Type '/q' in the console to quit"""

        ttk.Label(
            instructions_frame,
            text=instructions_text,
            justify=tk.LEFT,
            wraplength=250,
        ).pack(fill=tk.BOTH, expand=True)

    def _build_control_button(self, parent_frame):
        """Build the start/stop control button."""
        # Button styles
        style = ttk.Style()
        style.configure(
            "Start.TButton",
            foreground="white",
            background="#007bff",
            font=("Arial", 14, "bold"),
            padding=10,
        )
        style.configure(
            "Stop.TButton",
            foreground="white",
            background="#dc3545",
            font=("Arial", 14, "bold"),
            padding=10,
        )

        self.toggle_button = ttk.Button(
            parent_frame,
            text="START EYESIGHT",
            command=self._toggle_app,
            style="Start.TButton",
            width=20,
        )
        self.toggle_button.pack(pady=20, padx=20, fill=tk.X)

    def _build_status_bar(self, parent_frame):
        """Build the status bar frame."""
        status_frame = ttk.LabelFrame(parent_frame, text="Status", padding=10)
        status_frame.pack(fill=tk.X, pady=10, side=tk.BOTTOM)

        ttk.Label(
            status_frame,
            textvariable=self.status_var,
            foreground="blue",
            font=("Arial", 10, "bold"),
        ).pack(fill=tk.X)

    def _toggle_api_key_visibility(self):
        """Toggle the visibility of the API key."""
        self.api_entry.config(show="" if self.show_key.get() else "*")

    def _toggle_app(self):
        """Toggle the application state (start/stop)."""
        if self._app_manager.is_running():
            self._stop_app()
        else:
            self._start_app()

    def _start_app(self):
        """Start the Eyesight application."""
        # Check if API key is provided
        api_key = self.api_key.get().strip()
        if not api_key:
            messagebox.showerror(
                "API Key Required", "Please enter your Gemini API key."
            )
            return

        # Check if app is already running via the manager
        if self._app_manager.is_running():
            return

        # Set the API key in environment for the core app to pick up
        os.environ["GEMINI_API_KEY"] = api_key

        # Get the selected video mode
        video_mode = VideoMode.from_string(self.video_mode.get())

        # Print a message to the console
        print("\n" + "-" * 50)
        print(f"Starting Eyesight with video mode: {video_mode.value}")
        print("-" * 50 + "\n")

        # Update UI (will be further updated by manager callbacks)
        self.status_var.set(f"Starting with mode: {video_mode.value}")
        self.toggle_button.config(
            text="STOP EYESIGHT", style="Stop.TButton", state="disabled"
        )  # Disable while starting

        # Start the app using the manager
        self._app_manager.start(api_key, video_mode)

    def _stop_app(self):
        """Stop the Eyesight application."""
        if not self._app_manager.is_running():
            return

        self.status_var.set("Stopping application...")
        self.toggle_button.config(state="disabled")  # Disable while stopping
        self._app_manager.stop()

    def _on_closing(self):
        """Handle window close event."""
        if self._app_manager.is_running():
            if messagebox.askyesno(
                "Quit",
                "Eyesight is still running. Do you want to stop it and exit?",
            ):
                self.status_var.set("Shutting down...")
                self.toggle_button.config(state="disabled")
                # Stop the app manager, it will handle cleanup and signal when done
                self._app_manager.stop()
                # Exit will happen in _handle_stopped callback if exit_after is True
                self._exit_after_stop = True  # Flag to indicate exit after stop
            # If user says no, do nothing and leave the window open
        else:
            # App is not running, just destroy the window and exit
            self.root.destroy()
            # Use root.quit() for a cleaner Tkinter exit
            self.root.quit()

    # Remove _run_app and _cleanup_resources methods - moved to AppLifecycleManager

    def _handle_status_update(self, message):
        """Handle status updates from the AppLifecycleManager."""
        self.status_var.set(message)

    def _handle_error(self, error_message):
        """Handle errors from the AppLifecycleManager."""
        messagebox.showerror("Error", error_message)
        # Ensure UI is reset after an error
        self._handle_stopped()

    def _handle_stopped(self):
        """Handle the app stopping from the AppLifecycleManager."""
        self.status_var.set("Application stopped")
        self.toggle_button.config(
            text="START EYESIGHT", style="Start.TButton", state="normal"
        )
        # If exit was requested on closing, perform the exit now
        if getattr(self, "_exit_after_stop", False):
            self.root.destroy()
            self.root.quit()
            # Force exit after a short delay to ensure the process terminates
            threading.Timer(0.1, os._exit, args=(0,)).start()


def run_gui():
    """Run the Eyesight GUI."""
    print("\n" + "=" * 60)
    print(" " * 15 + "EYESIGHT GUI IS NOW RUNNING")
    print("=" * 60)

    # Set up signal handlers for graceful shutdown
    # Signal handling might need refinement with threading and Tkinter
    # For now, keep the basic exit on SIGINT
    signal.signal(signal.SIGINT, lambda sig, frame: os._exit(0))

    root = tk.Tk()
    EyesightGUI(root)
    root.mainloop()
