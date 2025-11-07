"""
Tests for Hardware Module Integration.

Integration tests for GPIO manager and hardware coordination.
"""

import pytest
import config

# Force mock mode for testing
config.MOCK_HARDWARE = True

from hardware.gpio_manager import GPIOManager, get_gpio_manager
from hardware.display import get_display
from hardware.joystick import get_joystick
from hardware.camera import get_camera


def test_gpio_manager_creation():
    """Test GPIO manager instance creation."""
    gpio = GPIOManager()
    assert gpio.initialized is False


def test_gpio_manager_setup():
    """Test GPIO manager setup in mock mode."""
    gpio = GPIOManager()
    result = gpio.setup()
    assert result is True
    assert gpio.initialized is True


def test_gpio_manager_brightness():
    """Test GPIO brightness control."""
    gpio = GPIOManager()
    gpio.setup()

    # Should not raise exception
    gpio.set_brightness(50)
    gpio.set_brightness(100)
    gpio.set_brightness(0)


def test_gpio_manager_button():
    """Test GPIO button reading."""
    gpio = GPIOManager()
    gpio.setup()

    # In mock mode, should return False
    state = gpio.read_button()
    assert state is False


def test_gpio_manager_adc():
    """Test GPIO ADC reading."""
    gpio = GPIOManager()
    gpio.setup()

    # In mock mode, should return center value
    value = gpio.read_adc(0)
    assert value == config.JOYSTICK_CENTER


def test_gpio_manager_cleanup():
    """Test GPIO cleanup."""
    gpio = GPIOManager()
    gpio.setup()

    # Should not raise exception
    gpio.cleanup()


def test_gpio_manager_singleton():
    """Test GPIO manager singleton pattern."""
    gpio1 = get_gpio_manager()
    gpio2 = get_gpio_manager()

    assert gpio1 is gpio2


def test_all_hardware_initialization():
    """Test initializing all hardware components."""
    gpio = get_gpio_manager()
    display = get_display()
    joystick = get_joystick()
    camera = get_camera()

    # Setup all
    assert gpio.setup() is True
    assert display.setup() is True
    assert camera.setup() is True

    # Start joystick
    joystick.start()
    assert joystick.running is True

    # Cleanup
    joystick.stop()
    camera.cleanup()
    display.cleanup()
    gpio.cleanup()


def test_hardware_coordination():
    """Test coordination between hardware components."""
    gpio = get_gpio_manager()
    display = get_display()
    joystick = get_joystick()

    # Setup
    gpio.setup()
    display.setup()
    joystick.start()

    # Test brightness through both interfaces
    gpio.set_brightness(75)
    display.set_brightness(50)

    # Cleanup
    joystick.stop()
    gpio.cleanup()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
