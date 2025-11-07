"""
Menu System and Navigation State Machine.

Manages page state, navigation logic, and transitions between pages.
Handles input events and updates state accordingly.
"""

import logging
from typing import Optional, Any, Dict, List
import time
import config

logger = logging.getLogger(__name__)


class PageState:
    """
    Represents the current UI state.

    Attributes:
        current_page: Name of current page
        previous_page: Name of previous page (for back button)
        menu_index: Selected menu item index
        page_stack: Stack of previous pages for navigation
        page_data: Dictionary of page-specific data
        scroll_offset: Scroll position for scrollable pages
        slider_value: Current slider value (0-100)
        brightness: Current brightness setting
        timeout: Current timeout setting (seconds)
        language: Current language ('en' or 'fi')
        confirmation_data: Data for confirmation dialogs
        error_message: Current error message
        loading_message: Current loading message
    """

    def __init__(self) -> None:
        """Initialize page state."""
        self.current_page: str = config.PAGE_SPLASH
        self.previous_page: str = config.PAGE_SPLASH
        self.menu_index: int = 0
        self.page_stack: List[str] = []
        self.page_data: Dict[str, Any] = {}
        self.scroll_offset: int = 0
        self.slider_value: int = 50

        # Settings
        self.brightness: int = config.UI_BRIGHTNESS
        self.timeout: int = config.UI_TIMEOUT
        self.language: str = config.UI_LANGUAGE

        # Dialog data
        self.confirmation_data: Dict[str, Any] = {}
        self.error_message: str = ""
        self.error_code: str = ""
        self.loading_message: str = "Loading..."
        self.loading_progress: float = 0.0

        # Bitcoin data
        self.bitcoin_address: str = ""
        self.bitcoin_address_type: str = "native_segwit"
        self.signature_data: str = ""
        self.signature_valid: bool = False

        # QR code data
        self.qr_data: str = ""
        self.qr_zoom: int = 100  # Percentage

        # Animation
        self.spinner_frame: int = 0
        self.last_frame_time: float = time.time()

    def navigate_to(self, page: str, push_to_stack: bool = True) -> None:
        """
        Navigate to a new page.

        Args:
            page: Page name constant
            push_to_stack: Whether to push current page to stack
        """
        if push_to_stack and self.current_page != config.PAGE_SPLASH:
            self.page_stack.append(self.current_page)

        self.previous_page = self.current_page
        self.current_page = page
        self.menu_index = 0
        self.scroll_offset = 0

        logger.info(f"Navigated to {page}")

    def go_back(self) -> None:
        """Navigate to previous page from stack."""
        if self.page_stack:
            previous = self.page_stack.pop()
            self.navigate_to(previous, push_to_stack=False)
        else:
            # Default to home
            self.navigate_to(config.PAGE_HOME, push_to_stack=False)

    def update_spinner(self) -> None:
        """Update spinner animation frame."""
        current_time = time.time()
        if (current_time - self.last_frame_time) > (config.SPINNER_FRAME_MS / 1000.0):
            self.spinner_frame = (self.spinner_frame + 1) % 8
            self.last_frame_time = current_time


class MenuSystem:
    """
    Menu system with input handling and navigation logic.

    Attributes:
        state: Current page state
    """

    def __init__(self) -> None:
        """Initialize menu system."""
        self.state: PageState = PageState()
        logger.info("Menu system created")

    def handle_input(self, direction: str) -> None:
        """
        Handle joystick input and update state.

        Args:
            direction: Input direction (UP/DOWN/LEFT/RIGHT/PRESS)
        """
        logger.debug(f"Input: {direction} on page {self.state.current_page}")

        # Route to page-specific handler
        handler_name = f"_handle_{self.state.current_page.lower()}"
        handler = getattr(self, handler_name, self._handle_default)
        handler(direction)

    def _handle_default(self, direction: str) -> None:
        """Default input handler."""
        if direction == config.INPUT_LEFT:
            self.state.go_back()

    def _handle_splash(self, direction: str) -> None:
        """Handle input on splash page."""
        # Auto-transition handled in main loop
        pass

    def _handle_home(self, direction: str) -> None:
        """Handle input on home page."""
        menu_items = 5

        if direction == config.INPUT_UP:
            self.state.menu_index = (self.state.menu_index - 1) % menu_items
        elif direction == config.INPUT_DOWN:
            self.state.menu_index = (self.state.menu_index + 1) % menu_items
        elif direction == config.INPUT_PRESS:
            # Navigate based on selection
            if self.state.menu_index == 0:
                self.state.navigate_to(config.PAGE_VERIFY_SIGNATURE)
            elif self.state.menu_index == 1:
                self.state.navigate_to(config.PAGE_GENERATE_QR)
            elif self.state.menu_index == 2:
                self.state.navigate_to(config.PAGE_VIEW_ADDRESS)
            elif self.state.menu_index == 3:
                self.state.navigate_to(config.PAGE_SETTINGS)
            elif self.state.menu_index == 4:
                self.state.navigate_to(config.PAGE_ABOUT)

    def _handle_verify_signature(self, direction: str) -> None:
        """Handle input on verify signature page."""
        if direction == config.INPUT_LEFT:
            self.state.go_back()
        elif direction == config.INPUT_UP:
            self.state.scroll_offset = max(0, self.state.scroll_offset - 20)
        elif direction == config.INPUT_DOWN:
            self.state.scroll_offset += 20

    def _handle_generate_qr(self, direction: str) -> None:
        """Handle input on QR code generation page."""
        if direction == config.INPUT_LEFT:
            self.state.go_back()
        elif direction == config.INPUT_UP:
            self.state.qr_zoom = min(200, self.state.qr_zoom + 10)
        elif direction == config.INPUT_DOWN:
            self.state.qr_zoom = max(50, self.state.qr_zoom - 10)

    def _handle_view_address(self, direction: str) -> None:
        """Handle input on view address page."""
        if direction == config.INPUT_LEFT:
            self.state.go_back()
        elif direction == config.INPUT_UP:
            self.state.scroll_offset = max(0, self.state.scroll_offset - 20)
        elif direction == config.INPUT_DOWN:
            self.state.scroll_offset += 20

    def _handle_camera_preview(self, direction: str) -> None:
        """Handle input on camera preview page."""
        if direction == config.INPUT_LEFT:
            self.state.go_back()

    def _handle_settings(self, direction: str) -> None:
        """Handle input on settings page."""
        menu_items = 4

        if direction == config.INPUT_UP:
            self.state.menu_index = (self.state.menu_index - 1) % menu_items
        elif direction == config.INPUT_DOWN:
            self.state.menu_index = (self.state.menu_index + 1) % menu_items
        elif direction == config.INPUT_LEFT:
            self.state.go_back()
        elif direction == config.INPUT_RIGHT or direction == config.INPUT_PRESS:
            # Navigate to setting
            if self.state.menu_index == 0:
                self.state.slider_value = self.state.brightness
                self.state.navigate_to(config.PAGE_BRIGHTNESS_SETTING)
            elif self.state.menu_index == 1:
                self.state.slider_value = self.state.timeout
                self.state.navigate_to(config.PAGE_TIMEOUT_SETTING)
            elif self.state.menu_index == 2:
                self.state.navigate_to(config.PAGE_LANGUAGE_SETTING)
            elif self.state.menu_index == 3:
                self.state.navigate_to(config.PAGE_RESET_SETTING)

    def _handle_brightness_setting(self, direction: str) -> None:
        """Handle input on brightness setting page."""
        if direction == config.INPUT_LEFT:
            self.state.slider_value = max(0, self.state.slider_value - 5)
            self.state.brightness = self.state.slider_value
        elif direction == config.INPUT_RIGHT:
            self.state.slider_value = min(100, self.state.slider_value + 5)
            self.state.brightness = self.state.slider_value
        elif direction == config.INPUT_PRESS:
            # Save and go back
            self.state.brightness = self.state.slider_value
            self.state.go_back()

    def _handle_timeout_setting(self, direction: str) -> None:
        """Handle input on timeout setting page."""
        if direction == config.INPUT_LEFT:
            self.state.slider_value = max(30, self.state.slider_value - 30)
            self.state.timeout = self.state.slider_value
        elif direction == config.INPUT_RIGHT:
            self.state.slider_value = min(600, self.state.slider_value + 30)
            self.state.timeout = self.state.slider_value
        elif direction == config.INPUT_PRESS:
            self.state.timeout = self.state.slider_value
            self.state.go_back()

    def _handle_language_setting(self, direction: str) -> None:
        """Handle input on language setting page."""
        languages = ['en', 'fi']
        current_index = languages.index(self.state.language)

        if direction == config.INPUT_UP:
            current_index = (current_index - 1) % len(languages)
            self.state.language = languages[current_index]
        elif direction == config.INPUT_DOWN:
            current_index = (current_index + 1) % len(languages)
            self.state.language = languages[current_index]
        elif direction == config.INPUT_PRESS:
            self.state.go_back()

    def _handle_reset_setting(self, direction: str) -> None:
        """Handle input on reset confirmation page."""
        if direction == config.INPUT_LEFT:
            self.state.menu_index = 1  # NO
        elif direction == config.INPUT_RIGHT:
            self.state.menu_index = 0  # YES
        elif direction == config.INPUT_PRESS:
            if self.state.menu_index == 0:  # YES
                # Reset to defaults
                self.state.brightness = config.UI_BRIGHTNESS
                self.state.timeout = config.UI_TIMEOUT
                self.state.language = config.UI_LANGUAGE
                logger.info("Settings reset to defaults")
            self.state.go_back()

    def _handle_about(self, direction: str) -> None:
        """Handle input on about page."""
        if direction == config.INPUT_LEFT:
            self.state.go_back()
        elif direction == config.INPUT_UP:
            self.state.scroll_offset = max(0, self.state.scroll_offset - 20)
        elif direction == config.INPUT_DOWN:
            self.state.scroll_offset += 20

    def _handle_error(self, direction: str) -> None:
        """Handle input on error page."""
        if direction == config.INPUT_UP or direction == config.INPUT_DOWN:
            self.state.menu_index = 1 - self.state.menu_index  # Toggle between 0 and 1
        elif direction == config.INPUT_PRESS:
            if self.state.menu_index == 0:  # Retry
                # Retry logic would go here
                logger.info("Retry selected")
            self.state.go_back()


# Singleton instance
_menu_system: Optional[MenuSystem] = None


def get_menu_system() -> MenuSystem:
    """
    Get singleton menu system instance.

    Returns:
        MenuSystem instance
    """
    global _menu_system
    if _menu_system is None:
        _menu_system = MenuSystem()
    return _menu_system
