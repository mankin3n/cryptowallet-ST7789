"""
CLI Input Handler for Terminal Control.

Allows controlling the application via keyboard input from the terminal.
Works in parallel with hardware buttons and in mock mode.

Keyboard Controls:
- Arrow Up / 'w' / '8': UP
- Arrow Down / 's' / '2': DOWN
- Enter / Space / '5': SELECT
- 'q': Quit application
"""

import logging
import sys
import threading
import time
from typing import Optional
import config

logger = logging.getLogger(__name__)

# Try to import termios for Unix-like systems
_HAS_TERMIOS = False
try:
    import termios
    import tty
    _HAS_TERMIOS = True
except ImportError:
    logger.debug("termios not available (Windows?), using simplified input")


class CLIInput:
    """
    CLI input handler for keyboard control.

    Reads keyboard input in a background thread and converts to input events
    that can be consumed by the joystick module.

    Attributes:
        running: Whether input thread is active
        input_thread: Background thread for reading input
        callback: Function to call with input events
        enabled: Whether CLI input is enabled
    """

    def __init__(self) -> None:
        """Initialize CLI input handler."""
        self.running: bool = False
        self.input_thread: Optional[threading.Thread] = None
        self.callback: Optional[callable] = None
        self.enabled: bool = False

        logger.info("CLI Input handler created")

    def start(self, callback: callable) -> None:
        """
        Start CLI input thread.

        Args:
            callback: Function to call with direction string (UP/DOWN/PRESS)
        """
        if self.running:
            logger.warning("CLI input already running")
            return

        self.callback = callback
        self.running = True
        self.enabled = True

        self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self.input_thread.start()

        logger.info("CLI Input started")
        logger.info("Keyboard controls:")
        logger.info("  ↑/w/8: UP  |  ↓/s/2: DOWN  |  Enter/Space/5: SELECT  |  q: Quit")

    def stop(self) -> None:
        """Stop CLI input thread."""
        self.running = False
        if self.input_thread:
            self.input_thread.join(timeout=1.0)
        logger.info("CLI Input stopped")

    def _read_key_unix(self) -> str:
        """
        Read a single key from terminal (Unix/Linux/Mac).

        Returns:
            Key character or escape sequence
        """
        if not _HAS_TERMIOS:
            return ''

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)

            # Handle arrow keys (escape sequences)
            if ch == '\x1b':  # ESC
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    return f'\x1b[{ch3}'

            return ch

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _read_key_simple(self) -> str:
        """
        Read a single line from stdin (fallback for Windows).

        Returns:
            First character of input line
        """
        try:
            line = input().strip()
            if line:
                return line[0].lower()
            return ''
        except EOFError:
            return ''

    def _input_loop(self) -> None:
        """Main input loop (runs in background thread)."""
        logger.info("CLI input loop started (press keys to control)")

        while self.running:
            try:
                # Read key based on platform
                if _HAS_TERMIOS:
                    key = self._read_key_unix()
                else:
                    key = self._read_key_simple()

                if not key:
                    time.sleep(0.01)
                    continue

                # Map keys to directions
                direction = None

                # UP
                if key in ['\x1b[A', 'w', 'W', '8']:
                    direction = config.INPUT_UP

                # DOWN
                elif key in ['\x1b[B', 's', 'S', '2']:
                    direction = config.INPUT_DOWN

                # SELECT (Enter, Space, or numpad 5)
                elif key in ['\r', '\n', ' ', '5']:
                    direction = config.INPUT_PRESS

                # QUIT
                elif key in ['q', 'Q']:
                    logger.info("Quit command received from CLI")
                    # Signal application to quit
                    import signal
                    import os
                    os.kill(os.getpid(), signal.SIGINT)
                    return

                # Send event via callback
                if direction and self.callback:
                    logger.debug(f"CLI input: {direction}")
                    self.callback(direction)

                # Small delay to prevent excessive CPU usage
                time.sleep(0.05)

            except Exception as e:
                logger.error(f"CLI input error: {e}")
                time.sleep(0.1)

    def is_enabled(self) -> bool:
        """
        Check if CLI input is enabled.

        Returns:
            True if enabled, False otherwise
        """
        return self.enabled


# Singleton instance
_cli_input: Optional[CLIInput] = None


def get_cli_input() -> CLIInput:
    """
    Get singleton CLI input instance.

    Returns:
        CLIInput instance
    """
    global _cli_input
    if _cli_input is None:
        _cli_input = CLIInput()
    return _cli_input
