"""
Tests for Joystick Module.

Unit tests for HW-504 joystick input handler.
"""

import pytest
import time
import config

# Force mock mode for testing
config.MOCK_HARDWARE = True

from hardware.joystick import Joystick, JoystickEvent, get_joystick


def test_joystick_creation():
    """Test joystick instance creation."""
    joystick = Joystick()
    assert joystick.event_queue is not None
    assert joystick.running is False


def test_joystick_event_creation():
    """Test joystick event creation."""
    event = JoystickEvent(config.INPUT_UP)
    assert event.direction == config.INPUT_UP
    assert event.timestamp > 0


def test_joystick_start_stop():
    """Test starting and stopping joystick polling."""
    joystick = Joystick()

    joystick.start()
    assert joystick.running is True

    time.sleep(0.1)  # Let thread start

    joystick.stop()
    assert joystick.running is False


def test_joystick_get_event():
    """Test getting events from queue."""
    joystick = Joystick()

    # Queue should be empty
    event = joystick.get_event()
    assert event is None


def test_joystick_clear_events():
    """Test clearing event queue."""
    joystick = Joystick()

    # Should not raise exception
    joystick.clear_events()


def test_joystick_singleton():
    """Test joystick singleton pattern."""
    joystick1 = get_joystick()
    joystick2 = get_joystick()

    assert joystick1 is joystick2


def test_joystick_direction_mapping():
    """Test analog to direction mapping."""
    joystick = Joystick()

    # Test center (deadzone)
    direction = joystick._map_direction(512, 512)
    assert direction == config.INPUT_NONE

    # Test up
    direction = joystick._map_direction(512, 100)
    assert direction == config.INPUT_UP

    # Test down
    direction = joystick._map_direction(512, 900)
    assert direction == config.INPUT_DOWN

    # Test left
    direction = joystick._map_direction(100, 512)
    assert direction == config.INPUT_LEFT

    # Test right
    direction = joystick._map_direction(900, 512)
    assert direction == config.INPUT_RIGHT


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
