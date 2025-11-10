"""
Page Renderers for All UI Pages.

Contains rendering functions for all 11 pages in the UI architecture.
Each function takes PageState and Theme, returns PIL Image.
"""

import logging
import time
from datetime import datetime
from PIL import Image, ImageDraw
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
    Render a modern splash screen with a logo and loading animation.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BACKGROUND'))
    draw = ImageDraw.Draw(canvas)

    # App name
    app_name = "CryptoWallet"
    font_large = theme.get_font('header')
    text_width, text_height = draw.textsize(app_name, font=font_large)
    draw.text(
        ((config.DISPLAY_WIDTH - text_width) / 2, 80),
        app_name,
        font=font_large,
        fill=theme.get_color('PRIMARY')
    )

    # Loading text
    loading_text = "Initializing..."
    font_small = theme.get_font('body')
    text_width, _ = draw.textsize(loading_text, font=font_small)
    draw.text(
        ((config.DISPLAY_WIDTH - text_width) / 2, 130),
        loading_text,
        font=font_small,
        fill=theme.get_color('TEXT')
    )

    # Progress bar
    state.update_spinner()
    progress = (state.spinner_frame % 50) / 49.0  # Simple progress animation
    progress_width = int(150 * progress)
    progress_y = 170
    draw.rectangle(
        [
            ((config.DISPLAY_WIDTH - 150) / 2, progress_y),
            ((config.DISPLAY_WIDTH - 150) / 2 + progress_width, progress_y + 5)
        ],
        fill=theme.get_color('PRIMARY')
    )
    draw.rectangle(
        [
            ((config.DISPLAY_WIDTH - 150) / 2, progress_y),
            ((config.DISPLAY_WIDTH + 150) / 2, progress_y + 5)
        ],
        outline=theme.get_color('SECONDARY')
    )

    return canvas


def render_home_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render a modern main menu page.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BACKGROUND'))
    draw = ImageDraw.Draw(canvas)

    # Header
    draw_header(draw, theme, "MAIN MENU")

    # Menu items
    menu_items = [
        "Verify Signature",
        "Generate QR Code",
        "View Address",
        "Settings",
        "About"
    ]

    y_start = config.HEADER_HEIGHT + 20
    item_spacing = 35

    for i, item in enumerate(menu_items):
        is_selected = (i == state.menu_index)
        
        # Selection highlight
        if is_selected:
            draw.rectangle(
                [
                    (config.MARGIN_SIDE, y_start + (i * item_spacing) - 5),
                    (config.DISPLAY_WIDTH - config.MARGIN_SIDE, y_start + (i * item_spacing) + item_spacing - 10)
                ],
                fill=theme.get_color('SURFACE')
            )
        
        # Text
        color = theme.get_color('PRIMARY') if is_selected else theme.get_color('TEXT')
        draw.text(
            (config.MARGIN_SIDE + 15, y_start + (i * item_spacing)),
            item,
            font=theme.get_font('menu'),
            fill=color
        )

    # Status bar
    draw_status_bar(draw, theme, hint="↑↓ Select | ✓ Enter")

    return canvas


def render_verify_signature_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render a modern signature verification page.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BACKGROUND'))
    draw = ImageDraw.Draw(canvas)

    # Header
    draw_header(draw, theme, "VERIFY SIGNATURE")

    y = config.HEADER_HEIGHT + 30

    # Display validation result
    if state.signature_valid:
        status_text = "SIGNATURE VALID"
        status_color = theme.get_color('SUCCESS')
        icon = "✓"
    else:
        status_text = "SIGNATURE INVALID"
        status_color = theme.get_color('DANGER')
        icon = "✗"

    # Status text
    font_large = theme.get_font('header')
    text_width, _ = draw.textsize(status_text, font=font_large)
    draw.text(
        ((config.DISPLAY_WIDTH - text_width) / 2, y),
        f"{icon} {status_text}",
        font=font_large,
        fill=status_color
    )
    y += 50

    # Signature data
    if state.signature_data:
        draw.text(
            (config.MARGIN_SIDE, y),
            "Signature Hash:",
            font=theme.get_font('body'),
            fill=theme.get_color('TEXT')
        )
        y += 25

        # Show as hex
        hex_sig = state.signature_data.hex()[:32]
        draw_text(
            draw,
            hex_sig,
            (config.MARGIN_SIDE, y),
            theme.get_font('hint'),
            theme.get_color('MUTED'),
            max_width=config.DISPLAY_WIDTH - (2 * config.MARGIN_SIDE)
        )
    else:
        draw.text(
            (config.MARGIN_SIDE, y),
            "No signature data loaded",
            font=theme.get_font('body'),
            fill=theme.get_color('WARNING')
        )

    # Status bar
    draw_status_bar(draw, theme, hint="← Back")

    return canvas


def render_generate_qr_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render a modern QR code generation page.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BACKGROUND'))
    draw = ImageDraw.Draw(canvas)

    # Header
    draw_header(draw, theme, "QR CODE")

    # Generate QR code
    qr_data = state.qr_data if state.qr_data else "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
    qr_size = int(config.QR_MAX_SIZE * (state.qr_zoom / 100.0))
    qr_size = max(80, min(160, qr_size))

    qr_image = create_qr_code(qr_data, qr_size, theme.get_color('TEXT'), theme.get_color('BACKGROUND'))

    # Center QR code
    qr_x = (config.DISPLAY_WIDTH - qr_size) // 2
    qr_y = config.HEADER_HEIGHT + 15

    canvas.paste(qr_image, (qr_x, qr_y))

    # Zoom indicator
    zoom_text = f"Zoom: {state.qr_zoom}%"
    font_small = theme.get_font('hint')
    text_width, _ = draw.textsize(zoom_text, font=font_small)
    draw.text(
        ((config.DISPLAY_WIDTH - text_width) / 2, config.DISPLAY_HEIGHT - config.STATUS_BAR_HEIGHT - 25),
        zoom_text,
        font=font_small,
        fill=theme.get_color('MUTED')
    )

    # Status bar
    draw_status_bar(draw, theme, hint="← Back | ↑↓ Zoom")

    return canvas


def render_view_address_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render a modern Bitcoin address view page.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BACKGROUND'))
    draw = ImageDraw.Draw(canvas)

    # Header
    draw_header(draw, theme, "BITCOIN ADDRESS")

    y = config.HEADER_HEIGHT + 15

    # Address type
    addr_type_display = state.bitcoin_address_type.replace('_', ' ').title()
    draw.text(
        (config.MARGIN_SIDE, y),
        f"Type: {addr_type_display}",
        font=theme.get_font('body'),
        fill=theme.get_color('MUTED')
    )
    y += 25

    # Address
    address = state.bitcoin_address if state.bitcoin_address else "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
    draw_text(
        draw,
        address,
        (config.MARGIN_SIDE, y),
        theme.get_font('hint'),
        theme.get_color('TEXT'),
        max_width=config.DISPLAY_WIDTH - (2 * config.MARGIN_SIDE)
    )
    y += 50

    # QR code
    qr_image = create_qr_code(address, 90, theme.get_color('TEXT'), theme.get_color('BACKGROUND'))
    qr_x = (config.DISPLAY_WIDTH - 90) // 2
    canvas.paste(qr_image, (qr_x, y))

    # Status bar
    draw_status_bar(draw, theme, hint="← Back | ✓ Copy")

    return canvas


def render_camera_preview_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render a modern camera preview page.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BACKGROUND'))
    draw = ImageDraw.Draw(canvas)

    # Header
    draw_header(draw, theme, "CAMERA PREVIEW")

    # Camera feed
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
            fill=theme.get_color('MUTED')
        )

    # Status bar
    draw_status_bar(draw, theme, hint="← Back | ✓ Capture")

    return canvas


def render_settings_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render a modern settings menu page.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BACKGROUND'))
    draw = ImageDraw.Draw(canvas)

    # Header
    draw_header(draw, theme, "SETTINGS")

    # Menu items
    menu_items = [
        ("Display Brightness", "☀"),
        ("Screen Timeout", "⏱"),
        ("Language", "🌐"),
        ("Reset to Defaults", "🔄")
    ]

    y_start = config.HEADER_HEIGHT + 20
    item_spacing = 35

    for i, (item, icon) in enumerate(menu_items):
        is_selected = (i == state.menu_index)
        
        # Selection highlight
        if is_selected:
            draw.rectangle(
                [
                    (config.MARGIN_SIDE, y_start + (i * item_spacing) - 5),
                    (config.DISPLAY_WIDTH - config.MARGIN_SIDE, y_start + (i * item_spacing) + item_spacing - 10)
                ],
                fill=theme.get_color('SURFACE')
            )
        
        # Text
        color = theme.get_color('PRIMARY') if is_selected else theme.get_color('TEXT')
        draw.text(
            (config.MARGIN_SIDE + 15, y_start + (i * item_spacing)),
            f"{icon} {item}",
            font=theme.get_font('menu'),
            fill=color
        )

    # Status bar
    draw_status_bar(draw, theme, hint="↑↓ Select | ✓ Enter")

    return canvas


def render_brightness_setting_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render a modern brightness setting page with a slider.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BACKGROUND'))
    draw = ImageDraw.Draw(canvas)

    # Header
    draw_header(draw, theme, "DISPLAY BRIGHTNESS")

    y = config.HEADER_HEIGHT + 40

    # Current value
    draw.text(
        (config.MARGIN_SIDE, y),
        f"Current: {state.slider_value}%",
        font=theme.get_font('body'),
        fill=theme.get_color('TEXT')
    )
    y += 50

    # Slider
    draw_slider(
        draw, theme,
        state.slider_value, 0, 100,
        (config.MARGIN_SIDE, y),
        width=config.DISPLAY_WIDTH - (2 * config.MARGIN_SIDE)
    )
    y += 40

    # Range labels
    draw.text((config.MARGIN_SIDE, y), "0%", font=theme.get_font('hint'), fill=theme.get_color('MUTED'))
    draw.text((config.DISPLAY_WIDTH - 40, y), "100%", font=theme.get_font('hint'), fill=theme.get_color('MUTED'))

    # Status bar
    draw_status_bar(draw, theme, hint="← Adjust → | ✓ Save")

    return canvas


def render_timeout_setting_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render a modern timeout setting page with a slider.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BACKGROUND'))
    draw = ImageDraw.Draw(canvas)

    # Header
    draw_header(draw, theme, "SCREEN TIMEOUT")

    y = config.HEADER_HEIGHT + 40

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
        fill=theme.get_color('TEXT')
    )
    y += 50

    # Slider
    draw_slider(
        draw, theme,
        state.slider_value, 30, 600,
        (config.MARGIN_SIDE, y),
        width=config.DISPLAY_WIDTH - (2 * config.MARGIN_SIDE)
    )
    y += 40

    # Range labels
    draw.text((config.MARGIN_SIDE, y), "30s", font=theme.get_font('hint'), fill=theme.get_color('MUTED'))
    draw.text((config.DISPLAY_WIDTH - 40, y), "10m", font=theme.get_font('hint'), fill=theme.get_color('MUTED'))

    # Status bar
    draw_status_bar(draw, theme, hint="← Adjust → | ✓ Save")

    return canvas


def render_language_setting_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render a modern language selection page.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BACKGROUND'))
    draw = ImageDraw.Draw(canvas)

    # Header
    draw_header(draw, theme, "LANGUAGE")

    # Language options
    languages = [
        ('en', 'English'),
        ('fi', 'Suomi (Finnish)')
    ]

    y_start = config.HEADER_HEIGHT + 20
    item_spacing = 35

    for i, (code, name) in enumerate(languages):
        is_selected = (code == state.language)
        
        # Selection highlight
        if is_selected:
            draw.rectangle(
                [
                    (config.MARGIN_SIDE, y_start + (i * item_spacing) - 5),
                    (config.DISPLAY_WIDTH - config.MARGIN_SIDE, y_start + (i * item_spacing) + item_spacing - 10)
                ],
                fill=theme.get_color('SURFACE')
            )
        
        # Text
        color = theme.get_color('PRIMARY') if is_selected else theme.get_color('TEXT')
        draw.text(
            (config.MARGIN_SIDE + 15, y_start + (i * item_spacing)),
            name,
            font=theme.get_font('menu'),
            fill=color
        )

    # Status bar
    draw_status_bar(draw, theme, hint="↑↓ Select | ✓ Apply")

    return canvas


def render_reset_setting_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render a modern reset confirmation dialog.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BACKGROUND'))
    draw = ImageDraw.Draw(canvas)

    # Header
    draw_header(draw, theme, "RESET TO DEFAULTS")

    # Dialog box
    dialog_width = 280
    dialog_height = 130
    dialog_x = (config.DISPLAY_WIDTH - dialog_width) // 2
    dialog_y = config.HEADER_HEIGHT + 20

    # Draw dialog background
    draw.rectangle(
        [(dialog_x, dialog_y), (dialog_x + dialog_width, dialog_y + dialog_height)],
        fill=theme.get_color('SURFACE'),
        outline=theme.get_color('SECONDARY')
    )

    # Warning text
    warning_text = "Are you sure you want to reset?"
    font_body = theme.get_font('body')
    text_width, _ = draw.textsize(warning_text, font=font_body)
    draw.text(
        (dialog_x + (dialog_width - text_width) / 2, dialog_y + 20),
        warning_text,
        font=font_body,
        fill=theme.get_color('WARNING')
    )

    # Subtext
    subtext = "All settings will be lost."
    font_small = theme.get_font('hint')
    text_width, _ = draw.textsize(subtext, font=font_small)
    draw.text(
        (dialog_x + (dialog_width - text_width) / 2, dialog_y + 50),
        subtext,
        font=font_small,
        fill=theme.get_color('MUTED')
    )

    # Buttons
    button_y = dialog_y + 80
    button_width = 100
    button_height = 30
    
    # YES button
    yes_x = dialog_x + 30
    draw_button(
        draw, theme, "YES",
        (yes_x, button_y),
        width=button_width,
        height=button_height,
        selected=(state.menu_index == 0)
    )

    # NO button
    no_x = dialog_x + dialog_width - button_width - 30
    draw_button(
        draw, theme, "NO",
        (no_x, button_y),
        width=button_width,
        height=button_height,
        selected=(state.menu_index == 1)
    )

    # Status bar
    draw_status_bar(draw, theme, hint="← → Select | ✓ Confirm")

    return canvas


def render_about_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render a modern about/info page.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BACKGROUND'))
    draw = ImageDraw.Draw(canvas)

    # Header
    draw_header(draw, theme, "ABOUT")

    y = config.HEADER_HEIGHT + 15 - state.scroll_offset

    # Device info
    info_items = [
        ("Device", "SeedSigner Mini"),
        ("Version", "v1.0.0"),
        ("Build", datetime.now().strftime("%Y%m%d")),
        ("---", ""),
        ("Hardware", ""),
        ("  Display", "ST7789 320x240"),
        ("  Camera", "RPi Cam v2/v3"),
        ("  Input", "HW-504 Joystick"),
        ("  CPU", "Raspberry Pi 4B"),
        ("---", ""),
        ("Security", ""),
        ("  Air-Gapped", "YES"),
        ("  Encrypted", "YES"),
        ("  Open Source", "YES"),
    ]

    for label, value in info_items:
        if "---" in label:
            y += 5
            draw.line(
                [(config.MARGIN_SIDE, y), (config.DISPLAY_WIDTH - config.MARGIN_SIDE, y)],
                fill=theme.get_color('SECONDARY')
            )
            y += 5
            continue

        if value:
            # Render label and value
            draw.text(
                (config.MARGIN_SIDE, y),
                label,
                font=theme.get_font('body'),
                fill=theme.get_color('MUTED')
            )
            text_width, _ = draw.textsize(value, font=theme.get_font('body'))
            draw.text(
                (config.DISPLAY_WIDTH - config.MARGIN_SIDE - text_width, y),
                value,
                font=theme.get_font('body'),
                fill=theme.get_color('TEXT')
            )
        else:
            # Render a section header
            draw.text(
                (config.MARGIN_SIDE, y),
                label,
                font=theme.get_font('menu'),
                fill=theme.get_color('PRIMARY')
            )

        y += 25

    # Status bar
    draw_status_bar(draw, theme, hint="← Back | ↑↓ Scroll")

    return canvas


def render_loading_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render a modern loading page with a spinner and progress.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BACKGROUND'))
    draw = ImageDraw.Draw(canvas)

    y = 80

    # Loading message
    message = state.loading_message if state.loading_message else "Please wait..."
    font_body = theme.get_font('body')
    text_width, _ = draw.textsize(message, font=font_body)
    draw.text(
        ((config.DISPLAY_WIDTH - text_width) / 2, y),
        message,
        font=font_body,
        fill=theme.get_color('TEXT')
    )
    y += 40

    # Spinner
    state.update_spinner()
    draw_spinner(
        draw,
        theme,
        ((config.DISPLAY_WIDTH) / 2, y),
        radius=15,
        frame=state.spinner_frame
    )
    y += 40

    # Progress bar if available
    if state.loading_progress > 0:
        draw_progress_bar(
            draw,
            theme,
            state.loading_progress,
            ((config.DISPLAY_WIDTH - 150) / 2, y),
            width=150
        )

    return canvas


def render_error_page(state: PageState, theme: Theme) -> Image.Image:
    """
    Render a modern error page with a message and options.

    Args:
        state: Current page state
        theme: UI theme

    Returns:
        PIL Image (320x240)
    """
    canvas = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), theme.get_color('BACKGROUND'))
    draw = ImageDraw.Draw(canvas)

    y = 50

    # Error icon
    font_icon = theme.get_font('header')
    draw.text((config.DISPLAY_WIDTH / 2 - 15, y), "✗", font=font_icon, fill=theme.get_color('DANGER'))
    y += 40

    # Error message
    error_text = state.error_message if state.error_message else "An unknown error occurred."
    draw_text(
        draw,
        error_text,
        (config.MARGIN_SIDE, y),
        theme.get_font('body'),
        theme.get_color('TEXT'),
        max_width=config.DISPLAY_WIDTH - (2 * config.MARGIN_SIDE)
    )
    y += 40

    # Error code
    if state.error_code:
        draw_text(
            draw,
            f"Details: {state.error_code}",
            (config.MARGIN_SIDE, y),
            theme.get_font('hint'),
            theme.get_color('MUTED'),
            max_width=config.DISPLAY_WIDTH - (2 * config.MARGIN_SIDE)
        )

    # Buttons
    button_y = config.DISPLAY_HEIGHT - config.STATUS_BAR_HEIGHT - 45
    button_width = 100
    
    # RETRY button
    retry_x = 40
    draw_button(
        draw, theme, "RETRY",
        (retry_x, button_y),
        width=button_width,
        selected=(state.menu_index == 0)
    )

    # BACK button
    back_x = config.DISPLAY_WIDTH - button_width - 40
    draw_button(
        draw, theme, "BACK",
        (back_x, button_y),
        width=button_width,
        selected=(state.menu_index == 1)
    )

    # Status bar
    draw_status_bar(draw, theme, hint="← → Select | ✓ Execute")

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
