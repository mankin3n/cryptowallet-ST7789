"""
Tests for Display Module.

Unit tests for ST7789 display driver.
"""

import pytest
from PIL import Image
import config

# Force mock mode for testing
config.MOCK_HARDWARE = True

from hardware.display import Display, get_display


def test_display_creation():
    """Test display instance creation."""
    display = Display()
    assert display.width == config.DISPLAY_WIDTH
    assert display.height == config.DISPLAY_HEIGHT


def test_display_setup():
    """Test display setup in mock mode."""
    display = Display()
    result = display.setup()
    assert result is True


def test_display_show_image():
    """Test showing image on display."""
    display = Display()
    display.setup()

    # Create test image
    test_image = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), (255, 0, 0))

    # Should not raise exception
    display.show_image(test_image)


def test_display_clear():
    """Test clearing display."""
    display = Display()
    display.setup()

    # Should not raise exception
    display.clear()
    display.clear(config.COLOR_RED)


def test_display_singleton():
    """Test display singleton pattern."""
    display1 = get_display()
    display2 = get_display()

    assert display1 is display2


def test_display_brightness():
    """Test brightness control."""
    display = Display()
    display.setup()

    # Should not raise exception
    display.set_brightness(50)
    display.set_brightness(100)
    display.set_brightness(0)


def test_display_wrong_size_image():
    """Test handling of wrong size image."""
    display = Display()
    display.setup()

    # Create wrong size image
    wrong_image = Image.new('RGB', (100, 100), (0, 255, 0))

    # Should resize automatically
    display.show_image(wrong_image)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
