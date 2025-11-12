"""
ST7789 Display Driver.

Wraps a Python ST7789 library to provide support for PIL Images.
Provides high-level methods for rendering images, controlling brightness,
and managing the display lifecycle.
"""
from abc import ABC, abstractmethod

from abc import ABC, abstractmethod
import logging
import time
from typing import Optional
from PIL import Image
import config

# Try to import ST7789 driver
_DISPLAY_MOCK_MODE = config.MOCK_HARDWARE
if not config.MOCK_HARDWARE:
    try:
        from hardware.st7789_320x240 import ST7789_320x240
    except ImportError:
        logging.warning("ST7789 library not available, using mock display")
        _DISPLAY_MOCK_MODE = True

logger = logging.getLogger(__name__)


class DisplayBase(ABC):
    """Abstract base class for display controllers."""

    def __init__(self) -> None:
        self.width: int = config.DISPLAY_WIDTH
        self.height: int = config.DISPLAY_HEIGHT
        self.last_frame_time: float = 0.0
        self.target_frame_time: float = 1.0 / config.DISPLAY_FPS
        logger.info(f"Display created {self.width}x{self.height} @ {config.DISPLAY_FPS}fps (mock={_DISPLAY_MOCK_MODE})")

    @abstractmethod
    def setup(self) -> bool:
        """Initialize the display."""
        pass

    @abstractmethod
    def show_image(self, image: Image.Image) -> None:
        """Display a PIL Image on the screen."""
        pass

    def clear(self, color: tuple[int, int, int] = config.COLOR_BLACK) -> None:
        """Clear display to a solid color."""
        image = Image.new('RGB', (self.width, self.height), color)
        self.show_image(image)

    @abstractmethod
    def set_brightness(self, brightness: int) -> None:
        """Set display backlight brightness."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup display resources."""
        pass


class Display(DisplayBase):
    """ST7789 TFT display controller for real hardware."""

    def __init__(self) -> None:
        """Initialize display controller."""
        super().__init__()
        self.device: Optional[any] = None

    def setup(self) -> bool:
        """Initialize the ST7789 display."""
        try:
            self.device = ST7789_320x240(
                width=self.width,
                height=self.height,
                dc_pin=config.ST7789_DC_PIN,
                rst_pin=config.ST7789_RST_PIN,
                bl_pin=config.ST7789_LED_PIN,
                cs_pin=config.ST7789_CS_PIN,
                spi_bus=config.DISPLAY_SPI_PORT,
                spi_device=0,
                spi_speed_hz=config.DISPLAY_SPI_SPEED,
                use_bcm_numbering=True
            )
            self.clear()
            logger.info("Display initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Display initialization failed: {e}")
            return False

    def show_image(self, image: Image.Image) -> None:
        """Display a PIL Image on the screen."""
        current_time = time.time()
        elapsed = current_time - self.last_frame_time
        if elapsed < self.target_frame_time:
            time.sleep(self.target_frame_time - elapsed)

        try:
            if image.size != (self.width, self.height):
                image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            if self.device:
                self.device.show_image(image)
            self.last_frame_time = time.time()
        except Exception as e:
            logger.error(f"Failed to display image: {e}")

    def set_brightness(self, brightness: int) -> None:
        """Set display backlight brightness."""
        brightness = max(0, min(100, brightness))
        from hardware.gpio_manager import get_gpio_manager
        gpio = get_gpio_manager()
        gpio.set_brightness(brightness)

    def cleanup(self) -> None:
        """Cleanup display resources."""
        try:
            self.clear()
            logger.info("Display cleanup complete")
        except Exception as e:
            logger.error(f"Display cleanup failed: {e}")


class MockDisplay(DisplayBase):
    """Mock display controller for development."""

    def setup(self) -> bool:
        """Mock setup."""
        logger.info("Mock mode: Display setup skipped")
        return True

    def show_image(self, image: Image.Image) -> None:
        """Mock image display."""
        current_time = time.time()
        elapsed = current_time - self.last_frame_time
        if elapsed < self.target_frame_time:
            time.sleep(self.target_frame_time - elapsed)
        self.last_frame_time = time.time()
        logger.debug("Mock mode: Image displayed")

    def set_brightness(self, brightness: int) -> None:
        """Mock brightness setting."""
        brightness = max(0, min(100, brightness))
        logger.debug(f"Mock mode: Brightness set to {brightness}%")

    def cleanup(self) -> None:
        """Mock cleanup."""
        logger.info("Mock mode: Display cleanup skipped")


# Singleton instance
_display: Optional[DisplayBase] = None


def get_display() -> DisplayBase:
    """
    Get singleton display instance.

    Returns:
        Display instance (real or mock)
    """
    global _display
    if _display is None:
        if _DISPLAY_MOCK_MODE:
            _display = MockDisplay()
        else:
            _display = Display()
    return _display
