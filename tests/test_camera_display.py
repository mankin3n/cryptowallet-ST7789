#!/usr/bin/env python3
"""
Camera Display Test - Live Camera Feed on ST7789 Display

Tests the camera and display by showing live camera feed on screen.
Useful for verifying camera is working and properly focused.

Usage:
    python tests/test_camera_display.py

Controls:
    Q: Quit test

Hardware Required:
    - ST7789 Display (320x240)
    - Raspberry Pi Camera Module v2 or v3
"""

import sys
import os
import time
import logging
import signal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from hardware.display import get_display
from hardware.camera import get_camera
from hardware.cli_input import get_cli_input
from PIL import Image, ImageDraw, ImageFont

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CameraDisplayTest:
    """
    Camera display test application.

    Shows live camera feed on ST7789 display with FPS counter.
    """

    def __init__(self):
        """Initialize test."""
        self.running = False
        self.display = get_display()
        self.camera = get_camera()
        self.cli_input = get_cli_input()
        self.frame_count = 0
        self.start_time = 0

        logger.info("=" * 60)
        logger.info("Camera Display Test")
        logger.info("=" * 60)

    def setup(self) -> bool:
        """
        Setup hardware.

        Returns:
            True if setup successful
        """
        logger.info("Setting up hardware...")

        # Setup display
        if not self.display.setup():
            logger.error("Display setup failed")
            return False

        logger.info("✓ Display initialized")

        # Setup camera
        if not self.camera.setup():
            logger.error("Camera setup failed")
            return False

        logger.info("✓ Camera initialized")

        # Start camera capture
        try:
            self.camera.start_capture()
            logger.info("✓ Camera capture started")
        except Exception as e:
            logger.error(f"Camera capture failed: {e}")
            return False

        # Start CLI input for quit command
        try:
            self.cli_input.start(callback=self._handle_input)
            logger.info("✓ CLI input enabled (Press Q to quit)")
        except Exception as e:
            logger.warning(f"CLI input not available: {e}")

        logger.info("Hardware setup complete!")
        logger.info("")
        logger.info("=" * 60)
        logger.info("Camera feed should now appear on display")
        logger.info("Press Q to quit")
        logger.info("=" * 60)

        return True

    def _handle_input(self, direction: str):
        """
        Handle CLI input.

        Args:
            direction: Input direction (not used, only Q is handled in cli_input)
        """
        # Q is handled directly in cli_input by sending SIGINT
        pass

    def run(self):
        """Main test loop."""
        self.running = True
        self.start_time = time.time()
        self.frame_count = 0

        logger.info("Starting camera display loop...")

        try:
            while self.running:
                # Get camera frame
                frame = self.camera.get_frame()

                if frame is not None:
                    # Resize to display size if needed
                    if frame.size != (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT):
                        frame = frame.resize(
                            (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT),
                            Image.Resampling.LANCZOS
                        )

                    # Add FPS overlay
                    frame = self._add_overlay(frame)

                    # Display frame
                    self.display.show_image(frame)

                    self.frame_count += 1
                else:
                    # No frame available, show waiting message
                    self._show_waiting()

                # Small delay to prevent excessive CPU usage
                time.sleep(0.03)  # ~30 FPS

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")

        except Exception as e:
            logger.error(f"Error in display loop: {e}", exc_info=True)

        finally:
            self.cleanup()

    def _add_overlay(self, frame: Image.Image) -> Image.Image:
        """
        Add FPS and info overlay to frame.

        Args:
            frame: Camera frame

        Returns:
            Frame with overlay
        """
        # Create drawing context
        draw = ImageDraw.Draw(frame)

        # Calculate FPS
        elapsed = time.time() - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0

        # Load font (use default if DejaVu not available)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            font = ImageFont.load_default()

        # Draw semi-transparent background for text
        overlay_height = 25
        overlay = Image.new('RGBA', (config.DISPLAY_WIDTH, overlay_height), (0, 0, 0, 180))
        frame.paste(overlay, (0, 0), overlay)

        # Draw FPS counter
        fps_text = f"FPS: {fps:.1f}"
        draw.text((5, 5), fps_text, fill=(0, 255, 0), font=font)

        # Draw frame counter
        frame_text = f"Frames: {self.frame_count}"
        draw.text((100, 5), frame_text, fill=(255, 255, 255), font=font)

        # Draw quit hint
        quit_text = "Q: Quit"
        draw.text((config.DISPLAY_WIDTH - 60, 5), quit_text, fill=(255, 165, 0), font=font)

        return frame

    def _show_waiting(self):
        """Show waiting for camera message."""
        # Create blank frame
        frame = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), (30, 30, 30))
        draw = ImageDraw.Draw(frame)

        # Load font
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Draw message
        msg1 = "Waiting for camera..."
        msg2 = "Check camera connection"

        # Center text
        bbox1 = draw.textbbox((0, 0), msg1, font=font_large)
        text_width1 = bbox1[2] - bbox1[0]

        bbox2 = draw.textbbox((0, 0), msg2, font=font_small)
        text_width2 = bbox2[2] - bbox2[0]

        x1 = (config.DISPLAY_WIDTH - text_width1) // 2
        y1 = config.DISPLAY_HEIGHT // 2 - 20

        x2 = (config.DISPLAY_WIDTH - text_width2) // 2
        y2 = config.DISPLAY_HEIGHT // 2 + 10

        draw.text((x1, y1), msg1, fill=(255, 165, 0), font=font_large)
        draw.text((x2, y2), msg2, fill=(150, 150, 150), font=font_small)

        self.display.show_image(frame)

    def cleanup(self):
        """Cleanup resources."""
        logger.info("")
        logger.info("Cleaning up...")

        try:
            self.cli_input.stop()
            self.camera.cleanup()
            self.display.cleanup()

            # Show summary
            elapsed = time.time() - self.start_time
            avg_fps = self.frame_count / elapsed if elapsed > 0 else 0

            logger.info("=" * 60)
            logger.info("Test Summary:")
            logger.info(f"  Total frames: {self.frame_count}")
            logger.info(f"  Duration: {elapsed:.1f}s")
            logger.info(f"  Average FPS: {avg_fps:.1f}")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    def handle_signal(self, signum, frame):
        """Handle system signals."""
        logger.info(f"Signal {signum} received, stopping test...")
        self.running = False


def main():
    """Main entry point."""
    test = CameraDisplayTest()

    # Setup signal handlers
    signal.signal(signal.SIGINT, test.handle_signal)
    signal.signal(signal.SIGTERM, test.handle_signal)

    # Setup hardware
    if not test.setup():
        logger.error("Hardware setup failed!")
        logger.error("Make sure camera and display are connected.")
        return 1

    # Run test
    test.run()

    return 0


if __name__ == '__main__':
    sys.exit(main())
