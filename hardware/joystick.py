"""
HW-504 Joystick Input Handler.

Reads analog joystick position via MCP3008 ADC and button via GPIO.
Maps analog values to directional inputs (UP/DOWN/LEFT/RIGHT).
Provides debouncing and event queue for input processing.
"""

import logging
import time
import threading
from queue import Queue
from typing import Optional
import config
from hardware.gpio_manager import get_gpio_manager

logger = logging.getLogger(__name__)


class JoystickEvent:
    """
    Represents a joystick input event.

    Attributes:
        direction: Input direction (UP/DOWN/LEFT/RIGHT/PRESS/NONE)
        timestamp: Event timestamp
    """

    def __init__(self, direction: str) -> None:
        """
        Create joystick event.

        Args:
            direction: Input direction constant from config
        """
        self.direction: str = direction
        self.timestamp: float = time.time()

    def __repr__(self) -> str:
        return f"JoystickEvent({self.direction})"


class Joystick:
    """
    HW-504 joystick controller with MCP3008 ADC.

    Attributes:
        gpio: GPIO manager instance
        event_queue: Queue of joystick events
        running: Whether polling thread is running
        last_button_time: Timestamp of last button press (for debouncing)
        last_direction: Last detected direction (for debouncing)
    """

    def __init__(self) -> None:
        """Initialize joystick controller."""
        self.gpio = get_gpio_manager()
        self.event_queue: Queue[JoystickEvent] = Queue()
        self.running: bool = False
        self.poll_thread: Optional[threading.Thread] = None
        self.last_button_time: float = 0.0
        self.last_direction: str = config.INPUT_NONE
        self.last_direction_time: float = 0.0
        self.is_available: bool = False

        logger.info("Joystick controller created")

    def start(self) -> None:
        """Start joystick polling thread."""
        if self.running:
            logger.warning("Joystick already running")
            return

        # Check if ADC SPI is available
        if hasattr(self.gpio, 'adc_spi') and self.gpio.adc_spi is not None:
            self.is_available = True
            logger.info("✓ Joystick ADC (MCP3008) detected")
        else:
            self.is_available = False
            logger.info("  Joystick ADC not available - input disabled")
            logger.info("  → Check MCP3008 wiring and SPI1 enabled")

        self.running = True
        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poll_thread.start()
        logger.info("Joystick polling started")

    def stop(self) -> None:
        """Stop joystick polling thread."""
        self.running = False
        if self.poll_thread:
            self.poll_thread.join(timeout=1.0)
        logger.info("Joystick polling stopped")

    def _poll_loop(self) -> None:
        """Main polling loop (runs in background thread)."""
        poll_interval = 1.0 / config.JOYSTICK_POLL_RATE

        while self.running:
            try:
                # Read analog positions
                x_value = self.gpio.read_adc(config.JOYSTICK_X_CHANNEL)
                y_value = self.gpio.read_adc(config.JOYSTICK_Y_CHANNEL)

                # Map to direction
                direction = self._map_direction(x_value, y_value)

                # Check for direction change with debouncing
                current_time = time.time()
                if direction != config.INPUT_NONE:
                    if direction != self.last_direction or (current_time - self.last_direction_time) > 0.2:
                        self.event_queue.put(JoystickEvent(direction))
                        self.last_direction = direction
                        self.last_direction_time = current_time
                else:
                    self.last_direction = config.INPUT_NONE

                # Read button
                button_pressed = self.gpio.read_button()
                if button_pressed:
                    # Debounce button
                    if (current_time - self.last_button_time) > (config.JOYSTICK_DEBOUNCE_MS / 1000.0):
                        self.event_queue.put(JoystickEvent(config.INPUT_PRESS))
                        self.last_button_time = current_time

                time.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Joystick polling error: {e}")
                time.sleep(poll_interval)

    def _map_direction(self, x: int, y: int) -> str:
        """
        Map analog X/Y values to direction.

        Args:
            x: X-axis ADC value (0-1023)
            y: Y-axis ADC value (0-1023)

        Returns:
            Direction constant (UP/DOWN/LEFT/RIGHT/NONE)
        """
        # Calculate deltas from center
        dx = x - config.JOYSTICK_CENTER
        dy = y - config.JOYSTICK_CENTER

        # Check if within deadzone
        if abs(dx) < config.JOYSTICK_DEADZONE and abs(dy) < config.JOYSTICK_DEADZONE:
            return config.INPUT_NONE

        # Determine primary direction (prefer vertical over horizontal)
        if abs(dy) > abs(dx):
            # Vertical movement
            if dy > config.JOYSTICK_THRESHOLD:
                return config.INPUT_DOWN  # Y increases downward
            elif dy < -config.JOYSTICK_THRESHOLD:
                return config.INPUT_UP
        else:
            # Horizontal movement
            if dx > config.JOYSTICK_THRESHOLD:
                return config.INPUT_RIGHT  # X increases rightward
            elif dx < -config.JOYSTICK_THRESHOLD:
                return config.INPUT_LEFT

        return config.INPUT_NONE

    def get_event(self) -> Optional[JoystickEvent]:
        """
        Get next joystick event from queue.

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
    Get singleton joystick instance.

    Returns:
        Joystick instance
    """
    global _joystick
    if _joystick is None:
        _joystick = Joystick()
    return _joystick
