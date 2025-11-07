"""
Page Renderers for All UI Pages.

Contains rendering functions for all 11 pages in the UI architecture.
Each function takes PageState and Theme, returns PIL Image.
"""

import logging
import time
from datetime import datetime
from PIL import Image
import config
from ui.themes import Theme
from ui.menu_system import PageState
from ui.widgets import (
    draw_text, draw_header, draw_status_bar, draw_menu_item,
    draw_button, draw_slider, draw_progress_bar, draw_spinner,
    create_qr_code
)

logger = logging.getLogger(__name__)


def render_splash_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render splash screen with logo and loading animation.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BLACK'))
    draw = canvas._getdraw()

    # Draw title
    title = "🔐 SeedSigner Mini"
    bbox = draw.textbbox((0, 0), title, font=theme.get_font('header'))
    title_width = bbox[2] - bbox[0]
    draw.text(
        ((config.DISPLAY_WIDTH - title_width) // 2, 80),
        title,
        font=theme.get_font('header'),
        fill=theme.get_color('WHITE')
    )

    # Draw subtitle
    subtitle = "Initializing..."
    bbox = draw.textbbox((0, 0), subtitle, font=theme.get_font('body'))
    subtitle_width = bbox[2] - bbox[0]
    draw.text(
        ((config.DISPLAY_WIDTH - subtitle_width) // 2, 120),
        subtitle,
        font=theme.get_font('body'),
        fill=theme.get_color('GRAY')
    )

    # Draw spinner
    state.update_spinner()
    draw_spinner(draw, theme, (config.DISPLAY_WIDTH // 2, 160), state.spinner_frame)

    return canvas


def render_home_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render main menu page.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BLACK'))
    draw = canvas._getdraw()

    # Header
    draw_header(draw, theme, "🏠 MAIN MENU")

    # Menu items
    menu_items = [
        "Verify Signature",
        "Generate QR Code",
        "View Address",
        "Settings",
        "About"
    ]

    y_start = config.HEADER_HEIGHT + 20
    item_spacing = 30

    for i, item in enumerate(menu_items):
        draw_menu_item(
            draw, theme, item,
            y_start + (i * item_spacing),
            selected=(i == state.menu_index)
        )

    # Status bar
    draw_status_bar(draw, theme, hint="▲▼ Select ✓ Enter")

    return canvas


def render_verify_signature_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render signature verification page.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BLACK'))
    draw = canvas._getdraw()

    # Header
    draw_header(draw, theme, "✓ VERIFY SIGNATURE")

    # Content area
    y = config.HEADER_HEIGHT + 10

    # Status
    status_text = "Valid" if state.signature_valid else "Invalid"
    status_color = theme.get_color('GREEN') if state.signature_valid else theme.get_color('RED')

    draw.text((config.MARGIN_SIDE, y), "Status:", font=theme.get_font('body'), fill=theme.get_color('WHITE'))
    draw.text((config.MARGIN_SIDE + 80, y), status_text, font=theme.get_font('body'), fill=status_color)
    y += 25

    # Signature data
    if state.signature_data:
        draw.text((config.MARGIN_SIDE, y), "Signature:", font=theme.get_font('body'), fill=theme.get_color('WHITE'))
        y += 20
        sig_short = state.signature_data[:32] + "..." if len(state.signature_data) > 32 else state.signature_data
        draw.text((config.MARGIN_SIDE, y), sig_short, font=theme.get_font('hint'), fill=theme.get_color('GRAY'))
        y += 25
    else:
        draw.text((config.MARGIN_SIDE, y), "No signature loaded", font=theme.get_font('body'), fill=theme.get_color('GRAY'))

    # Status bar
    draw_status_bar(draw, theme, hint="◀ Back")

    return canvas


def render_generate_qr_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render QR code generation page.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BLACK'))
    draw = canvas._getdraw()

    # Header
    draw_header(draw, theme, "📱 QR CODE")

    # Generate QR code
    qr_data = state.qr_data if state.qr_data else "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
    qr_size = int(config.QR_MAX_SIZE * (state.qr_zoom / 100.0))
    qr_size = max(80, min(160, qr_size))

    qr_image = create_qr_code(qr_data, qr_size)

    # Center QR code
    qr_x = (config.DISPLAY_WIDTH - qr_size) // 2
    qr_y = config.HEADER_HEIGHT + ((config.CONTENT_HEIGHT - qr_size) // 2)

    canvas.paste(qr_image, (qr_x, qr_y))

    # Zoom indicator
    zoom_text = f"Zoom: {state.qr_zoom}%"
    draw.text(
        (config.DISPLAY_WIDTH - 100, config.HEADER_HEIGHT + 10),
        zoom_text,
        font=theme.get_font('hint'),
        fill=theme.get_color('GRAY')
    )

    # Status bar
    draw_status_bar(draw, theme, hint="◀ Back ▲▼ Zoom")

    return canvas


def render_view_address_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render Bitcoin address view page.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BLACK'))
    draw = canvas._getdraw()

    # Header
    draw_header(draw, theme, "📍 BITCOIN ADDRESS")

    y = config.HEADER_HEIGHT + 10

    # Address type
    addr_type_display = state.bitcoin_address_type.replace('_', ' ').title()
    draw.text((config.MARGIN_SIDE, y), f"Type: {addr_type_display}", font=theme.get_font('body'), fill=theme.get_color('WHITE'))
    y += 25

    # Address
    address = state.bitcoin_address if state.bitcoin_address else "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
    draw.text((config.MARGIN_SIDE, y), "Address:", font=theme.get_font('body'), fill=theme.get_color('WHITE'))
    y += 20

    # Wrap address text
    draw_text(
        draw, address,
        (config.MARGIN_SIDE, y),
        theme.get_font('hint'),
        theme.get_color('CYAN'),
        max_width=config.DISPLAY_WIDTH - (2 * config.MARGIN_SIDE)
    )
    y += 40

    # QR code (smaller)
    qr_image = create_qr_code(address, 100)
    qr_x = (config.DISPLAY_WIDTH - 100) // 2
    canvas.paste(qr_image, (qr_x, y))

    # Status bar
    draw_status_bar(draw, theme, hint="◀ Back ✓ Copy")

    return canvas


def render_camera_preview_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render camera preview page.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BLACK'))
    draw = canvas._getdraw()

    # Header
    draw_header(draw, theme, "📷 CAMERA PREVIEW")

    # Camera feed placeholder (would be replaced with actual camera frame)
    from hardware.camera import get_camera
    camera = get_camera()
    frame = camera.get_frame()

    if frame:
        # Resize to fit content area
        frame = frame.resize((config.DISPLAY_WIDTH, config.CONTENT_HEIGHT), Image.Resampling.LANCZOS)
        canvas.paste(frame, (0, config.HEADER_HEIGHT))
    else:
        # Placeholder
        draw.text(
            (config.DISPLAY_WIDTH // 2 - 60, config.DISPLAY_HEIGHT // 2),
            "No camera feed",
            font=theme.get_font('body'),
            fill=theme.get_color('GRAY')
        )

    # Status bar
    draw_status_bar(draw, theme, hint="◀ Back ✓ Capture")

    return canvas


def render_settings_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render settings menu page.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BLACK'))
    draw = canvas._getdraw()

    # Header
    draw_header(draw, theme, "⚙ SETTINGS")

    # Menu items
    menu_items = [
        "Display Brightness",
        "Screen Timeout",
        "Language",
        "Reset to Defaults"
    ]

    y_start = config.HEADER_HEIGHT + 20
    item_spacing = 35

    for i, item in enumerate(menu_items):
        draw_menu_item(
            draw, theme, item,
            y_start + (i * item_spacing),
            selected=(i == state.menu_index)
        )

    # Status bar
    draw_status_bar(draw, theme, hint="◀ Back ▶ Enter")

    return canvas


def render_brightness_setting_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render brightness setting page with slider.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BLACK'))
    draw = canvas._getdraw()

    # Header
    draw_header(draw, theme, "☀ BRIGHTNESS")

    y = config.HEADER_HEIGHT + 30

    # Current value
    draw.text(
        (config.MARGIN_SIDE, y),
        f"Current: {state.slider_value}%",
        font=theme.get_font('body'),
        fill=theme.get_color('WHITE')
    )
    y += 40

    # Slider
    draw_slider(
        draw, theme,
        state.slider_value, 0, 100,
        (config.MARGIN_SIDE, y),
        width=200
    )
    y += 40

    # Range labels
    draw.text((config.MARGIN_SIDE, y), "0%", font=theme.get_font('hint'), fill=theme.get_color('GRAY'))
    draw.text((config.DISPLAY_WIDTH - 40, y), "100%", font=theme.get_font('hint'), fill=theme.get_color('GRAY'))

    # Status bar
    draw_status_bar(draw, theme, hint="◀─ Adjust ─► ✓ Save")

    return canvas


def render_timeout_setting_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render timeout setting page with slider.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BLACK'))
    draw = canvas._getdraw()

    # Header
    draw_header(draw, theme, "⏱ SCREEN TIMEOUT")

    y = config.HEADER_HEIGHT + 30

    # Current value (convert seconds to display format)
    if state.slider_value >= 60:
        minutes = state.slider_value // 60
        display_text = f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        display_text = f"{state.slider_value} seconds"

    draw.text(
        (config.MARGIN_SIDE, y),
        f"Current: {display_text}",
        font=theme.get_font('body'),
        fill=theme.get_color('WHITE')
    )
    y += 40

    # Slider
    draw_slider(
        draw, theme,
        state.slider_value, 30, 600,
        (config.MARGIN_SIDE, y),
        width=200
    )
    y += 40

    # Range labels
    draw.text((config.MARGIN_SIDE, y), "30s", font=theme.get_font('hint'), fill=theme.get_color('GRAY'))
    draw.text((config.DISPLAY_WIDTH - 40, y), "10m", font=theme.get_font('hint'), fill=theme.get_color('GRAY'))

    # Status bar
    draw_status_bar(draw, theme, hint="◀─ Adjust ─► ✓ Save")

    return canvas


def render_language_setting_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render language selection page.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BLACK'))
    draw = canvas._getdraw()

    # Header
    draw_header(draw, theme, "🌐 LANGUAGE")

    # Language options
    languages = [
        ('en', 'English'),
        ('fi', 'Suomi (Finnish)')
    ]

    y_start = config.HEADER_HEIGHT + 30
    item_spacing = 35

    for i, (code, name) in enumerate(languages):
        selected = (code == state.language)
        draw_menu_item(
            draw, theme, name,
            y_start + (i * item_spacing),
            selected=selected
        )

    # Status bar
    draw_status_bar(draw, theme, hint="▲▼ Select ✓ Apply")

    return canvas


def render_reset_setting_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render reset confirmation dialog.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BLACK'))
    draw = canvas._getdraw()

    # Header
    draw_header(draw, theme, "🔄 RESET")

    # Dialog box
    dialog_width = 260
    dialog_height = 120
    dialog_x = (config.DISPLAY_WIDTH - dialog_width) // 2
    dialog_y = config.HEADER_HEIGHT + 30

    # Draw dialog background
    draw.rectangle(
        [(dialog_x, dialog_y), (dialog_x + dialog_width, dialog_y + dialog_height)],
        fill=theme.get_color('DARK_GRAY'),
        outline=theme.get_color('LIGHT_GRAY')
    )

    # Warning text
    warning_text = "Reset to defaults?"
    bbox = draw.textbbox((0, 0), warning_text, font=theme.get_font('body'))
    text_width = bbox[2] - bbox[0]
    draw.text(
        (dialog_x + (dialog_width - text_width) // 2, dialog_y + 20),
        warning_text,
        font=theme.get_font('body'),
        fill=theme.get_color('ORANGE')
    )

    # Subtext
    subtext = "All settings will be lost"
    bbox = draw.textbbox((0, 0), subtext, font=theme.get_font('hint'))
    text_width = bbox[2] - bbox[0]
    draw.text(
        (dialog_x + (dialog_width - text_width) // 2, dialog_y + 50),
        subtext,
        font=theme.get_font('hint'),
        fill=theme.get_color('GRAY')
    )

    # Buttons
    button_y = dialog_y + 80
    draw_button(draw, theme, "YES", (dialog_x + 40, button_y), selected=(state.menu_index == 0))
    draw_button(draw, theme, "NO", (dialog_x + 150, button_y), selected=(state.menu_index == 1))

    # Status bar
    draw_status_bar(draw, theme, hint="◀─ Select ─► ✓ Confirm")

    return canvas


def render_about_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render about/info page.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BLACK'))
    draw = canvas._getdraw()

    # Header
    draw_header(draw, theme, "ℹ ABOUT")

    y = config.HEADER_HEIGHT + 10 - state.scroll_offset

    # Device info
    info_lines = [
        ("Device:", "SeedSigner Mini"),
        ("Version:", "1.0.0"),
        ("Build:", datetime.now().strftime("%Y%m%d")),
        ("", ""),
        ("Hardware:", ""),
        ("├─ Display:", "ST7789 320x240"),
        ("├─ Camera:", "RPi Cam v2/v3"),
        ("├─ Input:", "HW-504 Joystick"),
        ("└─ CPU:", "Raspberry Pi 4B"),
    ]

    for label, value in info_lines:
        if label:
            full_text = f"{label} {value}"
            draw.text(
                (config.MARGIN_SIDE, y),
                full_text,
                font=theme.get_font('body') if not label.startswith('├') and not label.startswith('└') else theme.get_font('hint'),
                fill=theme.get_color('WHITE') if not label.startswith('├') and not label.startswith('└') else theme.get_color('GRAY')
            )
        y += 18

    # Status bar
    draw_status_bar(draw, theme, hint="◀ Back ▲▼ Scroll")

    return canvas


def render_loading_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render loading page with spinner and progress.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BLACK'))
    draw = canvas._getdraw()

    # Header
    draw_header(draw, theme, "⏳ PROCESSING...")

    # Loading message
    message = state.loading_message
    bbox = draw.textbbox((0, 0), message, font=theme.get_font('body'))
    message_width = bbox[2] - bbox[0]
    draw.text(
        ((config.DISPLAY_WIDTH - message_width) // 2, 80),
        message,
        font=theme.get_font('body'),
        fill=theme.get_color('WHITE')
    )

    # Spinner
    state.update_spinner()
    draw_spinner(draw, theme, (config.DISPLAY_WIDTH // 2, 130), state.spinner_frame)

    # Progress bar
    if state.loading_progress > 0:
        draw_progress_bar(draw, theme, state.loading_progress, (20, 170))

    return canvas


def render_error_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render error page with message and options.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BLACK'))
    draw = canvas._getdraw()

    # Header
    draw_header(draw, theme, "⚠ ERROR")

    y = config.HEADER_HEIGHT + 20

    # Error message
    error_text = state.error_message if state.error_message else "An error occurred"
    y += draw_text(
        draw, error_text,
        (config.MARGIN_SIDE, y),
        theme.get_font('body'),
        theme.get_color('RED'),
        max_width=config.DISPLAY_WIDTH - (2 * config.MARGIN_SIDE)
    ) + 10

    # Error code
    if state.error_code:
        draw.text(
            (config.MARGIN_SIDE, y),
            f"Code: {state.error_code}",
            font=theme.get_font('hint'),
            fill=theme.get_color('GRAY')
        )
        y += 30

    # Buttons
    button_y = config.DISPLAY_HEIGHT - config.STATUS_BAR_HEIGHT - 50
    draw_button(draw, theme, "Retry", (50, button_y), selected=(state.menu_index == 0))
    draw_button(draw, theme, "Back", (170, button_y), selected=(state.menu_index == 1))

    # Status bar
    draw_status_bar(draw, theme, hint="▲▼ Select ✓ Execute")

    return canvas


# Page renderer registry
PAGE_RENDERERS = {
    config.PAGE_SPLASH: render_splash_page,
    config.PAGE_HOME: render_home_page,
    config.PAGE_VERIFY_SIGNATURE: render_verify_signature_page,
    config.PAGE_GENERATE_QR: render_generate_qr_page,
    config.PAGE_VIEW_ADDRESS: render_view_address_page,
    config.PAGE_CAMERA_PREVIEW: render_camera_preview_page,
    config.PAGE_SETTINGS: render_settings_page,
    config.PAGE_BRIGHTNESS_SETTING: render_brightness_setting_page,
    config.PAGE_TIMEOUT_SETTING: render_timeout_setting_page,
    config.PAGE_LANGUAGE_SETTING: render_language_setting_page,
    config.PAGE_RESET_SETTING: render_reset_setting_page,
    config.PAGE_ABOUT: render_about_page,
    config.PAGE_LOADING: render_loading_page,
    config.PAGE_ERROR: render_error_page,
}


def render_page(page_name: str, state: PageState, theme: Theme) -> Image.Image:
    """
    Render a page by name.

    Args:
        page_name: Page constant from config
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    renderer = PAGE_RENDERERS.get(page_name)

    if renderer:
        try:
            return renderer(state, theme)
        except Exception as e:
            logger.error(f"Page render error for {page_name}: {e}")
            # Fallback to error page
            state.error_message = f"Failed to render {page_name}"
            state.error_code = str(e)
            return render_error_page(state, theme)
    else:
        logger.error(f"No renderer for page: {page_name}")
        state.error_message = f"Unknown page: {page_name}"
        return render_error_page(state, theme)
