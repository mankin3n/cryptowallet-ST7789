"""
Screen Manager for UI Rendering.

Manages canvas creation, double buffering, and display updates.
Handles FPS limiting and provides high-level rendering interface.
"""

import logging
from typing import Optional
from PIL import Image, ImageDraw
import config
from hardware.display import get_display
from ui.themes import get_theme, Theme

logger = logging.getLogger(__name__)


class ScreenManager:
    """
    Manages screen rendering and display updates.

    Attributes:
        display: Display hardware instance
        theme: UI theme instance
        current_canvas: Current frame buffer
    """

    def __init__(self) -> None:
        """Initialize screen manager."""
        self.display = get_display()
        self.theme: Theme = get_theme()
        self.current_canvas: Optional[Image.Image] = None

        logger.info("Screen manager created")

    def create_canvas(self, background: tuple[int, int, int] = None) -> tuple[Image.Image, ImageDraw.Draw]:
        """
        Create a new canvas for rendering.

        Args:
            background: Background color (default: black)

        Returns:
            Tuple of (Image, ImageDraw)
        """
        if background is None:
            background = self.theme.get_color('BLACK')

        canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), background)
        draw = ImageDraw.Draw(canvas)

        return canvas, draw

    def render_canvas(self, canvas: Image.Image) -> None:
        """
        Render canvas to physical display.

        Args:
            canvas: PIL Image to display
        """
        self.current_canvas = canvas
        self.display.show_image(canvas)

    def clear_screen(self, color: tuple[int, int, int] = None) -> None:
        """
        Clear screen to solid color.

        Args:
            color: RGB color (default: black)
        """
        if color is None:
            color = self.theme.get_color('BLACK')

        self.display.clear(color)


# Singleton instance
_screen_manager: Optional[ScreenManager] = None


def get_screen_manager() -> ScreenManager:
    """
    Get singleton screen manager instance.

    Returns:
        ScreenManager instance
    """
    global _screen_manager
    if _screen_manager is None:
        _screen_manager = ScreenManager()
    return _screen_manager
