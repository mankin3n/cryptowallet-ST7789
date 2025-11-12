"""
Configuration file for hardware security device.

Contains all GPIO pins, SPI settings, display parameters, and application
constants. Modify these values to match your hardware setup.
"""

import os
from typing import Final

# ==============================================================================
# ENVIRONMENT
# ==============================================================================

# Mock hardware mode for development without physical GPIO
MOCK_HARDWARE: bool = os.getenv('MOCK_HARDWARE', 'False').lower() == 'true'
DEBUG_MODE: bool = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# ==============================================================================
# GPIO PINS (BCM Numbering)
# ==============================================================================

# ST7789 Display (SPI Port 0)
ST7789_DC_PIN: Final[int] = 24      # Data/Command pin (BOARD Pin 18)
ST7789_RST_PIN: Final[int] = 25     # Reset pin (BOARD Pin 22)
ST7789_LED_PIN: Final[int] = 12     # Backlight (PWM capable, BOARD Pin 32)
ST7789_CS_PIN: Final[int] = 8       # Chip Select (BOARD Pin 24)
ST7789_MOSI_PIN: Final[int] = 10    # SPI0 MOSI (BOARD Pin 19)
ST7789_SCLK_PIN: Final[int] = 11    # SPI0 Clock (BOARD Pin 23)

# MCP3008 ADC for Joystick (SPI Port 1)
MCP3008_CS_PIN: Final[int] = 16     # Chip Select
MCP3008_MOSI_PIN: Final[int] = 20   # SPI1 MOSI
MCP3008_MISO_PIN: Final[int] = 19   # SPI1 MISO
MCP3008_CLK_PIN: Final[int] = 21    # SPI1 Clock

# HW-504 Joystick Button
JOYSTICK_SW_PIN: Final[int] = 23    # Digital button (active LOW)

# ==============================================================================
# SPI CONFIGURATION
# ==============================================================================

# Display SPI
DISPLAY_SPI_PORT: Final[int] = 0
DISPLAY_SPI_DEVICE: Final[int] = 0
DISPLAY_SPI_SPEED: Final[int] = 80_000_000  # 80 MHz

# ADC SPI
ADC_SPI_PORT: Final[int] = 1
ADC_SPI_DEVICE: Final[int] = 0
ADC_SPI_SPEED: Final[int] = 1_000_000       # 1 MHz

# ==============================================================================
# DISPLAY CONFIGURATION
# ==============================================================================

DISPLAY_WIDTH: Final[int] = 320
DISPLAY_HEIGHT: Final[int] = 240
DISPLAY_FPS: Final[int] = 30
DISPLAY_ROTATION: Final[int] = 0            # 0, 90, 180, or 270

# Layout dimensions
HEADER_HEIGHT: Final[int] = 30
STATUS_BAR_HEIGHT: Final[int] = 30
CONTENT_HEIGHT: Final[int] = DISPLAY_HEIGHT - HEADER_HEIGHT - STATUS_BAR_HEIGHT  # 180px

# Margins and padding
MARGIN_SIDE: Final[int] = 10
MARGIN_TOP: Final[int] = 5
PADDING: Final[int] = 5

# ==============================================================================
# JOYSTICK CONFIGURATION
# ==============================================================================

# ADC channels
JOYSTICK_X_CHANNEL: Final[int] = 0
JOYSTICK_Y_CHANNEL: Final[int] = 1

# Analog calibration (10-bit ADC: 0-1023)
JOYSTICK_CENTER: Final[int] = 512
JOYSTICK_DEADZONE: Final[int] = 100         # No movement within ±100 of center
JOYSTICK_THRESHOLD: Final[int] = 300        # Trigger movement at ±300 from center
JOYSTICK_MAX: Final[int] = 1023

# Polling and debouncing
JOYSTICK_POLL_RATE: Final[int] = 100        # Hz (10ms interval)
JOYSTICK_DEBOUNCE_MS: Final[int] = 50       # Button debounce time

# ==============================================================================
# CAMERA CONFIGURATION
# ==============================================================================

CAMERA_RESOLUTION: Final[tuple[int, int]] = (320, 240)
CAMERA_FPS: Final[int] = 15
CAMERA_FORMAT: Final[str] = 'RGB888'
CAMERA_BUFFER_SIZE: Final[int] = 2

# ==============================================================================
# UI CONFIGURATION
# ==============================================================================

# Default settings
UI_BRIGHTNESS: Final[int] = 100             # 0-100%
UI_TIMEOUT: Final[int] = 300                # Seconds (5 minutes)
UI_LANGUAGE: Final[str] = 'en'              # 'en' or 'fi'

# Animation
SPLASH_DURATION: Final[float] = 2.0         # Seconds
SPINNER_FRAME_MS: Final[int] = 200          # Milliseconds per frame
TRANSITION_DURATION: Final[float] = 0.3     # Seconds

# Fonts (will be loaded from system)
FONT_FAMILY: Final[str] = 'DejaVuSansMono'
FONT_SIZE_HEADER: Final[int] = 20
FONT_SIZE_MENU: Final[int] = 16
FONT_SIZE_BODY: Final[int] = 14
FONT_SIZE_STATUS: Final[int] = 11
FONT_SIZE_HINT: Final[int] = 10

# ==============================================================================
# COLOR PALETTE (RGB tuples)
# ==============================================================================

# Hacker Theme Colors
COLOR_BLACK: Final[tuple[int, int, int]] = (0, 0, 0)
COLOR_WHITE: Final[tuple[int, int, int]] = (255, 255, 255)
COLOR_GREEN: Final[tuple[int, int, int]] = (0, 255, 0)
COLOR_DARK_GREEN: Final[tuple[int, int, int]] = (0, 128, 0)
COLOR_RED: Final[tuple[int, int, int]] = (255, 0, 0)
COLOR_ORANGE: Final[tuple[int, int, int]] = (255, 165, 0)
COLOR_CYAN: Final[tuple[int, int, int]] = (0, 255, 255)
COLOR_YELLOW: Final[tuple[int, int, int]] = (255, 255, 0)
COLOR_GRAY: Final[tuple[int, int, int]] = (128, 128, 128)
COLOR_DARK_GRAY: Final[tuple[int, int, int]] = (32, 32, 32)
COLOR_LIGHT_GRAY: Final[tuple[int, int, int]] = (192, 192, 192)

# Modern Theme Colors
COLOR_PRIMARY: Final[tuple[int, int, int]] = (0, 122, 255)
COLOR_SECONDARY: Final[tuple[int, int, int]] = (100, 100, 100)
COLOR_SUCCESS: Final[tuple[int, int, int]] = (40, 167, 69)
COLOR_DANGER: Final[tuple[int, int, int]] = (220, 53, 69)
COLOR_WARNING: Final[tuple[int, int, int]] = (255, 193, 7)
COLOR_INFO: Final[tuple[int, int, int]] = (23, 162, 184)
COLOR_BACKGROUND: Final[tuple[int, int, int]] = (30, 30, 30)
COLOR_SURFACE: Final[tuple[int, int, int]] = (45, 45, 45)
COLOR_TEXT: Final[tuple[int, int, int]] = (220, 220, 220)
COLOR_MUTED: Final[tuple[int, int, int]] = (150, 150, 150)

# ==============================================================================
# BITCOIN CONFIGURATION
# ==============================================================================

BITCOIN_NETWORK: Final[str] = 'testnet'     # 'mainnet' or 'testnet'
BITCOIN_ADDRESS_TYPES: Final[list[str]] = ['legacy', 'segwit', 'native_segwit']

# ==============================================================================
# QR CODE CONFIGURATION
# ==============================================================================

QR_VERSION: Final[int] = 1                  # Auto-size
QR_ERROR_CORRECTION: Final[str] = 'H'       # High (30% recovery)
QR_BOX_SIZE: Final[int] = 10
QR_BORDER: Final[int] = 4
QR_MAX_SIZE: Final[int] = 160               # Max QR code size in pixels

# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================

LOG_LEVEL: Final[str] = 'INFO' if not DEBUG_MODE else 'DEBUG'
LOG_FILE: Final[str] = 'seedsigner.log'
LOG_MAX_BYTES: Final[int] = 10_485_760      # 10 MB
LOG_BACKUP_COUNT: Final[int] = 3
LOG_FORMAT: Final[str] = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ==============================================================================
# PAGE NAMES (State machine)
# ==============================================================================

PAGE_SPLASH: Final[str] = 'SPLASH'
PAGE_HOME: Final[str] = 'HOME'
PAGE_VERIFY_SIGNATURE: Final[str] = 'VERIFY_SIGNATURE'
PAGE_GENERATE_QR: Final[str] = 'GENERATE_QR'
PAGE_VIEW_ADDRESS: Final[str] = 'VIEW_ADDRESS'
PAGE_CAMERA_PREVIEW: Final[str] = 'CAMERA_PREVIEW'
PAGE_SETTINGS: Final[str] = 'SETTINGS'
PAGE_BRIGHTNESS_SETTING: Final[str] = 'BRIGHTNESS_SETTING'
PAGE_TIMEOUT_SETTING: Final[str] = 'TIMEOUT_SETTING'
PAGE_LANGUAGE_SETTING: Final[str] = 'LANGUAGE_SETTING'
PAGE_RESET_SETTING: Final[str] = 'RESET_SETTING'
PAGE_ABOUT: Final[str] = 'ABOUT'
PAGE_LOADING: Final[str] = 'LOADING'
PAGE_ERROR: Final[str] = 'ERROR'
PAGE_CONFIRMATION: Final[str] = 'CONFIRMATION'

# ==============================================================================
# INPUT EVENTS
# ==============================================================================

INPUT_UP: Final[str] = 'UP'
INPUT_DOWN: Final[str] = 'DOWN'
INPUT_LEFT: Final[str] = 'LEFT'
INPUT_RIGHT: Final[str] = 'RIGHT'
INPUT_PRESS: Final[str] = 'PRESS'
INPUT_NONE: Final[str] = 'NONE'
