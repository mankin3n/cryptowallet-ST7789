"""
Tests for Display Module.

Unit tests for ST7789 display driver.
"""

import pytest
from PIL import Image
import config

# Force mock mode for testing
config.MOCK_HARDWARE = True

from hardware.display import get_display, DisplayBase
import hardware.display as display_module

@pytest.fixture(autouse=True)
def reset_display_singleton():
    """Reset the display singleton before each test."""
    display_module._display = None

@pytest.fixture
def display() -> DisplayBase:
    """Provides a display instance for tests."""
    return get_display()


def test_display_creation(display: DisplayBase):
    """Test display instance creation."""
    assert display.width == config.DISPLAY_WIDTH
    assert display.height == config.DISPLAY_HEIGHT


def test_display_setup(display: DisplayBase):
    """Test display setup in mock mode."""
    result = display.setup()
    assert result is True


def test_display_show_image(display: DisplayBase):
    """Test showing image on display."""
    display.setup()
    test_image = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), (255, 0, 0))
    display.show_image(test_image)


def test_display_clear(display: DisplayBase):
    """Test clearing display."""
    display.setup()
    display.clear()
    display.clear(config.COLOR_RED)


def test_display_singleton():
    """Test display singleton pattern."""
    display1 = get_display()
    display2 = get_display()
    assert display1 is display2


def test_display_brightness(display: DisplayBase):
    """Test brightness control."""
    display.setup()
    display.set_brightness(50)
    display.set_brightness(100)
    display.set_brightness(0)


def test_display_wrong_size_image(display: DisplayBase):
    """Test handling of wrong size image."""
    display.setup()
    wrong_image = Image.new('RGB', (100, 100), (0, 255, 0))
    display.show_image(wrong_image)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
