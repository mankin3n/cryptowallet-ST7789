#!/usr/bin/env python3
"""
Simple ST7789 Display Test Script

This script tests the ST7789 320x240 display with a series of color patterns.
Use this to verify your display hardware is working correctly.

Wiring (BCM GPIO):
    DC  -> GPIO 24 (Pin 18)
    RST -> GPIO 25 (Pin 22)
    BL  -> GPIO 12 (Pin 32)
    CS  -> GPIO 8  (Pin 24)
    SDA -> GPIO 10 (Pin 19)
    SCL -> GPIO 11 (Pin 23)

Usage:
    python test_display.py
"""

import time
from PIL import Image, ImageDraw, ImageFont

try:
    from hardware.st7789_320x240 import ST7789_320x240
    print("✓ ST7789 driver imported successfully")
except ImportError as e:
    print(f"✗ Failed to import ST7789 driver: {e}")
    print("\nMake sure you're running this on a Raspberry Pi with:")
    print("  - RPi.GPIO installed (pip install RPi.GPIO)")
    print("  - spidev installed (pip install spidev)")
    exit(1)


def draw_text_centered(draw, text, y, font, fill=(255, 255, 255)):
    """Draw centered text."""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (320 - text_width) // 2
    draw.text((x, y), text, font=font, fill=fill)


def test_display():
    """Run display tests."""
    print("\n" + "="*50)
    print("ST7789 320x240 Display Test")
    print("="*50)

    # Initialize display
    print("\n[1/7] Initializing display...")
    try:
        display = ST7789_320x240(
            width=320,
            height=240,
            dc_pin=24,      # GPIO 24 (Pin 18)
            rst_pin=25,     # GPIO 25 (Pin 22)
            bl_pin=12,      # GPIO 12 (Pin 32)
            cs_pin=8,       # GPIO 8  (Pin 24)
            spi_bus=0,
            spi_device=0,
            spi_speed_hz=32000000,  # 32 MHz
            use_bcm_numbering=True
        )
        print("✓ Display initialized successfully")
        print(f"  Resolution: {display.width}x{display.height}")
        print(f"  Backlight: ON")
    except Exception as e:
        print(f"✗ Display initialization failed: {e}")
        return False

    time.sleep(1)

    # Test 1: Red screen
    print("\n[2/7] Testing RED screen...")
    try:
        img = Image.new('RGB', (320, 240), (255, 0, 0))
        display.show_image(img)
        print("✓ Red screen displayed")
        time.sleep(2)
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 2: Green screen
    print("\n[3/7] Testing GREEN screen...")
    try:
        img = Image.new('RGB', (320, 240), (0, 255, 0))
        display.show_image(img)
        print("✓ Green screen displayed")
        time.sleep(2)
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 3: Blue screen
    print("\n[4/7] Testing BLUE screen...")
    try:
        img = Image.new('RGB', (320, 240), (0, 0, 255))
        display.show_image(img)
        print("✓ Blue screen displayed")
        time.sleep(2)
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 4: White screen
    print("\n[5/7] Testing WHITE screen...")
    try:
        img = Image.new('RGB', (320, 240), (255, 255, 255))
        display.show_image(img)
        print("✓ White screen displayed")
        time.sleep(2)
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 5: Black screen
    print("\n[6/7] Testing BLACK screen...")
    try:
        img = Image.new('RGB', (320, 240), (0, 0, 0))
        display.show_image(img)
        print("✓ Black screen displayed")
        time.sleep(2)
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 6: Color bars
    print("\n[7/7] Testing COLOR BARS...")
    try:
        img = Image.new('RGB', (320, 240), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        colors = [
            (255, 0, 0),    # Red
            (255, 165, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 255, 255),  # Cyan
            (0, 0, 255),    # Blue
            (255, 0, 255),  # Magenta
            (255, 255, 255) # White
        ]

        bar_height = 240 // len(colors)
        for i, color in enumerate(colors):
            y = i * bar_height
            draw.rectangle([(0, y), (320, y + bar_height)], fill=color)

        display.show_image(img)
        print("✓ Color bars displayed")
        time.sleep(3)
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Test 7: Text display
    print("\n[BONUS] Testing TEXT display...")
    try:
        img = Image.new('RGB', (320, 240), (30, 30, 30))
        draw = ImageDraw.Draw(img)

        try:
            # Try to load a font
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            # Fallback to default font
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        draw_text_centered(draw, "ST7789", 60, font_large, (0, 255, 0))
        draw_text_centered(draw, "320x240", 110, font_small, (255, 255, 255))
        draw_text_centered(draw, "Display Test", 140, font_small, (255, 255, 255))
        draw_text_centered(draw, "SUCCESS!", 180, font_small, (0, 255, 0))

        display.show_image(img)
        print("✓ Text displayed")
        time.sleep(3)
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    # Cleanup
    print("\n[CLEANUP] Turning off display...")
    try:
        display.clear(0x0000)  # Black screen
        display.cleanup()
        print("✓ Display cleanup complete")
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")

    print("\n" + "="*50)
    print("All tests completed successfully! ✓")
    print("="*50)
    print("\nYour display is working correctly.")
    print("Pin configuration verified:")
    print("  DC  = GPIO 24 (Pin 18)")
    print("  RST = GPIO 25 (Pin 22)")
    print("  BL  = GPIO 12 (Pin 32)")
    print("  CS  = GPIO 8  (Pin 24)")
    print("  SDA = GPIO 10 (Pin 19)")
    print("  SCL = GPIO 11 (Pin 23)")

    return True


if __name__ == "__main__":
    try:
        success = test_display()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
