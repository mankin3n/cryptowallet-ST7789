"""
ST7789 Display Driver.

Wraps the gavinlyonsrepo/ST7789_TFT_RPI library with PIL Image support.
Provides high-level methods for rendering images, controlling brightness,
and managing the display lifecycle.
"""

import logging
import time
from typing import Optional
from PIL import Image
import config

if not config.MOCK_HARDWARE:
    try:
        from ST7789 import ST7789
    except ImportError:
        logging.warning("ST7789 library not available, forcing mock mode")
        config.MOCK_HARDWARE = True

logger = logging.getLogger(__name__)


class Display:
    """
    ST7789 TFT display controller.

    Attributes:
        width: Display width in pixels
        height: Display height in pixels
        device: ST7789 device instance
        last_frame_time: Timestamp of last frame for FPS limiting
    """

    def __init__(self) -> None:
        """Initialize display controller."""
        self.width: int = config.DISPLAY_WIDTH
        self.height: int = config.DISPLAY_HEIGHT
        self.device: Optional[any] = None
        self.last_frame_time: float = 0.0
        self.target_frame_time: float = 1.0 / config.DISPLAY_FPS

        logger.info(f"Display created {self.width}x{self.height} @ {config.DISPLAY_FPS}fps (mock={config.MOCK_HARDWARE})")

    def setup(self) -> bool:
        """
        Initialize the ST7789 display.

        Returns:
            True if initialization successful, False otherwise
        """
        if config.MOCK_HARDWARE:
            logger.info("Mock mode: Display setup skipped")
            return True

        try:
            # Initialize ST7789 with correct pins from config
            self.device = ST7789(
                port=config.DISPLAY_SPI_PORT,
                cs=config.ST7789_CS_PIN,
                dc=config.ST7789_DC_PIN,
                rst=config.ST7789_RST_PIN,
                backlight=config.ST7789_LED_PIN,
                spi_speed_hz=config.DISPLAY_SPI_SPEED,
                width=self.width,
                height=self.height,
                rotation=config.DISPLAY_ROTATION
            )

            # Clear display to black
            self.clear()

            logger.info("Display initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Display initialization failed: {e}")
            return False

    def show_image(self, image: Image.Image) -> None:
        """
        Display a PIL Image on the screen.

        Args:
            image: PIL Image object (must be 320x240 RGB)
        """
        # FPS limiting
        current_time = time.time()
        elapsed = current_time - self.last_frame_time
        if elapsed < self.target_frame_time:
            time.sleep(self.target_frame_time - elapsed)

        if config.MOCK_HARDWARE:
            self.last_frame_time = time.time()
            logger.debug("Mock mode: Image displayed")
            return

        try:
            # Ensure image is correct size and mode
            if image.size != (self.width, self.height):
                image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)

            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Display image
            if self.device:
                self.device.display(image)

            self.last_frame_time = time.time()

        except Exception as e:
            logger.error(f"Failed to display image: {e}")

    def clear(self, color: tuple[int, int, int] = config.COLOR_BLACK) -> None:
        """
        Clear display to a solid color.

        Args:
            color: RGB tuple (default: black)
        """
        image = Image.new('RGB', (self.width, self.height), color)
        self.show_image(image)

    def set_brightness(self, brightness: int) -> None:
        """
        Set display backlight brightness.

        Args:
            brightness: Brightness level (0-100)
        """
        brightness = max(0, min(100, brightness))

        if config.MOCK_HARDWARE:
            logger.debug(f"Mock mode: Brightness set to {brightness}%")
            return

        # Brightness is controlled via GPIO manager PWM
        from hardware.gpio_manager import get_gpio_manager
        gpio = get_gpio_manager()
        gpio.set_brightness(brightness)

    def cleanup(self) -> None:
        """Cleanup display resources."""
        if config.MOCK_HARDWARE:
            logger.info("Mock mode: Display cleanup skipped")
            return

        try:
            self.clear()
            logger.info("Display cleanup complete")
        except Exception as e:
            logger.error(f"Display cleanup failed: {e}")


# Singleton instance
_display: Optional[Display] = None


def get_display() -> Display:
    """
    Get singleton display instance.

    Returns:
        Display instance
    """
    global _display
    if _display is None:
        _display = Display()
    return _display
