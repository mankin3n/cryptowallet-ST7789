# Hardware Tests

This directory contains hardware tests for verifying individual components.

## Available Tests

### Camera Display Test (`test_camera_display.py`)

**Purpose**: Verify camera and display are working correctly by showing live camera feed.

**Usage**:
```bash
python tests/test_camera_display.py
```

**What it does**:
- Initializes camera and display
- Shows live camera feed on ST7789 display
- Displays FPS counter and frame count
- Allows quit with Q key

**Requirements**:
- ST7789 Display connected
- Raspberry Pi Camera Module v2 or v3 connected
- Camera enabled in raspi-config

**Expected result**: You should see live camera feed on the display with an FPS counter in the top-left corner.

**Troubleshooting**:
- If you see "Waiting for camera..." - check camera cable connection
- If display is blank - check display wiring
- If FPS is low (<10) - camera may not be properly initialized

---

### Display Test (`test_display.py`)

**Purpose**: Verify ST7789 display is working correctly.

**Usage**:
```bash
python tests/test_display.py
```

**What it does**:
- Shows color patterns (red, green, blue, white, black)
- Shows color bars
- Shows text with different fonts
- Tests display initialization and rendering

**Requirements**:
- ST7789 Display connected

**Expected result**: Display should show various solid colors and patterns.

---

## Running Tests

All tests can be exited by pressing **Q** on the keyboard.

For automated unit tests, use pytest:
```bash
pytest tests/ -v
```

## Notes

- Hardware tests require actual hardware connected
- Tests use the same configuration as main application (config.py)
- Mock mode is automatically disabled for hardware tests
- Use DEBUG_MODE=True for verbose logging:
  ```bash
  DEBUG_MODE=True python tests/test_camera_display.py
  ```
