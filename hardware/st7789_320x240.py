"""
ST7789 TFT LCD Display Driver for 320x240 Resolution
Compatible with gavinlyonsrepo/ST7789_TFT_RPI wiring scheme

This driver is optimized for the ST7789 2.8" 320x240 SPI TFT LCD display
and uses the same pin configuration as the gavinlyonsrepo/ST7789_TFT_RPI library.

Wiring Configuration (BCM GPIO numbering):
    Display Pin -> Raspberry Pi Pin
    -----------------------------------
    VCC         -> 3.3V (Pin 1 or 17)
    GND         -> Ground (Pin 6, 9, 14, 20, 25, 30, 34, or 39)
    CS          -> GPIO8/CE0 (Pin 24) - Hardware SPI Chip Select
    RESET       -> GPIO25 (Pin 22)
    DC          -> GPIO24 (Pin 18)
    MOSI        -> GPIO10 (Pin 19) - Hardware SPI MOSI
    CLK         -> GPIO11 (Pin 23) - Hardware SPI Clock
    BL          -> GPIO12 (Pin 32) or connect to 3.3V via resistor

IMPORTANT: This is a 3.3V logic device. DO NOT connect to 5V logic.
"""

import array
import spidev
import RPi.GPIO as GPIO
import time
from typing import Optional


class ST7789_320x240:
    """
    ST7789 display driver for 320x240 resolution displays.
    Uses hardware SPI for optimal performance.
    """

    # Display commands
    CMD_SWRESET = 0x01  # Software reset
    CMD_SLPOUT = 0x11   # Sleep out
    CMD_NORON = 0x13    # Normal display mode on
    CMD_INVOFF = 0x20   # Display inversion off
    CMD_INVON = 0x21    # Display inversion on
    CMD_DISPON = 0x29   # Display on
    CMD_CASET = 0x2A    # Column address set
    CMD_RASET = 0x2B    # Row address set
    CMD_RAMWR = 0x2C    # Memory write
    CMD_MADCTL = 0x36   # Memory data access control
    CMD_COLMOD = 0x3A   # Interface pixel format
    CMD_PORCTRL = 0xB2  # Porch control
    CMD_GCTRL = 0xB7    # Gate control
    CMD_VCOMS = 0xBB    # VCOMS setting
    CMD_LCMCTRL = 0xC0  # LCM control
    CMD_VDVVRHEN = 0xC2 # VDV and VRH command enable
    CMD_VRHS = 0xC3     # VRH set
    CMD_VDVS = 0xC4     # VDV set
    CMD_FRCTRL2 = 0xC6  # Frame rate control in normal mode
    CMD_PWCTRL1 = 0xD0  # Power control 1
    CMD_PVGAMCTRL = 0xE0 # Positive voltage gamma control
    CMD_NVGAMCTRL = 0xE1 # Negative voltage gamma control

    def __init__(
        self,
        width: int = 320,
        height: int = 240,
        dc_pin: int = 24,      # BCM GPIO24 (Board Pin 18)
        rst_pin: int = 25,     # BCM GPIO25 (Board Pin 22)
        bl_pin: Optional[int] = 12,  # BCM GPIO12 (Board Pin 32)
        cs_pin: Optional[int] = 8,   # BCM GPIO8/CE0 (Board Pin 24)
        spi_bus: int = 0,
        spi_device: int = 0,
        spi_speed_hz: int = 32000000,  # 32MHz (max recommended)
        use_bcm_numbering: bool = True
    ):
        """
        Initialize ST7789 320x240 display driver.

        Args:
            width: Display width in pixels (default: 320)
            height: Display height in pixels (default: 240)
            dc_pin: Data/Command GPIO pin (BCM numbering by default)
            rst_pin: Reset GPIO pin (BCM numbering by default)
            bl_pin: Backlight GPIO pin (optional, BCM numbering by default)
            cs_pin: Chip Select GPIO pin (optional, BCM numbering by default)
            spi_bus: SPI bus number (0 or 1)
            spi_device: SPI device number (0 or 1)
            spi_speed_hz: SPI clock speed in Hz (max 32MHz recommended)
            use_bcm_numbering: If True, use BCM GPIO numbering; if False, use BOARD numbering
        """
        if width != 320 or height != 240:
            raise ValueError("This driver only supports 320x240 resolution")

        self.width = width
        self.height = height
        self._dc_pin = dc_pin
        self._rst_pin = rst_pin
        self._bl_pin = bl_pin
        self._cs_pin = cs_pin

        # Set GPIO mode
        if use_bcm_numbering:
            GPIO.setmode(GPIO.BCM)
        else:
            GPIO.setmode(GPIO.BOARD)

        GPIO.setwarnings(False)

        # Setup GPIO pins
        GPIO.setup(self._dc_pin, GPIO.OUT)
        GPIO.setup(self._rst_pin, GPIO.OUT)

        if self._bl_pin is not None:
            GPIO.setup(self._bl_pin, GPIO.OUT)
            GPIO.output(self._bl_pin, GPIO.LOW)  # Initially off

        if self._cs_pin is not None:
            GPIO.setup(self._cs_pin, GPIO.OUT)
            GPIO.output(self._cs_pin, GPIO.HIGH)  # Inactive (high)

        # Initialize SPI
        self._spi = spidev.SpiDev(spi_bus, spi_device)
        self._spi.max_speed_hz = spi_speed_hz
        self._spi.mode = 0  # SPI Mode 0 (CPOL=0, CPHA=0)

        # Initialize display
        self.init()

        # Turn on backlight
        if self._bl_pin is not None:
            GPIO.output(self._bl_pin, GPIO.HIGH)

    def _command(self, cmd: int):
        """Send command byte to display."""
        if self._cs_pin is not None:
            GPIO.output(self._cs_pin, GPIO.LOW)

        GPIO.output(self._dc_pin, GPIO.LOW)  # Command mode
        self._spi.writebytes([cmd])

        if self._cs_pin is not None:
            GPIO.output(self._cs_pin, GPIO.HIGH)

    def _data(self, data):
        """Send data byte(s) to display."""
        if self._cs_pin is not None:
            GPIO.output(self._cs_pin, GPIO.LOW)

        GPIO.output(self._dc_pin, GPIO.HIGH)  # Data mode

        if isinstance(data, int):
            self._spi.writebytes([data])
        elif isinstance(data, (bytes, bytearray)):
            self._spi.writebytes2(data)
        else:
            self._spi.writebytes(data)

        if self._cs_pin is not None:
            GPIO.output(self._cs_pin, GPIO.HIGH)

    def reset(self):
        """Perform hardware reset of the display."""
        GPIO.output(self._rst_pin, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self._rst_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self._rst_pin, GPIO.HIGH)
        time.sleep(0.12)  # Wait 120ms after reset

    def init(self):
        """Initialize display with optimal settings for 320x240."""
        self.reset()

        # Software reset
        self._command(self.CMD_SWRESET)
        time.sleep(0.15)

        # Exit sleep mode
        self._command(self.CMD_SLPOUT)
        time.sleep(0.12)

        # Memory Data Access Control - Landscape mode (320x240)
        # MY=0, MX=1, MV=1, ML=0, RGB=0, MH=0
        self._command(self.CMD_MADCTL)
        self._data(0x60)  # Row/Column exchange, Column address order reversed

        # Interface Pixel Format - 16-bit/pixel (RGB565)
        self._command(self.CMD_COLMOD)
        self._data(0x55)

        # Porch Control
        self._command(self.CMD_PORCTRL)
        self._data([0x0C, 0x0C, 0x00, 0x33, 0x33])

        # Gate Control
        self._command(self.CMD_GCTRL)
        self._data(0x35)

        # VCOMS Setting
        self._command(self.CMD_VCOMS)
        self._data(0x28)

        # LCM Control
        self._command(self.CMD_LCMCTRL)
        self._data(0x0C)

        # VDV and VRH Command Enable
        self._command(self.CMD_VDVVRHEN)
        self._data([0x01, 0xFF])

        # VRH Set
        self._command(self.CMD_VRHS)
        self._data(0x10)

        # VDV Set
        self._command(self.CMD_VDVS)
        self._data(0x20)

        # Frame Rate Control
        self._command(self.CMD_FRCTRL2)
        self._data(0x0F)

        # Power Control 1
        self._command(self.CMD_PWCTRL1)
        self._data([0xA4, 0xA1])

        # Positive Voltage Gamma Control
        self._command(self.CMD_PVGAMCTRL)
        self._data([
            0xD0, 0x00, 0x02, 0x07, 0x0A, 0x28, 0x32,
            0x44, 0x42, 0x06, 0x0E, 0x12, 0x14, 0x17
        ])

        # Negative Voltage Gamma Control
        self._command(self.CMD_NVGAMCTRL)
        self._data([
            0xD0, 0x00, 0x02, 0x07, 0x0A, 0x28, 0x31,
            0x54, 0x47, 0x0E, 0x1C, 0x17, 0x1B, 0x1E
        ])

        # Display Inversion On
        self._command(self.CMD_INVON)

        # Normal Display Mode On
        self._command(self.CMD_NORON)
        time.sleep(0.01)

        # Display On
        self._command(self.CMD_DISPON)
        time.sleep(0.12)

    def set_window(self, x_start: int, y_start: int, x_end: int, y_end: int):
        """
        Set the pixel address window for writing data.

        Args:
            x_start: Starting X coordinate
            y_start: Starting Y coordinate
            x_end: Ending X coordinate (inclusive)
            y_end: Ending Y coordinate (inclusive)
        """
        # Column Address Set
        self._command(self.CMD_CASET)
        self._data([
            (x_start >> 8) & 0xFF,
            x_start & 0xFF,
            (x_end >> 8) & 0xFF,
            x_end & 0xFF
        ])

        # Row Address Set
        self._command(self.CMD_RASET)
        self._data([
            (y_start >> 8) & 0xFF,
            y_start & 0xFF,
            (y_end >> 8) & 0xFF,
            y_end & 0xFF
        ])

        # Memory Write
        self._command(self.CMD_RAMWR)

    def show_image(self, image, x_start: int = 0, y_start: int = 0):
        """
        Display a PIL Image on the screen.

        Args:
            image: PIL Image object
            x_start: Starting X coordinate (default: 0)
            y_start: Starting Y coordinate (default: 0)
        """
        img_width, img_height = image.size

        if img_width != self.width or img_height != self.height:
            raise ValueError(
                f'Image must be same dimensions as display ({self.width}x{self.height}). '
                f'Got {img_width}x{img_height}.'
            )

        # Convert image to RGB565 format
        # Convert to BGR;16 (which gives us a weird RGB565-like format)
        # then byteswap to get proper RGB565
        arr = array.array("H", image.convert("BGR;16").tobytes())
        arr.byteswap()
        pixel_data = arr.tobytes()

        # Set window to full screen
        self.set_window(x_start, y_start, self.width - 1, self.height - 1)

        # Send pixel data
        if self._cs_pin is not None:
            GPIO.output(self._cs_pin, GPIO.LOW)

        GPIO.output(self._dc_pin, GPIO.HIGH)  # Data mode
        self._spi.writebytes2(pixel_data)

        if self._cs_pin is not None:
            GPIO.output(self._cs_pin, GPIO.HIGH)

    def clear(self, color: int = 0x0000):
        """
        Clear the display to a specific color.

        Args:
            color: 16-bit RGB565 color value (default: 0x0000 = black)
        """
        # Create buffer with color
        pixel_bytes = bytes([(color >> 8) & 0xFF, color & 0xFF])
        buffer_size = self.width * self.height * 2

        self.set_window(0, 0, self.width - 1, self.height - 1)

        if self._cs_pin is not None:
            GPIO.output(self._cs_pin, GPIO.LOW)

        GPIO.output(self._dc_pin, GPIO.HIGH)  # Data mode

        # Send in chunks for efficiency
        chunk_size = 4096
        full_chunks = buffer_size // chunk_size
        remainder = buffer_size % chunk_size

        chunk_data = pixel_bytes * (chunk_size // 2)

        for _ in range(full_chunks):
            self._spi.writebytes2(chunk_data)

        if remainder > 0:
            self._spi.writebytes2(pixel_bytes * (remainder // 2))

        if self._cs_pin is not None:
            GPIO.output(self._cs_pin, GPIO.HIGH)

    def invert(self, enabled: bool = True):
        """
        Enable or disable display color inversion.

        Args:
            enabled: True to enable inversion, False to disable
        """
        if enabled:
            self._command(self.CMD_INVON)
        else:
            self._command(self.CMD_INVOFF)

    def cleanup(self):
        """Clean up GPIO and SPI resources."""
        if self._bl_pin is not None:
            GPIO.output(self._bl_pin, GPIO.LOW)

        self._spi.close()
        # Note: We don't call GPIO.cleanup() to avoid conflicts with other GPIO usage
