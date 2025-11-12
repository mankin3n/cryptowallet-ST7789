# Hardware Wiring Guide

Complete wiring instructions for SeedSigner Mini hardware security device.

## Components Required

| Component | Specifications | Notes |
|-----------|---------------|-------|
| Raspberry Pi 4B | Any RAM variant | 1GB+ recommended |
| ST7789 TFT Display | 320x240 pixels, SPI interface | 2.4" or 2.8" modules |
| HW-504 Joystick Module | 5-axis analog joystick | With center button |
| MCP3008 ADC | 8-channel 10-bit ADC, SPI interface | For joystick analog input |
| Raspberry Pi Camera Module | v2 (8MP) or v3 (12MP) | CSI interface |
| Camera Cable | 15-pin ribbon cable | Length as needed |
| Breadboard | Half-size or larger | For prototyping |
| Jumper Wires | Male-to-Female | ~25 wires needed |
| Power Supply | 5V 3A USB-C | Official RPi power supply recommended |

## Component Overview

### ST7789 Display (SPI0)
- **Interface**: SPI (Serial Peripheral Interface)
- **Resolution**: 320x240 pixels
- **Clock Speed**: 80 MHz
- **Power**: 3.3V logic, ~100mA typical

### HW-504 Joystick + MCP3008 ADC (SPI1)
- **Interface**: Analog (VRx/VRy) + Digital button
- **ADC**: MCP3008 converts analog to SPI
- **Power**: 3.3V or 5V for joystick, 3.3V for MCP3008

### Camera Module (CSI)
- **Interface**: CSI (Camera Serial Interface)
- **Connection**: Dedicated 15-pin ribbon cable
- **Power**: 3.3V from RPi

---

## Raspberry Pi 4B GPIO Pinout Reference

```
     3V3  (1) (2)  5V       ┌─────────────┐
   GPIO2  (3) (4)  5V       │   USB x2    │
   GPIO3  (5) (6)  GND      │   USB x2    │
   GPIO4  (7) (8)  GPIO14   │   Ethernet  │
     GND  (9) (10) GPIO15   └─────────────┘
  GPIO17 (11) (12) GPIO18
  GPIO27 (13) (14) GND
  GPIO22 (15) (16) GPIO23 ◄── Joystick Button
     3V3 (17) (18) GPIO24 ◄── ST7789 DC
  GPIO10 (19) (20) GND
   GPIO9 (21) (22) GPIO25 ◄── ST7789 RST
  GPIO11 (23) (24) GPIO8  ◄── ST7789 CS
     GND (25) (26) GPIO7
   GPIO0 (27) (28) GPIO1
   GPIO5 (29) (30) GND
   GPIO6 (31) (32) GPIO12 ◄── ST7789 BL
  GPIO13 (33) (34) GND
  GPIO19 (35) (36) GPIO16 ◄── MCP3008 CS
  GPIO26 (37) (38) GPIO20 ◄── MCP3008 MOSI
     GND (39) (40) GPIO21 ◄── MCP3008 CLK
```

**SPI0 Pins** (ST7789 Display):
- GPIO 10 (pin 19): MOSI
- GPIO 9 (pin 21): MISO (not used by display)
- GPIO 11 (pin 23): SCLK
- GPIO 8 (pin 24): CE0 (CS)

**SPI1 Pins** (MCP3008 ADC):
- GPIO 20 (pin 38): MOSI
- GPIO 19 (pin 35): MISO
- GPIO 21 (pin 40): SCLK
- GPIO 16 (pin 36): CE0 (CS)

---

## Wiring Instructions

### 1. ST7789 Display (SPI0)

**Pin Connections:**

| ST7789 Pin | RPi GPIO | RPi Pin | Signal | Notes |
|------------|----------|---------|--------|-------|
| VCC | 3.3V | Pin 17 | Power | 3.3V only, NOT 5V |
| GND | GND | Pin 20 | Ground | Common ground |
| SCL (CLK) | GPIO 11 | Pin 23 | SPI0 SCLK | Clock signal |
| SDA (MOSI) | GPIO 10 | Pin 19 | SPI0 MOSI | Data out |
| RES (RST) | GPIO 25 | Pin 22 | Reset | Hardware reset |
| DC (A0) | GPIO 24 | Pin 18 | Data/Command | Register select |
| CS | GPIO 8 | Pin 24 | SPI0 CE0 | Chip select |
| BL (LED) | GPIO 12 | Pin 32 | Backlight | PWM control |

**Connection Steps:**
1. **Power down** the Raspberry Pi completely
2. Connect VCC to 3.3V (pin 17) - **verify 3.3V compatibility first**
3. Connect GND to any ground pin (pin 20 recommended)
4. Connect SCL to GPIO 11 (pin 23)
5. Connect SDA to GPIO 10 (pin 19)
6. Connect RES to GPIO 25 (pin 22)
7. Connect DC to GPIO 24 (pin 18)
8. Connect CS to GPIO 8 (pin 24)
9. Connect BL to GPIO 12 (pin 32)

**Wiring Diagram:**
```
ST7789 Display              Raspberry Pi 4B
┌─────────────┐             ┌──────────────┐
│             │             │              │
│  VCC    ────┼─────────────┤ Pin 17 (3.3V)│
│  GND    ────┼─────────────┤ Pin 20 (GND) │
│  SCL    ────┼─────────────┤ Pin 23 (GP11)│
│  SDA    ────┼─────────────┤ Pin 19 (GP10)│
│  RES    ────┼─────────────┤ Pin 22 (GP25)│
│  DC     ────┼─────────────┤ Pin 18 (GP24)│
│  CS     ────┼─────────────┤ Pin 24 (GP8) │
│  BL     ────┼─────────────┤ Pin 12 (GP18)│
│             │             │              │
└─────────────┘             └──────────────┘
```

---

### 2. MCP3008 ADC (SPI1)

**Pin Connections:**

| MCP3008 Pin | Pin # | RPi GPIO | RPi Pin | Signal |
|-------------|-------|----------|---------|--------|
| VDD | 16 | 3.3V | Pin 1 | Power |
| VREF | 15 | 3.3V | Pin 1 | Reference voltage |
| AGND | 14 | GND | Pin 6 | Analog ground |
| CLK | 13 | GPIO 21 | Pin 40 | SPI1 SCLK |
| DOUT | 12 | GPIO 19 | Pin 35 | SPI1 MISO |
| DIN | 11 | GPIO 20 | Pin 38 | SPI1 MOSI |
| CS/SHDN | 10 | GPIO 16 | Pin 36 | Chip select |
| DGND | 9 | GND | Pin 6 | Digital ground |
| CH0 | 1 | - | - | VRx (joystick X-axis) |
| CH1 | 2 | - | - | VRy (joystick Y-axis) |
| CH2-CH7 | 3-8 | - | - | Unused (future expansion) |

**MCP3008 Pin Layout:**
```
        ┌────────┐
   CH0 -│1    16│- VDD (3.3V)
   CH1 -│2    15│- VREF (3.3V)
   CH2 -│3    14│- AGND (GND)
   CH3 -│4    13│- CLK (GPIO 21)
   CH4 -│5    12│- DOUT (GPIO 19)
   CH5 -│6    11│- DIN (GPIO 20)
   CH6 -│7    10│- CS (GPIO 16)
   CH7 -│8     9│- DGND (GND)
        └────────┘
```

**Connection Steps:**
1. Insert MCP3008 into breadboard (straddle center gap)
2. Connect pin 16 (VDD) to 3.3V (RPi pin 1)
3. Connect pin 15 (VREF) to 3.3V (RPi pin 1)
4. Connect pins 14 & 9 (AGND & DGND) to GND (RPi pin 6)
5. Connect pin 13 (CLK) to GPIO 21 (RPi pin 40)
6. Connect pin 12 (DOUT) to GPIO 19 (RPi pin 35)
7. Connect pin 11 (DIN) to GPIO 20 (RPi pin 38)
8. Connect pin 10 (CS) to GPIO 16 (RPi pin 36)

**Wiring Diagram:**
```
MCP3008 ADC                 Raspberry Pi 4B
┌─────────────┐             ┌──────────────┐
│             │             │              │
│  VDD    ────┼─────────────┤ Pin 1 (3.3V) │
│  VREF   ────┼─────────────┤ Pin 1 (3.3V) │
│  AGND   ────┼─────────────┤ Pin 6 (GND)  │
│  CLK    ────┼─────────────┤ Pin 40 (GP21)│
│  DOUT   ────┼─────────────┤ Pin 35 (GP19)│
│  DIN    ────┼─────────────┤ Pin 38 (GP20)│
│  CS     ────┼─────────────┤ Pin 36 (GP16)│
│  DGND   ────┼─────────────┤ Pin 6 (GND)  │
│             │             │              │
└─────────────┘             └──────────────┘
```

---

### 3. HW-504 Joystick Module

**Pin Connections:**

| HW-504 Pin | Connection | Notes |
|------------|------------|-------|
| GND | GND (breadboard) | Common ground |
| +5V | 5V (RPi pin 2) | Or 3.3V for lower voltage |
| VRx | MCP3008 CH0 (pin 1) | X-axis analog output |
| VRy | MCP3008 CH1 (pin 2) | Y-axis analog output |
| SW | GPIO 23 (RPi pin 16) | Center button (active LOW) |

**Connection Steps:**
1. Connect joystick GND to breadboard ground rail
2. Connect +5V to RPi 5V (pin 2) or 3.3V for reduced range
3. Connect VRx to MCP3008 pin 1 (CH0)
4. Connect VRy to MCP3008 pin 2 (CH1)
5. Connect SW to GPIO 23 (RPi pin 16)
6. **Optional**: Add 10kΩ pull-up resistor from SW to 3.3V (internal pull-up used in software)

**Wiring Diagram:**
```
HW-504 Joystick            MCP3008 / RPi
┌─────────────┐            ┌──────────────┐
│             │            │              │
│  GND    ────┼────────────┤ GND          │
│  +5V    ────┼────────────┤ RPi Pin 2    │
│  VRx    ────┼────────────┤ MCP3008 CH0  │
│  VRy    ────┼────────────┤ MCP3008 CH1  │
│  SW     ────┼────────────┤ GPIO 23      │
│             │            │              │
└─────────────┘            └──────────────┘
```

---

### 4. Camera Module (CSI)

**Connection Steps:**
1. **Power down** the Raspberry Pi
2. Locate the CSI connector (between HDMI ports and USB ports)
3. Gently pull up the black plastic clip
4. Insert ribbon cable with **blue side facing Ethernet port** (contacts facing HDMI)
5. Push down the black clip to secure
6. Connect other end to camera module (blue side facing away from lens)
7. Ensure cable is fully seated on both ends

**Camera Connector Location:**
```
Raspberry Pi 4B (top view)

    ┌─────────────────────────────┐
    │  HDMI    HDMI               │
    │   [0]     [1]         [CSI] │ ◄── Camera connector
    │                       ┌───┐ │     (between HDMI and GPIO)
    │   USB-C               │ █ │ │
    │   Power               └───┘ │
    │                             │
    │  USB  USB  USB  USB         │
    │  [2]  [2]  [3]  [3]         │
    │                   Ethernet  │
    └─────────────────────────────┘
```

**Cable Orientation:**
- **Raspberry Pi side**: Blue tab faces Ethernet port
- **Camera side**: Blue tab faces away from lens
- Contacts face the HDMI ports on RPi
- Ensure cable is not twisted

---

## Complete Wiring Summary

**Power Rails (Breadboard Setup):**
- **3.3V rail**: ST7789 VCC, MCP3008 VDD & VREF
- **5V rail**: HW-504 joystick (optional, can use 3.3V)
- **GND rail**: All component grounds

**GPIO Pin Usage:**

| GPIO | Pin | Function | Component |
|------|-----|----------|-----------|
| GPIO 8 | 24 | SPI0 CE0 (CS) | ST7789 Display |
| GPIO 10 | 19 | SPI0 MOSI | ST7789 Display |
| GPIO 11 | 23 | SPI0 SCLK | ST7789 Display |
| GPIO 12 | 32 | PWM (Backlight) | ST7789 Display |
| GPIO 24 | 18 | Data/Command | ST7789 Display |
| GPIO 25 | 22 | Reset | ST7789 Display |
| GPIO 16 | 36 | SPI1 CE0 (CS) | MCP3008 ADC |
| GPIO 19 | 35 | SPI1 MISO | MCP3008 ADC |
| GPIO 20 | 38 | SPI1 MOSI | MCP3008 ADC |
| GPIO 21 | 40 | SPI1 SCLK | MCP3008 ADC |
| GPIO 23 | 16 | Digital Input | Joystick Button |

---

## Testing & Verification

### 1. Enable SPI Interfaces

```bash
# Enable SPI0 and SPI1
sudo raspi-config
# Navigate to: Interface Options -> SPI -> Enable
sudo reboot

# Verify SPI devices exist
ls -l /dev/spidev*
# Should show:
# /dev/spidev0.0  (SPI0, CE0 - ST7789)
# /dev/spidev0.1  (SPI0, CE1 - unused)
# /dev/spidev1.0  (SPI1, CE0 - MCP3008)
# /dev/spidev1.1  (SPI1, CE1 - unused)
```

### 2. Check GPIO Permissions

```bash
# Add user to required groups
sudo usermod -a -G spi,gpio,video $USER
# Logout and login for changes to take effect

# Verify group membership
groups
# Should include: spi gpio video
```

### 3. Test Camera Connection

```bash
# Enable camera interface
sudo raspi-config
# Navigate to: Interface Options -> Camera -> Enable
sudo reboot

# Check camera detection
vcgencmd get_camera
# Should show: supported=1 detected=1

# Test camera capture
libcamera-hello --timeout 5000
# Should display camera preview for 5 seconds
```

### 4. Test Display (Basic)

```bash
# Install required library
pip install ST7789

# Run test script (create test_display.py)
python3 << EOF
import ST7789
from PIL import Image, ImageDraw

# Initialize display
disp = ST7789.ST7789(
    port=0, cs=0,
    dc=24, rst=25, backlight=18,
    spi_speed_hz=80000000
)

# Create test image
img = Image.new('RGB', (320, 240), color=(0, 255, 0))
draw = ImageDraw.Draw(img)
draw.text((100, 100), "Display Test OK", fill=(0, 0, 0))

# Display image
disp.display(img)
print("Display test complete - check for green screen with text")
EOF
```

### 5. Test Joystick (MCP3008)

```bash
# Install SPI library
pip install spidev

# Run test script
python3 << EOF
import spidev
import time
import RPi.GPIO as GPIO

# Setup button
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Setup SPI for MCP3008
spi = spidev.SpiDev()
spi.open(1, 0)  # SPI1, CE0
spi.max_speed_hz = 1350000

def read_adc(channel):
    if channel < 0 or channel > 7:
        return -1
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

print("Move joystick and press button (Ctrl+C to exit)")
try:
    while True:
        x = read_adc(0)  # CH0 (VRx)
        y = read_adc(1)  # CH1 (VRy)
        button = GPIO.input(23)
        print(f"X: {x:4d}  Y: {y:4d}  Button: {'Released' if button else 'PRESSED'}")
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    spi.close()
    GPIO.cleanup()
EOF
```

**Expected Values:**
- **X/Y range**: 0-1023 (10-bit ADC)
- **Center position**: ~512 (±50)
- **Full left/up**: ~0-50
- **Full right/down**: ~950-1023
- **Button**: HIGH (1) when released, LOW (0) when pressed

### 6. Run Full Application

```bash
# Run in mock mode first (no hardware required)
MOCK_HARDWARE=True python main.py

# Run with real hardware
python main.py
```

---

## Troubleshooting

### Display Issues

**Blank/White Screen:**
- Check 3.3V power connection (NOT 5V)
- Verify SPI0 is enabled: `ls /dev/spidev0.0`
- Check DC and RST pin connections
- Verify GPIO numbering is BCM mode

**Corrupted/Garbled Display:**
- Reduce SPI speed (try 40 MHz instead of 80 MHz)
- Check for loose jumper wires
- Verify MOSI and SCLK connections
- Ensure proper ground connection

**No Backlight:**
- Check BL (LED) pin connection to GPIO 12
- Test PWM: `raspi-gpio set 12 op pn dl`
- Verify backlight pin voltage with multimeter

### Joystick Issues

**No Input Detected:**
- Verify SPI1 is enabled: `ls /dev/spidev1.0`
- Check MCP3008 power (3.3V on pins 15 & 16)
- Test with MCP3008 test script above
- Verify VREF is connected to 3.3V

**Erratic Values:**
- Check joystick power (5V or 3.3V)
- Verify analog ground connections
- Add 0.1µF capacitor across VDD and GND of MCP3008
- Ensure VRx/VRy are connected to correct channels

**Button Not Working:**
- Test with: `raspi-gpio get 23`
- Should show pull-up enabled and current state
- Verify connection to GPIO 23
- Check for hardware debouncing (10kΩ + 0.1µF RC filter)

### Camera Issues

**Camera Not Detected:**
- Check ribbon cable orientation (blue tab position)
- Ensure cable is fully inserted on both ends
- Enable legacy camera: `sudo raspi-config` → Interface → Legacy Camera
- Try different cable (cables can fail)

**Camera Error in Software:**
- Update firmware: `sudo apt update && sudo apt upgrade`
- Install libcamera: `sudo apt install libcamera-apps`
- Check permissions: user in 'video' group

### General Issues

**Permission Denied:**
```bash
sudo chmod 666 /dev/spidev0.0 /dev/spidev1.0
sudo usermod -a -G spi,gpio,video $USER
# Logout and login again
```

**SPI Not Enabled:**
```bash
# Enable SPI via config file
echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
# For SPI1, add:
echo "dtoverlay=spi1-3cs" | sudo tee -a /boot/config.txt
sudo reboot
```

---

## Safety Warnings

1. **ALWAYS power down** Raspberry Pi before connecting/disconnecting components
2. **Verify voltage levels**: ST7789 and MCP3008 are 3.3V devices (NOT 5V tolerant)
3. **Check polarity**: Reversing power can damage components
4. **Avoid shorts**: Keep wires organized and insulated
5. **ESD protection**: Touch grounded metal before handling components
6. **Double-check connections**: Review wiring diagram before powering on

---

## Advanced Configuration

### Multiple SPI Devices on Same Bus

Current configuration uses:
- **SPI0**: ST7789 display only (CE0)
- **SPI1**: MCP3008 ADC only (CE0)

If you need to add more SPI devices, you can use CE1 (chip enable 1):
- **SPI0 CE1**: GPIO 7 (pin 26)
- **SPI1 CE1**: Available via custom device tree overlay

### Enable SPI1 with Multiple Chip Enables

Edit `/boot/config.txt`:
```bash
# Enable SPI1 with 3 chip enables
dtoverlay=spi1-3cs
```

### Custom GPIO Pins

To change pin assignments, edit `config.py`:
```python
# Display pins
ST7789_DC_PIN = 24
ST7789_RST_PIN = 25
ST7789_LED_PIN = 12

# MCP3008 pins
MCP3008_CS_PIN = 16
MCP3008_MOSI_PIN = 20
MCP3008_MISO_PIN = 19
MCP3008_CLK_PIN = 21

# Joystick button
JOYSTICK_SW_PIN = 23
```

---

## Bill of Materials (BOM)

| Item | Quantity | Approximate Cost | Notes |
|------|----------|------------------|-------|
| Raspberry Pi 4B (2GB/4GB) | 1 | $35-55 | 1GB may work but not recommended |
| ST7789 Display (320x240) | 1 | $10-20 | Verify 3.3V compatibility |
| HW-504 Joystick | 1 | $2-5 | Standard analog joystick |
| MCP3008 ADC | 1 | $3-5 | DIP-16 package for breadboard |
| RPi Camera Module v2/v3 | 1 | $20-30 | v3 recommended for better image quality |
| Camera Cable (15-pin) | 1 | $3-5 | Length as needed (6"-12") |
| Breadboard (half-size) | 1 | $5-10 | 400 tie points minimum |
| Jumper Wires (M-F) | 25+ | $5-10 | Assorted colors recommended |
| USB-C Power Supply (5V 3A) | 1 | $8-12 | Official RPi PSU recommended |
| MicroSD Card (16GB+) | 1 | $8-15 | Class 10 or better |
| **Total** | | **$100-170** | Approximate, varies by supplier |

---

## Next Steps

1. **Verify all connections** against diagrams above
2. **Run test scripts** to verify each component
3. **Install software** following README.md
4. **Run in mock mode** to test software without hardware
5. **Deploy to hardware** and test full system integration