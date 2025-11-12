"""
CLI Input Handler for Terminal Control.

Allows controlling the application via keyboard input from the terminal.
Works in parallel with hardware buttons and in mock mode.

Keyboard Controls:
- Arrow Up / 'w' / '8': UP
- Arrow Down / 's' / '2': DOWN
- Arrow Left / 'a' / '4': BACK
- Arrow Right / 'd' / '6': RIGHT
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
    import select
    _HAS_TERMIOS = True
except ImportError:
    logger.debug("termios not available (Windows?), CLI input disabled")


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
        old_settings: Original terminal settings (for cleanup)
    """

    def __init__(self) -> None:
        """Initialize CLI input handler."""
        self.running: bool = False
        self.input_thread: Optional[threading.Thread] = None
        self.callback: Optional[callable] = None
        self.enabled: bool = False
        self.old_settings = None

        logger.info("CLI Input handler created")

    def start(self, callback: callable) -> None:
        """
        Start CLI input thread.

        Args:
            callback: Function to call with direction string (UP/DOWN/LEFT/PRESS)
        """
        if self.running:
            logger.warning("CLI input already running")
            return

        if not _HAS_TERMIOS:
            logger.info("CLI input not available on this platform")
            return

        self.callback = callback
        self.running = True
        self.enabled = True

        # Save original terminal settings
        try:
            self.old_settings = termios.tcgetattr(sys.stdin)
        except:
            logger.warning("Could not save terminal settings, CLI input disabled")
            self.running = False
            self.enabled = False
            return

        self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self.input_thread.start()

        logger.info("═" * 60)
        logger.info("CLI Keyboard Controls Enabled:")
        logger.info("  ↑/W/8: UP  │  ↓/S/2: DOWN  │  ←/A/4: BACK  │  →/D/6: RIGHT")
        logger.info("  Enter/Space/5: SELECT  │  Q: Quit")
        logger.info("═" * 60)

    def stop(self) -> None:
        """Stop CLI input thread and restore terminal."""
        self.running = False

        # Restore terminal settings
        if self.old_settings and _HAS_TERMIOS:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
            except:
                pass

        if self.input_thread:
            self.input_thread.join(timeout=1.0)

        logger.info("CLI Input stopped")

    def _read_key_nonblocking(self) -> str:
        """
        Read a single key from terminal in non-blocking mode.

        Returns:
            Key character or escape sequence, empty string if no input
        """
        if not _HAS_TERMIOS:
            return ''

        # Check if there's input available
        if not select.select([sys.stdin], [], [], 0)[0]:
            return ''

        try:
            ch = sys.stdin.read(1)

            # Handle arrow keys and escape sequences
            if ch == '\x1b':  # ESC
                # Wait briefly for the rest of the sequence
                # Arrow keys send: ESC [ A/B/C/D
                if select.select([sys.stdin], [], [], 0.01)[0]:
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[':
                        # Read the final character
                        if select.select([sys.stdin], [], [], 0.01)[0]:
                            ch3 = sys.stdin.read(1)
                            # Return complete escape sequence
                            return ch + ch2 + ch3
                    # Return what we have
                    return ch + ch2
                # Just ESC pressed alone
                return ch

            return ch

        except Exception as e:
            logger.debug(f"Key read error: {e}")
            return ''

    def _input_loop(self) -> None:
        """Main input loop (runs in background thread)."""
        # Set terminal to cbreak mode (not full raw mode)
        try:
            tty.setcbreak(sys.stdin.fileno())
        except:
            logger.error("Failed to set terminal mode, CLI input disabled")
            self.running = False
            return

        logger.debug("CLI input loop started")

        while self.running:
            try:
                # Read key in non-blocking mode
                key = self._read_key_nonblocking()

                if not key:
                    time.sleep(0.05)
                    continue

                # Map keys to directions
                direction = None

                # UP (Arrow Up or w or 8)
                if key in ['\x1b[A', 'w', 'W', '8']:
                    direction = config.INPUT_UP
                    logger.debug(f"CLI key: UP ({repr(key)})")

                # DOWN (Arrow Down or s or 2)
                elif key in ['\x1b[B', 's', 'S', '2']:
                    direction = config.INPUT_DOWN
                    logger.debug(f"CLI key: DOWN ({repr(key)})")

                # LEFT/BACK (Arrow Left or a or 4)
                elif key in ['\x1b[D', 'a', 'A', '4']:
                    direction = config.INPUT_LEFT
                    logger.debug(f"CLI key: BACK ({repr(key)})")

                # RIGHT (Arrow Right or d or 6)
                elif key in ['\x1b[C', 'd', 'D', '6']:
                    direction = config.INPUT_RIGHT
                    logger.debug(f"CLI key: RIGHT ({repr(key)})")

                # SELECT (Enter, Space, or numpad 5)
                elif key in ['\r', '\n', ' ', '5']:
                    direction = config.INPUT_PRESS
                    logger.debug(f"CLI key: SELECT ({repr(key)})")

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
                    self.callback(direction)

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
