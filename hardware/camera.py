"""
Raspberry Pi Camera Module Controller.

Handles camera initialization, frame capture, and QR code detection.
Provides non-blocking frame capture via background thread.
"""

import logging
import threading
import time
from queue import Queue
from typing import Optional
from PIL import Image
import config

# Try to import camera library
_CAMERA_MOCK_MODE = config.MOCK_HARDWARE
if not config.MOCK_HARDWARE:
    try:
        from picamera2 import Picamera2
    except ImportError:
        logging.warning("picamera2 not available, using mock camera")
        _CAMERA_MOCK_MODE = True

logger = logging.getLogger(__name__)


class Camera:
    """
    Raspberry Pi camera controller.

    Attributes:
        camera: Picamera2 instance
        frame_queue: Queue of captured frames
        running: Whether capture thread is running
        capture_thread: Background thread for frame capture
    """

    def __init__(self) -> None:
        """Initialize camera controller."""
        self.camera: Optional[any] = None
        self.frame_queue: Queue[Image.Image] = Queue(maxsize=config.CAMERA_BUFFER_SIZE)
        self.running: bool = False
        self.capture_thread: Optional[threading.Thread] = None

        logger.info(f"Camera controller created (mock={_CAMERA_MOCK_MODE})")

    def setup(self) -> bool:
        """
        Initialize camera hardware.

        Returns:
            True if initialization successful, False otherwise
        """
        if _CAMERA_MOCK_MODE:
            logger.info("Mock mode: Camera setup skipped")
            return True

        try:
            self.camera = Picamera2()

            # Configure camera for preview
            camera_config = self.camera.create_preview_configuration(
                main={"size": config.CAMERA_RESOLUTION, "format": config.CAMERA_FORMAT}
            )
            self.camera.configure(camera_config)

            # Start camera
            self.camera.start()
            time.sleep(0.5)  # Allow camera to warm up

            logger.info(f"Camera initialized: {config.CAMERA_RESOLUTION} @ {config.CAMERA_FPS}fps")
            return True

        except Exception as e:
            logger.error(f"Camera initialization failed: {e}")
            return False

    def start_capture(self) -> None:
        """Start background frame capture thread."""
        if self.running:
            logger.warning("Camera capture already running")
            return

        if _CAMERA_MOCK_MODE:
            logger.info("Mock mode: Camera capture simulated")
            self.running = True
            self.capture_thread = threading.Thread(target=self._mock_capture_loop, daemon=True)
            self.capture_thread.start()
            return

        if not self.camera:
            logger.error("Camera not initialized")
            return

        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        logger.info("Camera capture started")

    def stop_capture(self) -> None:
        """Stop background frame capture thread."""
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=1.0)
        logger.info("Camera capture stopped")

    def _capture_loop(self) -> None:
        """Main capture loop (runs in background thread)."""
        frame_interval = 1.0 / config.CAMERA_FPS

        while self.running:
            try:
                # Capture frame as numpy array
                frame_array = self.camera.capture_array()

                # Convert to PIL Image
                frame = Image.fromarray(frame_array)

                # Ensure correct size
                if frame.size != config.CAMERA_RESOLUTION:
                    frame = frame.resize(config.CAMERA_RESOLUTION, Image.Resampling.LANCZOS)

                # Add to queue (discard oldest if full)
                if self.frame_queue.full():
                    try:
                        self.frame_queue.get_nowait()
                    except:
                        pass

                self.frame_queue.put(frame)

                time.sleep(frame_interval)

            except Exception as e:
                logger.error(f"Frame capture error: {e}")
                time.sleep(frame_interval)

    def _mock_capture_loop(self) -> None:
        """Mock capture loop for testing without hardware."""
        frame_interval = 1.0 / config.CAMERA_FPS

        while self.running:
            try:
                # Create mock frame (gradient pattern)
                frame = Image.new('RGB', config.CAMERA_RESOLUTION, config.COLOR_DARK_GRAY)

                # Add to queue
                if self.frame_queue.full():
                    try:
                        self.frame_queue.get_nowait()
                    except:
                        pass

                self.frame_queue.put(frame)
                time.sleep(frame_interval)

            except Exception as e:
                logger.error(f"Mock capture error: {e}")
                time.sleep(frame_interval)

    def get_frame(self) -> Optional[Image.Image]:
        """
        Get latest captured frame.

        Returns:
            PIL Image or None if no frame available
        """
        if not self.frame_queue.empty():
            return self.frame_queue.get()
        return None

    def capture_single_frame(self) -> Optional[Image.Image]:
        """
        Capture a single frame immediately.

        Returns:
            PIL Image or None if capture failed
        """
        if _CAMERA_MOCK_MODE:
            # Return mock frame
            return Image.new('RGB', config.CAMERA_RESOLUTION, config.COLOR_DARK_GRAY)

        if not self.camera:
            logger.error("Camera not initialized")
            return None

        try:
            frame_array = self.camera.capture_array()
            frame = Image.fromarray(frame_array)

            if frame.size != config.CAMERA_RESOLUTION:
                frame = frame.resize(config.CAMERA_RESOLUTION, Image.Resampling.LANCZOS)

            return frame

        except Exception as e:
            logger.error(f"Single frame capture failed: {e}")
            return None

    def cleanup(self) -> None:
        """Cleanup camera resources."""
        self.stop_capture()

        if _CAMERA_MOCK_MODE:
            logger.info("Mock mode: Camera cleanup skipped")
            return

        try:
            if self.camera:
                self.camera.stop()
                self.camera.close()
            logger.info("Camera cleanup complete")

        except Exception as e:
            logger.error(f"Camera cleanup failed: {e}")


# Singleton instance
_camera: Optional[Camera] = None


def get_camera() -> Camera:
    """
    Get singleton camera instance.

    Returns:
        Camera instance
    """
    global _camera
    if _camera is None:
        _camera = Camera()
    return _camera
