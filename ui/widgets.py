"""
UI Widgets and Components.

Reusable UI components for building pages: buttons, text, labels,
progress bars, sliders, spinners, and QR code displays.
"""

import logging
from typing import Optional
from PIL import Image, ImageDraw
import qrcode
import math
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
    Draw a modern page header bar.

    Args:
        draw: ImageDraw object
        theme: Theme instance
        title: Header title text
    """
    # Draw header background
    draw.rectangle(
        [(0, 0), (config.DISPLAY_WIDTH, config.HEADER_HEIGHT)],
        fill=theme.get_color('SURFACE'),
    )

    # Draw title
    font_header = theme.get_font('header')
    bbox = draw.textbbox((0, 0), title, font=font_header)
    text_width = bbox[2] - bbox[0]
    draw.text(
        ((config.DISPLAY_WIDTH - text_width) / 2, (config.HEADER_HEIGHT - 20) / 2),
        title,
        font=font_header,
        fill=theme.get_color('TEXT')
    )

    # Draw bottom border
    draw.line(
        [(0, config.HEADER_HEIGHT - 1), (config.DISPLAY_WIDTH, config.HEADER_HEIGHT - 1)],
        fill=theme.get_color('SECONDARY')
    )


def draw_status_bar(
    draw: ImageDraw.Draw,
    theme: Theme,
    battery: int = 100,
    time_str: str = "00:00",
    hint: str = ""
) -> None:
    """
    Draw a modern status bar at the bottom of the screen.

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
        fill=theme.get_color('SURFACE'),
    )

    # Draw top border
    draw.line(
        [(0, y_start), (config.DISPLAY_WIDTH, y_start)],
        fill=theme.get_color('SECONDARY')
    )

    y_text = y_start + (config.STATUS_BAR_HEIGHT - 12) / 2

    # Battery indicator
    battery_text = f"BAT: {battery}%"
    draw.text(
        (config.MARGIN_SIDE, y_text),
        battery_text,
        font=theme.get_font('status'),
        fill=theme.get_color('MUTED')
    )

    # Time
    font_status = theme.get_font('status')
    bbox = draw.textbbox((0, 0), time_str, font=font_status)
    text_width = bbox[2] - bbox[0]
    draw.text(
        ((config.DISPLAY_WIDTH - text_width) / 2, y_text),
        time_str,
        font=font_status,
        fill=theme.get_color('MUTED')
    )

    # Hint text
    if hint:
        font_hint = theme.get_font('hint')
        bbox = draw.textbbox((0, 0), hint, font=font_hint)
        text_width = bbox[2] - bbox[0]
        draw.text(
            (config.DISPLAY_WIDTH - config.MARGIN_SIDE - text_width, y_text),
            hint,
            font=font_hint,
            fill=theme.get_color('MUTED')
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
    width: int = 0,
    height: int = 0,
    selected: bool = False
) -> tuple[int, int, int, int]:
    """
    Draw a modern button.

    Args:
        draw: ImageDraw object
        theme: Theme instance
        text: Button text
        position: (x, y) position
        width: Button width
        height: Button height
        selected: Whether button is selected

    Returns:
        Button bounding box (x1, y1, x2, y2)
    """
    x, y = position
    padding = 10

    # Calculate size if not provided
    if not width or not height:
        bbox = draw.textbbox((0, 0), text, font=theme.get_font('body'))
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        width = text_width + (2 * padding)
        height = text_height + (2 * padding)

    # Draw button background
    bg_color = theme.get_color('PRIMARY') if selected else theme.get_color('SURFACE')
    draw.rectangle(
        [(x, y), (x + width, y + height)],
        fill=bg_color,
        outline=theme.get_color('SECONDARY')
    )

    # Draw text
    font_body = theme.get_font('body')
    bbox = draw.textbbox((0, 0), text, font=font_body)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = x + (width - text_width) / 2
    text_y = y + (height - text_height) / 2
    text_color = theme.get_color('WHITE') if selected else theme.get_color('TEXT')
    draw.text(
        (text_x, text_y),
        text,
        font=font_body,
        fill=text_color
    )

    return (x, y, x + width, y + height)


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
    Draw a modern slider widget.

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
    height = 10
    handle_radius = 8

    # Draw track
    draw.rectangle(
        [(x, y + height / 2 - 2), (x + width, y + height / 2 + 2)],
        fill=theme.get_color('SECONDARY')
    )

    # Calculate handle position
    percentage = (value - min_val) / (max_val - min_val)
    handle_x = x + int(width * percentage)

    # Draw fill
    draw.rectangle(
        [(x, y + height / 2 - 2), (handle_x, y + height / 2 + 2)],
        fill=theme.get_color('PRIMARY')
    )

    # Draw handle
    draw.ellipse(
        [(handle_x - handle_radius, y + height / 2 - handle_radius), (handle_x + handle_radius, y + height / 2 + handle_radius)],
        fill=theme.get_color('PRIMARY'),
        outline=theme.get_color('WHITE')
    )


def draw_progress_bar(
    draw: ImageDraw.Draw,
    theme: Theme,
    progress: float,
    position: tuple[int, int],
    width: int = 280
) -> None:
    """
    Draw a modern progress bar.

    Args:
        draw: ImageDraw object
        theme: Theme instance
        progress: Progress value (0.0 to 1.0)
        position: (x, y) position
        width: Bar width in pixels
    """
    x, y = position
    height = 10

    # Draw background
    draw.rectangle(
        [(x, y), (x + width, y + height)],
        fill=theme.get_color('SECONDARY'),
        outline=theme.get_color('SECONDARY')
    )

    # Draw progress
    fill_width = int(width * max(0.0, min(1.0, progress)))
    draw.rectangle(
        [(x, y), (x + fill_width, y + height)],
        fill=theme.get_color('PRIMARY')
    )

    # Draw percentage
    percent_text = f"{int(progress * 100)}%"
    font_hint = theme.get_font('hint')
    bbox = draw.textbbox((0, 0), percent_text, font=font_hint)
    text_width = bbox[2] - bbox[0]
    draw.text(
        (x + width + 10, y),
        percent_text,
        font=font_hint,
        fill=theme.get_color('MUTED')
    )


def draw_spinner(
    draw: ImageDraw.Draw,
    theme: Theme,
    position: tuple[int, int],
    radius: int = 10,
    frame: int = 0
) -> None:
    """
    Draw a modern animated spinner.

    Args:
        draw: ImageDraw object
        theme: Theme instance
        position: (x, y) center position
        radius: Spinner radius
        frame: Animation frame
    """
    x, y = position
    segments = 12

    for i in range(segments):
        angle = (i * 360 / segments) + (frame * 30)
        rad = math.radians(angle)
        
        # Calculate opacity
        opacity = int(255 * (1 - (i / segments)))
        color = theme.get_color('PRIMARY')
        
        # Create a new color with opacity
        final_color = (color[0], color[1], color[2], opacity)

        # Draw segment
        seg_x = x + int(radius * math.cos(rad))
        seg_y = y + int(radius * math.sin(rad))
        
        # Use a small rectangle for each segment to simulate thickness
        draw.rectangle(
            [(seg_x - 1, seg_y - 3), (seg_x + 1, seg_y + 3)],
            fill=final_color
        )


def create_qr_code(
    data: str,
    size: int = config.QR_MAX_SIZE,
    fill_color: str = "black",
    back_color: str = "white"
) -> Image.Image:
    """
    Create QR code image.

    Args:
        data: Data to encode
        size: Desired QR code size in pixels
        fill_color: QR code color
        back_color: Background color

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
        qr_image = qr.make_image(fill_color=fill_color, back_color=back_color)

        # Resize to target size
        qr_image = qr_image.resize((size, size), Image.Resampling.NEAREST)

        return qr_image.convert('RGB')

    except Exception as e:
        logger.error(f"QR code generation failed: {e}")
        # Return placeholder
        placeholder = Image.new('RGB', (size, size), config.COLOR_RED)
        return placeholder
