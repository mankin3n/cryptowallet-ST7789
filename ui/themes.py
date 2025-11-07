"""
UI Theme and Styling.

Defines color palette, fonts, and visual styling constants for the UI.
Provides theme class for consistent visual design across all pages.
"""

import logging
from typing import Optional, Dict
from PIL import ImageFont
import config

logger = logging.getLogger(__name__)


class Theme:
    """
    UI theme with colors and fonts.

    Attributes:
        colors: Dictionary of color names to RGB tuples
        fonts: Dictionary of loaded fonts
    """

    def __init__(self) -> None:
        """Initialize theme with colors and fonts."""
        # Color palette
        self.colors: Dict[str, tuple[int, int, int]] = {
            'BLACK': config.COLOR_BLACK,
            'WHITE': config.COLOR_WHITE,
            'GREEN': config.COLOR_GREEN,
            'DARK_GREEN': config.COLOR_DARK_GREEN,
            'RED': config.COLOR_RED,
            'ORANGE': config.COLOR_ORANGE,
            'CYAN': config.COLOR_CYAN,
            'YELLOW': config.COLOR_YELLOW,
            'GRAY': config.COLOR_GRAY,
            'DARK_GRAY': config.COLOR_DARK_GRAY,
            'LIGHT_GRAY': config.COLOR_LIGHT_GRAY,
        }

        # Load fonts
        self.fonts: Dict[str, ImageFont.FreeTypeFont] = {}
        self._load_fonts()

        logger.info("Theme initialized")

    def _load_fonts(self) -> None:
        """Load TrueType fonts from system."""
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',
            '/System/Library/Fonts/Monaco.dfont',  # macOS fallback
            '/Library/Fonts/Monaco.ttf',  # macOS fallback
        ]

        # Try to find font file
        font_file = None
        for path in font_paths:
            try:
                # Test if file exists by trying to open it
                with open(path, 'rb'):
                    font_file = path
                    break
            except FileNotFoundError:
                continue

        if not font_file:
            logger.warning("Could not find TrueType font, using default")
            # Use default PIL font
            self.fonts = {
                'header': ImageFont.load_default(),
                'menu': ImageFont.load_default(),
                'body': ImageFont.load_default(),
                'status': ImageFont.load_default(),
                'hint': ImageFont.load_default(),
            }
            return

        try:
            self.fonts = {
                'header': ImageFont.truetype(font_file, config.FONT_SIZE_HEADER),
                'menu': ImageFont.truetype(font_file, config.FONT_SIZE_MENU),
                'body': ImageFont.truetype(font_file, config.FONT_SIZE_BODY),
                'status': ImageFont.truetype(font_file, config.FONT_SIZE_STATUS),
                'hint': ImageFont.truetype(font_file, config.FONT_SIZE_HINT),
            }
            logger.info(f"Fonts loaded from {font_file}")

        except Exception as e:
            logger.error(f"Font loading failed: {e}, using default")
            self.fonts = {
                'header': ImageFont.load_default(),
                'menu': ImageFont.load_default(),
                'body': ImageFont.load_default(),
                'status': ImageFont.load_default(),
                'hint': ImageFont.load_default(),
            }

    def get_color(self, name: str) -> tuple[int, int, int]:
        """
        Get color by name.

        Args:
            name: Color name (e.g., 'WHITE', 'GREEN')

        Returns:
            RGB tuple
        """
        return self.colors.get(name, self.colors['WHITE'])

    def get_font(self, size: str) -> ImageFont.FreeTypeFont:
        """
        Get font by size name.

        Args:
            size: Font size name ('header', 'menu', 'body', 'status', 'hint')

        Returns:
            ImageFont object
        """
        return self.fonts.get(size, self.fonts['body'])


# Singleton instance
_theme: Optional[Theme] = None


def get_theme() -> Theme:
    """
    Get singleton theme instance.

    Returns:
        Theme instance
    """
    global _theme
    if _theme is None:
        _theme = Theme()
    return _theme
