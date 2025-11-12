"""
GPIO Manager for hardware initialization and cleanup.

Handles SPI port setup, GPIO pin configuration, and cleanup on exit.
Supports mock mode for development without physical hardware.
"""

import logging
from typing import Optional
import config

# Try to import GPIO libraries
_GPIO_MOCK_MODE = config.MOCK_HARDWARE
if not config.MOCK_HARDWARE:
    try:
        import RPi.GPIO as GPIO
        import spidev
    except ImportError:
        logging.warning("RPi.GPIO or spidev not available, using mock GPIO")
        _GPIO_MOCK_MODE = True

logger = logging.getLogger(__name__)


class GPIOManager:
    """
    Manages GPIO pins and SPI interfaces for the hardware security device.

    Attributes:
        display_spi: SPI device for ST7789 display
        adc_spi: SPI device for MCP3008 ADC
        initialized: Whether GPIO has been initialized
    """

    def __init__(self) -> None:
        """Initialize GPIO manager."""
        self.display_spi: Optional[any] = None
        self.adc_spi: Optional[any] = None
        self.initialized: bool = False

        logger.info(f"GPIO Manager created (mock_mode={_GPIO_MOCK_MODE})")

    def setup(self) -> bool:
        """
        Setup GPIO pins and SPI interfaces.

        Returns:
            True if setup successful, False otherwise
        """
        if self.initialized:
            logger.warning("GPIO already initialized")
            return True

        if _GPIO_MOCK_MODE:
            logger.info("Mock mode: Skipping GPIO setup")
            self.initialized = True
            return True

        try:
            # Setup GPIO mode
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)

            # Setup display pins (optional - display driver handles its own GPIO)
            try:
                GPIO.setup(config.ST7789_DC_PIN, GPIO.OUT)
                GPIO.setup(config.ST7789_RST_PIN, GPIO.OUT)
                GPIO.setup(config.ST7789_LED_PIN, GPIO.OUT)

                # Initialize display backlight PWM
                self.backlight_pwm = GPIO.PWM(config.ST7789_LED_PIN, 1000)  # 1kHz
                self.backlight_pwm.start(config.UI_BRIGHTNESS)
                logger.info("Display GPIO pins configured")
            except Exception as e:
                logger.warning(f"Display GPIO setup failed: {e}")

            # Setup joystick button pin
            try:
                GPIO.setup(config.JOYSTICK_SW_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                logger.info("Joystick button configured")
            except Exception as e:
                logger.warning(f"Joystick button setup failed: {e}")

            # Setup SPI for display (Port 0) - optional, display driver handles its own SPI
            try:
                self.display_spi = spidev.SpiDev()
                self.display_spi.open(config.DISPLAY_SPI_PORT, config.DISPLAY_SPI_DEVICE)
                self.display_spi.max_speed_hz = config.DISPLAY_SPI_SPEED
                self.display_spi.mode = 0
                logger.info(f"Display SPI configured (Port {config.DISPLAY_SPI_PORT})")
            except Exception as e:
                logger.warning(f"Display SPI setup failed: {e}")
                self.display_spi = None

            # Setup SPI for ADC (Port 1)
            try:
                self.adc_spi = spidev.SpiDev()
                self.adc_spi.open(config.ADC_SPI_PORT, config.ADC_SPI_DEVICE)
                self.adc_spi.max_speed_hz = config.ADC_SPI_SPEED
                self.adc_spi.mode = 0
                logger.info(f"ADC SPI configured (Port {config.ADC_SPI_PORT})")
            except Exception as e:
                logger.warning(f"ADC SPI setup failed: {e}")
                self.adc_spi = None

            self.initialized = True
            logger.info("GPIO setup complete (some components may be unavailable)")
            return True

        except Exception as e:
            logger.error(f"GPIO setup failed completely: {e}")
            # Don't fail - allow app to continue in degraded mode
            self.initialized = True
            logger.warning("Continuing with limited GPIO functionality")
            return True

    def set_brightness(self, brightness: int) -> None:
        """
        Set display backlight brightness.

        Args:
            brightness: Brightness level (0-100)
        """
        brightness = max(0, min(100, brightness))

        if _GPIO_MOCK_MODE:
            logger.debug(f"Mock mode: Set brightness to {brightness}%")
            return

        if hasattr(self, 'backlight_pwm'):
            self.backlight_pwm.ChangeDutyCycle(brightness)
            logger.debug(f"Brightness set to {brightness}%")

    def read_button(self) -> bool:
        """
        Read joystick button state.

        Returns:
            True if button is pressed, False otherwise
        """
        if _GPIO_MOCK_MODE:
            return False

        try:
            # Button is active LOW (pressed = 0)
            return GPIO.input(config.JOYSTICK_SW_PIN) == GPIO.LOW
        except Exception as e:
            logger.error(f"Button read failed: {e}")
            return False

    def read_adc(self, channel: int) -> int:
        """
        Read analog value from MCP3008 ADC channel.

        Args:
            channel: ADC channel (0-7)

        Returns:
            10-bit ADC value (0-1023)
        """
        if _GPIO_MOCK_MODE:
            return config.JOYSTICK_CENTER

        if not self.adc_spi:
            logger.error("ADC SPI not initialized")
            return config.JOYSTICK_CENTER

        try:
            # MCP3008 command structure
            # Start bit, single-ended mode, channel select
            command = [1, (8 + channel) << 4, 0]
            response = self.adc_spi.xfer2(command)

            # Extract 10-bit value
            value = ((response[1] & 3) << 8) + response[2]
            return value

        except Exception as e:
            logger.error(f"ADC read failed on channel {channel}: {e}")
            return config.JOYSTICK_CENTER

    def cleanup(self) -> None:
        """Cleanup GPIO pins and close SPI interfaces."""
        if _GPIO_MOCK_MODE:
            logger.info("Mock mode: Skipping GPIO cleanup")
            return

        try:
            if hasattr(self, 'backlight_pwm'):
                self.backlight_pwm.stop()

            if self.display_spi:
                self.display_spi.close()

            if self.adc_spi:
                self.adc_spi.close()

            GPIO.cleanup()
            logger.info("GPIO cleanup complete")

        except Exception as e:
            logger.error(f"GPIO cleanup failed: {e}")

        finally:
            self.initialized = False


# Singleton instance
_gpio_manager: Optional[GPIOManager] = None


def get_gpio_manager() -> GPIOManager:
    """
    Get singleton GPIO manager instance.

    Returns:
        GPIOManager instance
    """
    global _gpio_manager
    if _gpio_manager is None:
        _gpio_manager = GPIOManager()
    return _gpio_manager
