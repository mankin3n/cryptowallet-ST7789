"""
UI Theme and Styling.

Defines color palettes, fonts, and visual styling for different UI themes.
Provides a flexible theming system to switch between visual styles.
"""

import logging
from typing import Optional, Dict
from abc import ABC, abstractmethod
from PIL import ImageFont
import config

logger = logging.getLogger(__name__)


class Theme(ABC):
    """Abstract base class for UI themes."""

    def __init__(self) -> None:
        """Initialize theme with colors and fonts."""
        self.colors: Dict[str, tuple[int, int, int]] = {}
        self.fonts: Dict[str, ImageFont.FreeTypeFont] = {}
        self._load_colors()
        self._load_fonts()
        logger.info(f"{self.__class__.__name__} initialized")

    @abstractmethod
    def _load_colors(self) -> None:
        """Load color palette for the theme."""
        pass

    @abstractmethod
    def _load_fonts(self) -> None:
        """Load fonts for the theme."""
        pass

    def get_color(self, name: str) -> tuple[int, int, int]:
        """Get color by name."""
        return self.colors.get(name, config.COLOR_WHITE)

    def get_font(self, size: str) -> ImageFont.FreeTypeFont:
        """Get font by size name."""
        return self.fonts.get(size, self.fonts.get('body'))


class HackerTheme(Theme):
    """The original hacker-style theme."""

    def _load_colors(self) -> None:
        """Load hacker color palette."""
        self.colors = {
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

    def _load_fonts(self) -> None:
        """Load monospaced fonts."""
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
            '/System/Library/Fonts/Monaco.dfont',
            '/Library/Fonts/Monaco.ttf',
        ]
        self._load_font_from_paths(font_paths, config.FONT_FAMILY)

    def _load_font_from_paths(self, font_paths: list[str], family: str) -> None:
        """Helper to load a font from a list of paths."""
        font_file = None
        for path in font_paths:
            try:
                with open(path, 'rb'):
                    font_file = path
                    break
            except FileNotFoundError:
                continue

        if not font_file:
            logger.warning(f"Could not find {family} font, using default")
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


class ModernTheme(Theme):
    """A cleaner, more modern theme."""

    def _load_colors(self) -> None:
        """Load modern color palette."""
        self.colors = {
            'BLACK': (20, 20, 20),
            'WHITE': (240, 240, 240),
            'PRIMARY': (0, 122, 255),
            'SECONDARY': (100, 100, 100),
            'SUCCESS': (40, 167, 69),
            'DANGER': (220, 53, 69),
            'WARNING': (255, 193, 7),
            'INFO': (23, 162, 184),
            'BACKGROUND': (30, 30, 30),
            'SURFACE': (45, 45, 45),
            'TEXT': (220, 220, 220),
            'MUTED': (150, 150, 150),
        }

    def _load_fonts(self) -> None:
        """Load sans-serif fonts."""
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/System/Library/Fonts/Helvetica.ttc',
            '/Library/Fonts/Arial.ttf',
        ]
        self._load_font_from_paths(font_paths, "sans-serif")

    def _load_font_from_paths(self, font_paths: list[str], family: str) -> None:
        """Helper to load a font from a list of paths."""
        font_file = None
        for path in font_paths:
            try:
                with open(path, 'rb'):
                    font_file = path
                    break
            except FileNotFoundError:
                continue

        if not font_file:
            logger.warning(f"Could not find {family} font, using default")
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
                'header': ImageFont.truetype(font_file, config.FONT_SIZE_HEADER + 2),
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


# Singleton instance
_theme: Optional[Theme] = None
_current_theme_name: str = 'modern'  # Default theme


def get_theme(theme_name: str = _current_theme_name) -> Theme:
    """
    Get singleton theme instance.

    Args:
        theme_name: 'modern' or 'hacker'

    Returns:
        Theme instance
    """
    global _theme, _current_theme_name
    if _theme is None or _current_theme_name != theme_name:
        if theme_name == 'modern':
            _theme = ModernTheme()
        elif theme_name == 'hacker':
            _theme = HackerTheme()
        else:
            logger.warning(f"Unknown theme '{theme_name}', falling back to ModernTheme")
            _theme = ModernTheme()
        _current_theme_name = theme_name
    return _theme


def set_theme(theme_name: str) -> None:
    """Set the global theme."""
    global _current_theme_name
    if theme_name in ['modern', 'hacker']:
        _current_theme_name = theme_name
        get_theme(theme_name)  # Force reload
        logger.info(f"Theme changed to {theme_name}")
    else:
        logger.error(f"Invalid theme name: {theme_name}")
