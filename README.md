# SeedSigner Mini - Hardware Security Device

Hardware security device for Raspberry Pi 4B with ST7789 320x240 TFT display, HW-504 joystick input, and camera module. Provides Bitcoin address generation, transaction signing, QR code generation/scanning, and air-gapped wallet functionality.

## Features

- **Bitcoin Wallet Operations**: Generate private keys, derive addresses (legacy/SegWit/native SegWit)
- **Transaction Signing**: Sign Bitcoin transactions and messages with ECDSA
- **QR Code Support**: Generate and scan QR codes for addresses and transactions
- **Camera Integration**: Live camera preview with QR code detection
- **Air-Gapped Security**: Designed to operate without network connectivity
- **Professional UI**: 11-page navigation system with 320x240 display
- **Settings Management**: Brightness, timeout, language configuration

## Hardware Requirements

- **Raspberry Pi 4B** (or compatible)
- **ST7789 TFT Display** (320x240 pixels)
  - Connected via SPI0
  - GPIO pins: DC=25, RST=27, LED=24
- **HW-504 Joystick**
  - Analog input via MCP3008 ADC on SPI1
  - Button on GPIO 23
- **Raspberry Pi Camera Module** v2 or v3 (optional)

## Installation

### 1. Clone Repository

```bash
cd ~
git clone https://github.com/mankin3n/cryptowallet-ST7789.git
cd cryptowallet-ST7789
```

### 2. Install System Dependencies

```bash
sudo apt-get update
# For Raspberry Pi OS Bookworm (or newer), use libtiff6
# For older versions (Buster/Bullseye), use libtiff5
sudo apt-get install -y python3-pip python3-dev python3-pil \
    libopenjp2-7 libtiff6 libatlas-base-dev \
    libzbar0 libzbar-dev
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Enable SPI and Camera (on Raspberry Pi)

```bash
sudo raspi-config
# Navigate to: Interface Options -> SPI -> Enable
# Navigate to: Interface Options -> Camera -> Enable
# Reboot when prompted
```

## Usage

### Run on Raspberry Pi with Hardware

```bash
python main.py
```

### Run in Mock Mode (without hardware)

For development and testing without physical hardware:

```bash
MOCK_HARDWARE=True python main.py
```

### Run Tests

```bash
pytest tests/ -v
```

## Navigation

### Joystick Controls

- **UP/DOWN**: Navigate menus, scroll content
- **LEFT**: Go back to previous page
- **RIGHT**: Enter submenu
- **PRESS** (center button): Select item, confirm action

### Page Structure

1. **Splash Screen** (2s auto-transition)
2. **Home Menu**
   - Verify Signature
   - Generate QR Code
   - View Address
   - Settings
   - About
3. **Settings**
   - Display Brightness (slider 0-100%)
   - Screen Timeout (30s - 10min)
   - Language (English/Finnish)
   - Reset to Defaults

## Configuration

All configuration is in `config.py`. Key settings:

```python
# GPIO Pins (BCM numbering)
ST7789_DC_PIN = 25
ST7789_RST_PIN = 27
ST7789_LED_PIN = 24
JOYSTICK_SW_PIN = 23

# Display
DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 240
DISPLAY_FPS = 30

# Bitcoin Network
BITCOIN_NETWORK = 'testnet'  # Change to 'mainnet' for production
```

## Project Structure

```
cryptowallet/
├── main.py                 # Application entry point
├── config.py              # Configuration constants
├── requirements.txt       # Python dependencies
├── hardware/              # Hardware drivers
│   ├── gpio_manager.py   # GPIO and SPI management
│   ├── display.py        # ST7789 display driver
│   ├── joystick.py       # HW-504 input handler
│   └── camera.py         # RPi Camera controller
├── ui/                    # User interface
│   ├── themes.py         # Colors and fonts
│   ├── widgets.py        # UI components
│   ├── screen_manager.py # Rendering engine
│   ├── menu_system.py    # State machine
│   └── pages.py          # Page renderers (11 pages)
├── crypto/                # Cryptography
│   ├── bitcoin.py        # Bitcoin operations
│   └── signing.py        # ECDSA signing
├── utils/                 # Utilities
│   ├── logger.py         # Logging setup
│   ├── qr_handler.py     # QR generation/scanning
│   └── image_utils.py    # Image processing
└── tests/                 # Unit tests
    ├── test_display.py
    ├── test_joystick.py
    └── test_hardware.py
```

## Security Considerations

⚠️ **IMPORTANT**: This is a prototype/educational project. For production use:

1. **Air-gapped operation**: Run on a device without network connectivity
2. **Secure key storage**: Implement secure element or encrypted storage
3. **Physical security**: Protect device from physical tampering
4. **Code audit**: Have cryptographic code professionally audited
5. **Mainnet caution**: Use testnet for testing, mainnet only after thorough validation

## Troubleshooting

### Display not working

```bash
# Check SPI is enabled
ls /dev/spidev*
# Should show: /dev/spidev0.0 /dev/spidev0.1

# Test permissions
groups | grep spi
# User should be in 'spi' group
```

### Camera not detected

```bash
# Check camera connection
vcgencmd get_camera
# Should show: supported=1 detected=1

# Test camera
libcamera-hello
```

### Permission errors

```bash
# Add user to required groups
sudo usermod -a -G spi,gpio,video $USER
# Logout and login again
```

## Development

### Mock Mode

Use mock mode for development without hardware:

```bash
MOCK_HARDWARE=True python main.py
```

### Debug Mode

Enable debug logging:

```bash
DEBUG_MODE=True python main.py
```

### Code Style

- Type hints on all functions
- Google-style docstrings
- Follow PEP 8 style guide

## License

MIT License - See LICENSE file for details

## References

- [ST7789 Library](https://github.com/gavinlyonsrepo/ST7789_TFT_RPI)
- [SeedSigner Project](https://github.com/SeedSigner/seedsigner)
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [Bitcoin Developer Guide](https://developer.bitcoin.org/)
