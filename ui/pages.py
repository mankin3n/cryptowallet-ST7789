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
from ui import ascii_art

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

    # Hacker-style boot sequence
    y = 20
    for i, line in enumerate(ascii_art.BOOT_SEQUENCE[:4]):
        if i < (state.spinner_frame // 2):
            draw.text(
                (10, y),
                line,
                font=theme.get_font('hint'),
                fill=theme.get_color('GREEN')
            )
            y += 18

    # ASCII art logo
    logo_lines = ascii_art.GLITCH_LOGO.strip().split('\n')
    logo_y = 100
    for line in logo_lines:
        draw.text(
            (20, logo_y),
            line,
            font=theme.get_font('body'),
            fill=theme.get_color('CYAN')
        )
        logo_y += 20

    # Terminal-style loading indicator
    state.update_spinner()
    loading_idx = state.spinner_frame % len(ascii_art.LOADING_FRAMES)
    loading_bar = ascii_art.LOADING_FRAMES[loading_idx]
    draw.text(
        (config.DISPLAY_WIDTH // 2 - 30, 180),
        loading_bar,
        font=theme.get_font('body'),
        fill=theme.get_color('GREEN')
    )

    # Matrix-style decoration at bottom
    draw.text(
        (10, config.DISPLAY_HEIGHT - 30),
        ascii_art.MATRIX_LINES[state.spinner_frame % len(ascii_art.MATRIX_LINES)],
        font=theme.get_font('hint'),
        fill=theme.get_color('DARK_GREEN')
    )

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

    # Terminal-style header
    y = 5
    header_lines = ascii_art.TERMINAL_HEADER.strip().split('\n')
    for line in header_lines:
        draw.text(
            (10, y),
            line,
            font=theme.get_font('hint'),
            fill=theme.get_color('GREEN')
        )
        y += 15

    # Separator
    draw.text(
        (10, y + 5),
        ascii_art.GLITCH_SEP,
        font=theme.get_font('hint'),
        fill=theme.get_color('CYAN')
    )

    # Menu items with terminal pointer
    menu_items = [
        "Verify Signature",
        "Generate QR Code",
        "View Address",
        "Settings",
        "About"
    ]

    y_start = y + 30
    item_spacing = 30

    for i, item in enumerate(menu_items):
        prefix = ascii_art.MENU_SELECTED_PREFIX if i == state.menu_index else " "
        color = theme.get_color('CYAN') if i == state.menu_index else theme.get_color('WHITE')

        draw.text(
            (15, y_start + (i * item_spacing)),
            f"{prefix} {item}",
            font=theme.get_font('menu'),
            fill=color
        )

    # Status bar with hacker style
    draw_status_bar(draw, theme, hint="↑↓ Select → Enter")

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

    # Terminal-style header
    draw.text((10, 10), "┌[SIGNATURE VERIFICATION]───────────┐",
              font=theme.get_font('hint'), fill=theme.get_color('CYAN'))

    y = 40

    # Display validation result with ASCII art
    if state.signature_valid:
        result_lines = ascii_art.SIGNATURE_VALID.strip().split('\n')
        color = theme.get_color('GREEN')
        status_icon = ascii_art.STATUS_SUCCESS
    else:
        result_lines = ascii_art.SIGNATURE_INVALID.strip().split('\n')
        color = theme.get_color('RED')
        status_icon = ascii_art.STATUS_ERROR

    for line in result_lines:
        draw.text((60, y), line, font=theme.get_font('hint'), fill=color)
        y += 15

    y += 10

    # Signature data with hex display
    if state.signature_data:
        draw.text((15, y), f"{status_icon} Signature Hash:",
                  font=theme.get_font('body'), fill=theme.get_color('WHITE'))
        y += 20

        # Show as hex
        hex_sig = ascii_art.hex_display(state.signature_data[:16], 8)
        draw.text((20, y), f"0x{hex_sig}",
                  font=theme.get_font('hint'), fill=theme.get_color('CYAN'))
        y += 20
        draw.text((20, y), "...", font=theme.get_font('hint'), fill=theme.get_color('GRAY'))
    else:
        draw.text((15, y), f"{ascii_art.STATUS_ERROR} No signature data loaded",
                  font=theme.get_font('body'), fill=theme.get_color('ORANGE'))

    # Status bar
    draw_status_bar(draw, theme, hint="← Back")

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

    # QR frame header
    y = 10
    qr_header_lines = ascii_art.QR_FRAME_HEADER.strip().split('\n')
    for line in qr_header_lines:
        draw.text((10, y), line, font=theme.get_font('hint'), fill=theme.get_color('CYAN'))
        y += 15

    # Generate QR code
    qr_data = state.qr_data if state.qr_data else "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
    qr_size = int(config.QR_MAX_SIZE * (state.qr_zoom / 100.0))
    qr_size = max(80, min(160, qr_size))

    qr_image = create_qr_code(qr_data, qr_size)

    # Center QR code
    qr_x = (config.DISPLAY_WIDTH - qr_size) // 2
    qr_y = y + 10

    canvas.paste(qr_image, (qr_x, qr_y))

    # QR frame footer
    y = qr_y + qr_size + 10
    qr_footer_lines = ascii_art.QR_FRAME_FOOTER.strip().split('\n')
    for line in qr_footer_lines:
        draw.text((10, y), line, font=theme.get_font('hint'), fill=theme.get_color('CYAN'))
        y += 15

    # Zoom indicator with progress bar style
    zoom_text = f"[ZOOM: {state.qr_zoom}%]"
    draw.text(
        (config.DISPLAY_WIDTH - 120, y),
        zoom_text,
        font=theme.get_font('hint'),
        fill=theme.get_color('GREEN')
    )

    # Status bar
    draw_status_bar(draw, theme, hint="← Back ↑↓ Zoom")

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

    # Terminal-style header
    draw.text((10, 10), "┌[₿ BITCOIN WALLET ADDRESS]─────────┐",
              font=theme.get_font('hint'), fill=theme.get_color('CYAN'))

    y = 35

    # Address type with status indicator
    addr_type_display = state.bitcoin_address_type.replace('_', ' ').title()
    draw.text((15, y), f"{ascii_art.STATUS_ONLINE} Type: {addr_type_display}",
              font=theme.get_font('body'), fill=theme.get_color('GREEN'))
    y += 25

    # Address in terminal box
    address = state.bitcoin_address if state.bitcoin_address else "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"

    # Use terminal box format
    addr_display = ascii_art.format_address_terminal(address)
    addr_lines = addr_display.strip().split('\n')
    for line in addr_lines:
        draw.text((15, y), line, font=theme.get_font('hint'), fill=theme.get_color('CYAN'))
        y += 15

    y += 5

    # QR code (smaller) with frame
    qr_image = create_qr_code(address, 90)
    qr_x = (config.DISPLAY_WIDTH - 90) // 2
    canvas.paste(qr_image, (qr_x, y))

    # Status bar
    draw_status_bar(draw, theme, hint="← Back → Copy")

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

    # Terminal-style settings header
    draw.text((10, 10), "┌[⚙ SYSTEM CONFIG]──────────────────┐",
              font=theme.get_font('hint'), fill=theme.get_color('CYAN'))

    # Menu items with terminal styling
    menu_items = [
        ("Display Brightness", "☀"),
        ("Screen Timeout", "⏱"),
        ("Language", "🌐"),
        ("Reset to Defaults", "🔄")
    ]

    y_start = 45
    item_spacing = 35

    for i, (item, icon) in enumerate(menu_items):
        prefix = ">>" if i == state.menu_index else "  "
        color = theme.get_color('CYAN') if i == state.menu_index else theme.get_color('WHITE')

        draw.text(
            (15, y_start + (i * item_spacing)),
            f"{prefix} {icon} {item}",
            font=theme.get_font('menu'),
            fill=color
        )

    # Separator at bottom
    draw.text((10, y_start + (len(menu_items) * item_spacing) + 10),
              ascii_art.GLITCH_SEP[:35],
              font=theme.get_font('hint'), fill=theme.get_color('DARK_GREEN'))

    # Status bar
    draw_status_bar(draw, theme, hint="← Back → Enter")

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

    # System info header
    y = 10 - state.scroll_offset
    info_header_lines = ascii_art.SYSTEM_INFO_HEADER.strip().split('\n')
    for line in info_header_lines:
        draw.text((10, y), line, font=theme.get_font('hint'), fill=theme.get_color('CYAN'))
        y += 15

    # Device info with terminal styling
    info_lines = [
        (f"{ascii_art.STATUS_ONLINE} Device:", "SeedSigner Mini"),
        (f"{ascii_art.STATUS_SUCCESS} Version:", "v1.0.0-HACKER"),
        (f"{ascii_art.STATUS_PROCESSING} Build:", datetime.now().strftime("0x%Y%m%d")),
        ("", ""),
        ("Hardware Specs:", ""),
        ("├─ Display:", "ST7789 320x240"),
        ("├─ Camera:", "RPi Cam v2/v3"),
        ("├─ Input:", "HW-504 Joystick"),
        ("└─ CPU:", "Raspberry Pi 4B"),
        ("", ""),
        ("Security:", ""),
        ("├─ Air-Gapped:", "YES"),
        ("├─ Encrypted:", "YES"),
        ("└─ Open Source:", "YES"),
    ]

    for label, value in info_lines:
        if label:
            full_text = f"{label} {value}"
            color = theme.get_color('GREEN') if label.startswith('├') or label.startswith('└') else theme.get_color('CYAN')
            draw.text(
                (15, y),
                full_text,
                font=theme.get_font('hint'),
                fill=color
            )
        y += 16

    # Footer
    footer_lines = ascii_art.SYSTEM_INFO_FOOTER.strip().split('\n')
    for line in footer_lines:
        draw.text((10, y), line, font=theme.get_font('hint'), fill=theme.get_color('CYAN'))
        y += 15

    # Status bar
    draw_status_bar(draw, theme, hint="← Back ↑↓ Scroll")

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

    y = 30

    # Processing indicator
    draw.text((10, y), "┌[PROCESSING]────────────────────────┐",
              font=theme.get_font('hint'), fill=theme.get_color('CYAN'))
    y += 25

    # Loading message
    message = state.loading_message if state.loading_message else "Please wait..."
    draw.text(
        (20, y),
        f"{ascii_art.STATUS_PROCESSING} {message}",
        font=theme.get_font('body'),
        fill=theme.get_color('GREEN')
    )
    y += 30

    # Animated loading bar
    state.update_spinner()
    loading_idx = state.spinner_frame % len(ascii_art.LOADING_FRAMES)
    loading_animation = ascii_art.LOADING_FRAMES[loading_idx]
    draw.text(
        (config.DISPLAY_WIDTH // 2 - 30, y),
        loading_animation,
        font=theme.get_font('body'),
        fill=theme.get_color('CYAN')
    )
    y += 30

    # Encryption animation
    encrypt_idx = state.spinner_frame % len(ascii_art.ENCRYPT_FRAMES)
    encrypt_bar = ascii_art.ENCRYPT_FRAMES[encrypt_idx]
    draw.text(
        (config.DISPLAY_WIDTH // 2 - 40, y),
        encrypt_bar,
        font=theme.get_font('body'),
        fill=theme.get_color('GREEN')
    )
    y += 30

    # Progress bar if available
    if state.loading_progress > 0:
        progress_text = ascii_art.draw_hacker_progress(state.loading_progress, 28)
        draw.text((20, y), progress_text, font=theme.get_font('hint'), fill=theme.get_color('CYAN'))

    # Data stream decoration
    stream_idx = state.spinner_frame % len(ascii_art.DATA_STREAM)
    draw.text(
        (10, config.DISPLAY_HEIGHT - 40),
        ascii_art.DATA_STREAM[stream_idx],
        font=theme.get_font('hint'),
        fill=theme.get_color('DARK_GREEN')
    )

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

    # Error box ASCII art
    y = 10
    error_lines = ascii_art.ERROR_BOX.strip().split('\n')
    for line in error_lines[:7]:  # Show first 7 lines of error box
        draw.text((5, y), line, font=theme.get_font('hint'), fill=theme.get_color('RED'))
        y += 14

    y += 10

    # Error message
    error_text = state.error_message if state.error_message else "System malfunction detected"
    draw_text(
        draw, error_text,
        (15, y),
        theme.get_font('body'),
        theme.get_color('ORANGE'),
        max_width=config.DISPLAY_WIDTH - 30
    )
    y += 35

    # Error code with hex display
    if state.error_code:
        draw.text(
            (15, y),
            f"{ascii_art.STATUS_ERROR} Error Code: 0x{hash(state.error_code) & 0xFFFF:04X}",
            font=theme.get_font('hint'),
            fill=theme.get_color('RED')
        )
        y += 20
        draw.text(
            (15, y),
            f"Details: {state.error_code[:30]}",
            font=theme.get_font('hint'),
            fill=theme.get_color('GRAY')
        )

    # Action prompts (hacker style)
    button_y = config.DISPLAY_HEIGHT - config.STATUS_BAR_HEIGHT - 45
    retry_prefix = ">>" if state.menu_index == 0 else "  "
    back_prefix = ">>" if state.menu_index == 1 else "  "

    draw.text((20, button_y), f"{retry_prefix} [RETRY]",
              font=theme.get_font('body'),
              fill=theme.get_color('CYAN') if state.menu_index == 0 else theme.get_color('GRAY'))
    draw.text((160, button_y), f"{back_prefix} [BACK]",
              font=theme.get_font('body'),
              fill=theme.get_color('CYAN') if state.menu_index == 1 else theme.get_color('GRAY'))

    # Status bar
    draw_status_bar(draw, theme, hint="← → Select ✓ Execute")

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
