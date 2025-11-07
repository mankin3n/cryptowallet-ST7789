"""
UI Widgets and Components.

Reusable UI components for building pages: buttons, text, labels,
progress bars, sliders, spinners, and QR code displays.
"""

import logging
from typing import Optional
from PIL import Image, ImageDraw
import qrcode
import config
from ui.themes import Theme

logger = logging.getLogger(__name__)


def draw_text(
    draw: ImageDraw.Draw,
    text: str,
    position: tuple[int, int],
    font,
    color: tuple[int, int, int],
    align: str = 'left',
    max_width: Optional[int] = None
) -> int:
    """
    Draw text with optional word wrapping.

    Args:
        draw: ImageDraw object
        text: Text to draw
        position: (x, y) position
        font: Font object
        color: RGB color
        align: Text alignment ('left', 'center', 'right')
        max_width: Maximum width for wrapping

    Returns:
        Height of drawn text in pixels
    """
    x, y = position

    if not max_width:
        draw.text((x, y), text, font=font, fill=color)
        bbox = draw.textbbox((x, y), text, font=font)
        return bbox[3] - bbox[1]

    # Word wrapping
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    # Draw lines
    line_height = 18
    total_height = 0

    for i, line in enumerate(lines):
        line_y = y + (i * line_height)
        draw.text((x, line_y), line, font=font, fill=color)
        total_height += line_height

    return total_height


def draw_header(
    draw: ImageDraw.Draw,
    theme: Theme,
    title: str
) -> None:
    """
    Draw page header bar.

    Args:
        draw: ImageDraw object
        theme: Theme instance
        title: Header title text
    """
    # Draw header background
    draw.rectangle(
        [(0, 0), (config.DISPLAY_WIDTH, config.HEADER_HEIGHT)],
        fill=theme.get_color('DARK_GRAY'),
        outline=theme.get_color('LIGHT_GRAY')
    )

    # Draw title
    draw.text(
        (config.MARGIN_SIDE, config.MARGIN_TOP + 5),
        title,
        font=theme.get_font('header'),
        fill=theme.get_color('WHITE')
    )


def draw_status_bar(
    draw: ImageDraw.Draw,
    theme: Theme,
    battery: int = 100,
    time_str: str = "00:00",
    hint: str = ""
) -> None:
    """
    Draw status bar at bottom of screen.

    Args:
        draw: ImageDraw object
        theme: Theme instance
        battery: Battery percentage (0-100)
        time_str: Time string
        hint: Navigation hint text
    """
    y_start = config.DISPLAY_HEIGHT - config.STATUS_BAR_HEIGHT

    # Draw background
    draw.rectangle(
        [(0, y_start), (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)],
        fill=theme.get_color('DARK_GRAY'),
        outline=theme.get_color('LIGHT_GRAY')
    )

    # Battery indicator
    battery_text = f"🔋{battery}%"
    draw.text(
        (config.MARGIN_SIDE, y_start + 8),
        battery_text,
        font=theme.get_font('status'),
        fill=theme.get_color('WHITE')
    )

    # Time
    draw.text(
        (config.DISPLAY_WIDTH // 2 - 20, y_start + 8),
        time_str,
        font=theme.get_font('status'),
        fill=theme.get_color('WHITE')
    )

    # Hint text
    if hint:
        draw.text(
            (config.DISPLAY_WIDTH - 150, y_start + 8),
            hint,
            font=theme.get_font('hint'),
            fill=theme.get_color('GRAY')
        )


def draw_menu_item(
    draw: ImageDraw.Draw,
    theme: Theme,
    text: str,
    y: int,
    selected: bool = False,
    enabled: bool = True
) -> None:
    """
    Draw a menu item.

    Args:
        draw: ImageDraw object
        theme: Theme instance
        text: Menu item text
        y: Y position
        selected: Whether item is selected
        enabled: Whether item is enabled
    """
    item_height = 30
    x_start = config.MARGIN_SIDE
    width = config.DISPLAY_WIDTH - (2 * config.MARGIN_SIDE)

    # Draw selection highlight
    if selected:
        draw.rectangle(
            [(x_start, y), (x_start + width, y + item_height)],
            fill=theme.get_color('DARK_GREEN')
        )
        draw.text(
            (x_start + 5, y + 7),
            "▶",
            font=theme.get_font('menu'),
            fill=theme.get_color('GREEN')
        )

    # Draw text
    color = theme.get_color('WHITE') if enabled else theme.get_color('GRAY')
    draw.text(
        (x_start + 25, y + 7),
        text,
        font=theme.get_font('menu'),
        fill=color
    )


def draw_button(
    draw: ImageDraw.Draw,
    theme: Theme,
    text: str,
    position: tuple[int, int],
    selected: bool = False
) -> tuple[int, int, int, int]:
    """
    Draw a button.

    Args:
        draw: ImageDraw object
        theme: Theme instance
        text: Button text
        position: (x, y) position
        selected: Whether button is selected

    Returns:
        Button bounding box (x1, y1, x2, y2)
    """
    x, y = position
    padding = 10

    # Calculate size
    bbox = draw.textbbox((0, 0), text, font=theme.get_font('body'))
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    button_width = text_width + (2 * padding)
    button_height = text_height + (2 * padding)

    # Draw button background
    bg_color = theme.get_color('GREEN') if selected else theme.get_color('DARK_GRAY')
    draw.rectangle(
        [(x, y), (x + button_width, y + button_height)],
        fill=bg_color,
        outline=theme.get_color('LIGHT_GRAY')
    )

    # Draw text
    text_color = theme.get_color('BLACK') if selected else theme.get_color('WHITE')
    draw.text(
        (x + padding, y + padding),
        text,
        font=theme.get_font('body'),
        fill=text_color
    )

    return (x, y, x + button_width, y + button_height)


def draw_slider(
    draw: ImageDraw.Draw,
    theme: Theme,
    value: int,
    min_val: int,
    max_val: int,
    position: tuple[int, int],
    width: int = 200
) -> None:
    """
    Draw a slider widget.

    Args:
        draw: ImageDraw object
        theme: Theme instance
        value: Current value
        min_val: Minimum value
        max_val: Maximum value
        position: (x, y) position
        width: Slider width in pixels
    """
    x, y = position
    height = 20

    # Draw track
    draw.rectangle(
        [(x, y), (x + width, y + height)],
        fill=theme.get_color('DARK_GRAY'),
        outline=theme.get_color('LIGHT_GRAY')
    )

    # Calculate fill width
    percentage = (value - min_val) / (max_val - min_val)
    fill_width = int(width * percentage)

    # Draw fill
    draw.rectangle(
        [(x, y), (x + fill_width, y + height)],
        fill=theme.get_color('GREEN')
    )

    # Draw value text
    value_text = f"{value}"
    draw.text(
        (x + width + 10, y + 2),
        value_text,
        font=theme.get_font('body'),
        fill=theme.get_color('WHITE')
    )


def draw_progress_bar(
    draw: ImageDraw.Draw,
    theme: Theme,
    progress: float,
    position: tuple[int, int],
    width: int = 280
) -> None:
    """
    Draw a progress bar.

    Args:
        draw: ImageDraw object
        theme: Theme instance
        progress: Progress value (0.0 to 1.0)
        position: (x, y) position
        width: Bar width in pixels
    """
    x, y = position
    height = 20

    # Draw background
    draw.rectangle(
        [(x, y), (x + width, y + height)],
        fill=theme.get_color('DARK_GRAY'),
        outline=theme.get_color('LIGHT_GRAY')
    )

    # Draw progress
    fill_width = int(width * max(0.0, min(1.0, progress)))
    draw.rectangle(
        [(x, y), (x + fill_width, y + height)],
        fill=theme.get_color('CYAN')
    )

    # Draw percentage
    percent_text = f"{int(progress * 100)}%"
    draw.text(
        (x + width // 2 - 15, y + 2),
        percent_text,
        font=theme.get_font('body'),
        fill=theme.get_color('WHITE')
    )


def draw_spinner(
    draw: ImageDraw.Draw,
    theme: Theme,
    position: tuple[int, int],
    frame: int = 0
) -> None:
    """
    Draw an animated spinner.

    Args:
        draw: ImageDraw object
        theme: Theme instance
        position: (x, y) center position
        frame: Animation frame (0-7)
    """
    x, y = position
    radius = 20
    segments = 8

    for i in range(segments):
        angle = (i * 360 / segments) + (frame * 45)
        opacity = 255 - (i * 30)

        # Calculate segment position
        import math
        rad = math.radians(angle)
        seg_x = x + int(radius * math.cos(rad))
        seg_y = y + int(radius * math.sin(rad))

        # Draw segment
        color = (opacity, opacity, opacity)
        draw.ellipse(
            [(seg_x - 3, seg_y - 3), (seg_x + 3, seg_y + 3)],
            fill=color
        )


def create_qr_code(data: str, size: int = config.QR_MAX_SIZE) -> Image.Image:
    """
    Create QR code image.

    Args:
        data: Data to encode
        size: Desired QR code size in pixels

    Returns:
        PIL Image of QR code
    """
    try:
        qr = qrcode.QRCode(
            version=config.QR_VERSION,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=config.QR_BOX_SIZE,
            border=config.QR_BORDER,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Create image
        qr_image = qr.make_image(fill_color="black", back_color="white")

        # Resize to target size
        qr_image = qr_image.resize((size, size), Image.Resampling.NEAREST)

        return qr_image.convert('RGB')

    except Exception as e:
        logger.error(f"QR code generation failed: {e}")
        # Return placeholder
        placeholder = Image.new('RGB', (size, size), config.COLOR_RED)
        return placeholder
