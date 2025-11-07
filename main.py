#!/usr/bin/env python3
"""
SeedSigner Mini - Hardware Security Device
Main Application Entry Point

Hardware security device for Raspberry Pi 4B with ST7789 320x240 display,
HW-504 joystick input, and camera module. Provides Bitcoin address generation,
transaction signing, QR code generation/scanning, and air-gapped wallet functionality.

Usage:
    python main.py                  # Run on Raspberry Pi with hardware
    MOCK_HARDWARE=True python main.py  # Run without hardware (testing)
"""

import logging
import time
import sys
import signal
from typing import Optional
import config

# Setup logging first
from utils.logger import setup_logging
setup_logging()

logger = logging.getLogger(__name__)

# Import hardware managers
from hardware.gpio_manager import get_gpio_manager
from hardware.display import get_display
from hardware.joystick import get_joystick
from hardware.camera import get_camera

# Import UI system
from ui.themes import get_theme
from ui.screen_manager import get_screen_manager
from ui.menu_system import get_menu_system
from ui.pages import render_page

# Import crypto
from crypto.bitcoin import get_wallet
from crypto.signing import get_signer


class Application:
    """
    Main application controller.

    Attributes:
        running: Whether application is running
        gpio: GPIO manager
        display: Display controller
        joystick: Joystick controller
        camera: Camera controller
        screen_manager: Screen rendering manager
        menu_system: Menu and navigation system
        theme: UI theme
        wallet: Bitcoin wallet
        signer: Cryptographic signer
    """

    def __init__(self) -> None:
        """Initialize application."""
        logger.info("=" * 60)
        logger.info("SeedSigner Mini - Hardware Security Device")
        logger.info("=" * 60)

        self.running: bool = False

        # Hardware
        self.gpio = get_gpio_manager()
        self.display = get_display()
        self.joystick = get_joystick()
        self.camera = get_camera()

        # UI
        self.screen_manager = get_screen_manager()
        self.menu_system = get_menu_system()
        self.theme = get_theme()

        # Crypto
        self.wallet = get_wallet()
        self.signer = get_signer()

        # Timing
        self.splash_start_time: Optional[float] = None

        logger.info("Application initialized")

    def setup(self) -> bool:
        """
        Setup all hardware and subsystems.

        Returns:
            True if setup successful, False otherwise
        """
        logger.info("Setting up hardware...")

        try:
            # Setup GPIO
            if not self.gpio.setup():
                logger.error("GPIO setup failed")
                return False

            # Setup display
            if not self.display.setup():
                logger.error("Display setup failed")
                return False

            # Setup camera
            if not self.camera.setup():
                logger.warning("Camera setup failed (continuing without camera)")

            # Start joystick polling
            self.joystick.start()

            # Start camera capture
            self.camera.start_capture()

            # Initialize Bitcoin wallet with test key
            self._initialize_wallet()

            logger.info("Hardware setup complete")
            return True

        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False

    def _initialize_wallet(self) -> None:
        """Initialize Bitcoin wallet with sample data."""
        try:
            # Generate or load private key
            private_key = self.wallet.generate_private_key()

            # Get addresses
            addresses = self.wallet.get_all_addresses()

            # Store in menu state
            self.menu_system.state.bitcoin_address = addresses.get('native_segwit', '')
            self.menu_system.state.bitcoin_address_type = 'native_segwit'

            logger.info("Wallet initialized")
            logger.debug(f"Address: {self.menu_system.state.bitcoin_address}")

        except Exception as e:
            logger.error(f"Wallet initialization failed: {e}")

    def run(self) -> None:
        """Main application event loop."""
        self.running = True
        self.splash_start_time = time.time()

        logger.info("Entering main event loop")

        try:
            while self.running:
                # Handle splash screen auto-transition
                if self.menu_system.state.current_page == config.PAGE_SPLASH:
                    if self.splash_start_time and \
                       (time.time() - self.splash_start_time) >= config.SPLASH_DURATION:
                        self.menu_system.state.navigate_to(config.PAGE_HOME, push_to_stack=False)
                        logger.info("Splash screen completed, showing home")

                # Process joystick input
                event = self.joystick.get_event()
                if event:
                    logger.debug(f"Input event: {event.direction}")
                    self.menu_system.handle_input(event.direction)

                # Render current page
                current_page = self.menu_system.state.current_page
                canvas = render_page(current_page, self.menu_system.state, self.theme)

                # Display on screen
                self.screen_manager.render_canvas(canvas)

                # Apply brightness setting
                if hasattr(self.menu_system.state, 'brightness'):
                    self.gpio.set_brightness(self.menu_system.state.brightness)

                # Small delay to prevent excessive CPU usage
                time.sleep(0.01)

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")

        except Exception as e:
            logger.error(f"Runtime error: {e}", exc_info=True)

        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """Cleanup all resources."""
        logger.info("Cleaning up...")

        try:
            # Stop joystick
            self.joystick.stop()

            # Stop camera
            self.camera.cleanup()

            # Clear display
            self.display.cleanup()

            # Cleanup GPIO
            self.gpio.cleanup()

            logger.info("Cleanup complete")

        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    def handle_signal(self, signum, frame) -> None:
        """
        Handle system signals.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Signal {signum} received, shutting down...")
        self.running = False


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        # Create application
        app = Application()

        # Setup signal handlers
        signal.signal(signal.SIGINT, app.handle_signal)
        signal.signal(signal.SIGTERM, app.handle_signal)

        # Setup hardware
        if not app.setup():
            logger.error("Application setup failed")
            return 1

        # Run application
        app.run()

        return 0

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
