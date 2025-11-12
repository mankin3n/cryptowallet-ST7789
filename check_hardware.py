#!/usr/bin/env python3
"""
Hardware Diagnostic Script

Checks if all required hardware interfaces are available.
"""

import os
import sys

def check_spi():
    """Check if SPI is enabled and accessible."""
    print("\n" + "="*50)
    print("Checking SPI Interface")
    print("="*50)

    spi_devices = ['/dev/spidev0.0', '/dev/spidev0.1', '/dev/spidev1.0']
    found = []

    for device in spi_devices:
        if os.path.exists(device):
            print(f"✓ {device} exists")
            if os.access(device, os.R_OK | os.W_OK):
                print(f"  ✓ Read/write access OK")
                found.append(device)
            else:
                print(f"  ✗ No read/write permission")
                print(f"    Run: sudo usermod -a -G spi $USER")
                print(f"    Then logout and login again")
        else:
            print(f"✗ {device} not found")

    if not found:
        print("\n⚠ SPI not enabled!")
        print("To enable SPI:")
        print("  1. Run: sudo raspi-config")
        print("  2. Go to: Interface Options -> SPI")
        print("  3. Select: Yes")
        print("  4. Reboot")
        return False

    return True

def check_gpio():
    """Check if GPIO is accessible."""
    print("\n" + "="*50)
    print("Checking GPIO")
    print("="*50)

    try:
        import RPi.GPIO as GPIO
        print("✓ RPi.GPIO library installed")

        # Try to set mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        print("✓ GPIO access OK")

        # Test a pin
        try:
            GPIO.setup(24, GPIO.OUT)
            print("✓ Can configure GPIO pins")
            GPIO.cleanup()
        except Exception as e:
            print(f"✗ Cannot configure GPIO: {e}")
            print("  Run: sudo usermod -a -G gpio $USER")
            print("  Then logout and login again")
            return False

        return True

    except ImportError:
        print("✗ RPi.GPIO not installed")
        print("  Install with: pip install RPi.GPIO")
        return False
    except Exception as e:
        print(f"✗ GPIO error: {e}")
        return False

def check_spidev():
    """Check if spidev library is available."""
    print("\n" + "="*50)
    print("Checking spidev Library")
    print("="*50)

    try:
        import spidev
        print("✓ spidev library installed")

        # Try to open SPI
        try:
            spi = spidev.SpiDev()
            spi.open(0, 0)
            print("✓ Can open SPI device")
            spi.close()
            return True
        except FileNotFoundError:
            print("✗ SPI device not found")
            print("  SPI needs to be enabled (see above)")
            return False
        except PermissionError:
            print("✗ No permission to access SPI")
            print("  Run: sudo usermod -a -G spi $USER")
            print("  Then logout and login again")
            return False

    except ImportError:
        print("✗ spidev not installed")
        print("  Install with: pip install spidev")
        return False

def check_pillow():
    """Check if Pillow is installed."""
    print("\n" + "="*50)
    print("Checking Pillow (PIL)")
    print("="*50)

    try:
        from PIL import Image
        print("✓ Pillow library installed")

        # Test creating an image
        img = Image.new('RGB', (320, 240), (0, 0, 0))
        print("✓ Can create images")
        return True

    except ImportError:
        print("✗ Pillow not installed")
        print("  Install with: pip install Pillow")
        return False

def main():
    print("\n" + "="*50)
    print("HARDWARE DIAGNOSTIC CHECK")
    print("ST7789 Display Requirements")
    print("="*50)

    results = {
        'SPI Interface': check_spi(),
        'GPIO Access': check_gpio(),
        'spidev Library': check_spidev(),
        'Pillow Library': check_pillow(),
    }

    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)

    all_ok = True
    for component, status in results.items():
        status_str = "✓ OK" if status else "✗ FAILED"
        print(f"{component:20s} {status_str}")
        if not status:
            all_ok = False

    print("\n" + "="*50)

    if all_ok:
        print("✓ All checks passed!")
        print("\nYour system is ready. You can now run:")
        print("  python test_display.py")
        print("  python main.py")
    else:
        print("✗ Some checks failed")
        print("\nPlease fix the issues above before running the display test.")

    print("="*50 + "\n")

    return 0 if all_ok else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
