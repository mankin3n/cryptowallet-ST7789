"""
Button Input Handler.

Reads button states from GPIO pins and maps to directional inputs.
Provides debouncing and event queue for input processing.

Hardware: 3 tactile push buttons
- UP button: GPIO 17 (BOARD Pin 11)
- DOWN button: GPIO 22 (BOARD Pin 15)
- SELECT button: GPIO 23 (BOARD Pin 16)
- Wiring: Connect one side of button to GPIO pin, other side to GND
- Internal pull-up resistors enabled (buttons are active LOW)
"""

import logging
import time
import threading
from queue import Queue
from typing import Optional
import config

logger = logging.getLogger(__name__)

# Try to import GPIO library
_BUTTON_MOCK_MODE = config.MOCK_HARDWARE
if not config.MOCK_HARDWARE:
    try:
        import RPi.GPIO as GPIO
    except ImportError:
        logging.warning("RPi.GPIO not available, buttons will be disabled")
        _BUTTON_MOCK_MODE = True


class JoystickEvent:
    """
    Represents a button input event.

    Attributes:
        direction: Input direction (UP/DOWN/PRESS/NONE)
        timestamp: Event timestamp
    """

    def __init__(self, direction: str) -> None:
        """
        Create button event.

        Args:
            direction: Input direction constant from config
        """
        self.direction: str = direction
        self.timestamp: float = time.time()

    def __repr__(self) -> str:
        return f"JoystickEvent({self.direction})"


class Joystick:
    """
    Button input controller.

    Reads 3 tactile buttons via GPIO pins with internal pull-up resistors.
    Buttons are active LOW (pressed = LOW, released = HIGH).

    Attributes:
        event_queue: Queue of button events
        running: Whether polling thread is running
        last_button_times: Dictionary tracking last press time for each button
        is_available: Whether button GPIO is available
    """

    def __init__(self) -> None:
        """Initialize button controller."""
        self.event_queue: Queue[JoystickEvent] = Queue()
        self.running: bool = False
        self.poll_thread: Optional[threading.Thread] = None
        self.last_button_times: dict[int, float] = {
            config.BUTTON_UP_PIN: 0.0,
            config.BUTTON_DOWN_PIN: 0.0,
            config.BUTTON_SELECT_PIN: 0.0
        }
        self.is_available: bool = False

        logger.info("Button input controller created")

    def start(self) -> None:
        """Start button polling thread."""
        if self.running:
            logger.warning("Button polling already running")
            return

        # Setup GPIO pins for buttons
        if _BUTTON_MOCK_MODE:
            self.is_available = False
            logger.info("  Buttons in mock mode (RPi.GPIO not available)")
            logger.info("  → Install with: pip install RPi.GPIO")
        else:
            try:
                logger.info("Attempting to initialize button inputs...")

                # GPIO should already be set to BCM mode by gpio_manager
                # Setup button pins as inputs with pull-up resistors
                GPIO.setup(config.BUTTON_UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.setup(config.BUTTON_DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.setup(config.BUTTON_SELECT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

                self.is_available = True
                logger.info("✓ Button inputs configured:")
                logger.info(f"  - UP: GPIO {config.BUTTON_UP_PIN}")
                logger.info(f"  - DOWN: GPIO {config.BUTTON_DOWN_PIN}")
                logger.info(f"  - SELECT: GPIO {config.BUTTON_SELECT_PIN}")
            except Exception as e:
                self.is_available = False
                logger.warning(f"Button GPIO setup failed: {e}")
                logger.info("  → Check GPIO permissions and wiring")

        self.running = True
        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poll_thread.start()
        logger.info("Button polling started")

    def stop(self) -> None:
        """Stop button polling thread."""
        self.running = False
        if self.poll_thread:
            self.poll_thread.join(timeout=1.0)
        logger.info("Button polling stopped")

    def _read_button(self, pin: int) -> bool:
        """
        Read button state from GPIO pin.

        Args:
            pin: GPIO pin number

        Returns:
            True if button pressed, False otherwise
        """
        if not self.is_available:
            return False

        try:
            # Button is active LOW (pressed = 0, released = 1)
            return GPIO.input(pin) == GPIO.LOW
        except Exception as e:
            logger.debug(f"Button read error on GPIO {pin}: {e}")
            return False

    def _poll_loop(self) -> None:
        """Main polling loop (runs in background thread)."""
        poll_interval = 1.0 / config.BUTTON_POLL_RATE

        while self.running:
            try:
                if not self.is_available:
                    # Just sleep if buttons not available
                    time.sleep(poll_interval)
                    continue

                current_time = time.time()

                # Check UP button
                if self._read_button(config.BUTTON_UP_PIN):
                    if (current_time - self.last_button_times[config.BUTTON_UP_PIN]) > (config.BUTTON_DEBOUNCE_MS / 1000.0):
                        self.event_queue.put(JoystickEvent(config.INPUT_UP))
                        self.last_button_times[config.BUTTON_UP_PIN] = current_time

                # Check DOWN button
                if self._read_button(config.BUTTON_DOWN_PIN):
                    if (current_time - self.last_button_times[config.BUTTON_DOWN_PIN]) > (config.BUTTON_DEBOUNCE_MS / 1000.0):
                        self.event_queue.put(JoystickEvent(config.INPUT_DOWN))
                        self.last_button_times[config.BUTTON_DOWN_PIN] = current_time

                # Check SELECT button
                if self._read_button(config.BUTTON_SELECT_PIN):
                    if (current_time - self.last_button_times[config.BUTTON_SELECT_PIN]) > (config.BUTTON_DEBOUNCE_MS / 1000.0):
                        self.event_queue.put(JoystickEvent(config.INPUT_PRESS))
                        self.last_button_times[config.BUTTON_SELECT_PIN] = current_time

                time.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Button polling error: {e}")
                time.sleep(poll_interval)

    def get_event(self) -> Optional[JoystickEvent]:
        """
        Get next button event from queue.

        Returns:
            JoystickEvent or None if queue empty
        """
        if not self.event_queue.empty():
            return self.event_queue.get()
        return None

    def clear_events(self) -> None:
        """Clear all pending events from queue."""
        while not self.event_queue.empty():
            self.event_queue.get()


# Singleton instance
_joystick: Optional[Joystick] = None


def get_joystick() -> Joystick:
    """
    Get singleton button input instance.

    Returns:
        Joystick (button input) instance
    """
    global _joystick
    if _joystick is None:
        _joystick = Joystick()
    return _joystick
