"""Login screen for AI Dashboard."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static

from ai_dashboard.core.logging import get_logger

if TYPE_CHECKING:
    from ai_dashboard.app import AIDashboardApp

logger = get_logger(__name__)


class LoginScreen(Screen):
    """Login screen for authentication.
    
    This screen handles:
    - First-time setup (password creation)
    - User authentication
    - Error display
    
    Attributes:
        BINDINGS: Keyboard bindings.
    """
    
    BINDINGS: ClassVar[tuple[Binding, ...]] = (
        Binding("enter", "login", "Login"),
        Binding("escape", "quit", "Quit"),
    )
    
    DEFAULT_CSS = """
    LoginScreen {
        align: center middle;
    }
    
    LoginScreen .login-container {
        width: 70;
        max-width: 80;
        padding: 2 4;
        background: $panel;
        border: thick $primary;
    }
    
    LoginScreen .login-title {
        color: $accent;
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
        width: 100%;
    }
    
    LoginScreen .login-section {
        color: $accent;
        text-style: bold;
        margin: 1 0;
        text-align: center;
    }
    
    LoginScreen .login-instruction {
        color: $text;
        margin: 1 0;
        text-align: center;
    }
    
    LoginScreen .login-error {
        color: $error;
        text-style: bold;
        margin: 1 0;
        text-align: center;
    }
    
    LoginScreen Input {
        margin: 1 0;
        width: 100%;
    }
    
    LoginScreen Button {
        width: 100%;
        margin-top: 1;
    }
    """
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize login screen."""
        super().__init__(**kwargs)
        self._is_setup: bool = False
    
    @property
    def app(self) -> "AIDashboardApp":
        """Get the app instance."""
        return super().app  # type: ignore
    
    def on_mount(self) -> None:
        """Handle screen mount event."""
        self._is_setup = not self.app.config.admin_password_hash
    
    def compose(self) -> ComposeResult:
        """Compose the login screen."""
        yield Header(show_clock=False)
        
        with Center():
            with Container(classes="login-container"):
                # ASCII Art Title
                yield Static(
                    "╔══════════════════════════════════════════════════════════════╗\n"
                    "║     █████╗ ██╗    ██╗ ██████╗ ██████╗ ██╗   ██╗              ║\n"
                    "║    ██╔══██╗██║    ██║██╔═══██╗██╔══██╗╚██╗ ██╔╝              ║\n"
                    "║    ███████║██║ █╗ ██║██║   ██║██████╔╝ ╚████╔╝               ║\n"
                    "║    ██╔══██║██║███╗██║██║   ██║██╔══██╗  ╚██╔╝                ║\n"
                    "║    ██║  ██║╚███╔███╔╝╚██████╔╝██║  ██║   ██║                 ║\n"
                    "║    ╚═╝  ╚═╝ ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝   ╚═╝                 ║\n"
                    "║                                                              ║\n"
                    "║           Enterprise AI Dashboard v1.0.0                     ║\n"
                    "╚══════════════════════════════════════════════════════════════╝",
                    classes="login-title",
                )
                
                # Section title
                if self._is_setup:
                    yield Static("🔐 First Time Setup", classes="login-section")
                    yield Static("Create an admin password:", classes="login-instruction")
                    yield Input(
                        placeholder="Enter password",
                        password=True,
                        id="setup-password",
                    )
                    yield Input(
                        placeholder="Confirm password",
                        password=True,
                        id="setup-confirm",
                    )
                else:
                    yield Static("🔐 Authentication Required", classes="login-section")
                    yield Static("Enter your admin password:", classes="login-instruction")
                    yield Input(
                        placeholder="Password",
                        password=True,
                        id="login-password",
                    )
                
                yield Static("", id="error-msg", classes="login-error")
                yield Button(
                    "Login" if not self._is_setup else "Setup",
                    variant="primary",
                    id="login-btn",
                )
        
        yield Footer()
    
    def action_login(self) -> None:
        """Handle login action from keyboard."""
        self._do_login()
    
    @on(Button.Pressed, "#login-btn")
    def on_login_button(self, event: Button.Pressed) -> None:
        """Handle login button press."""
        event.stop()
        self._do_login()
    
    def _do_login(self) -> None:
        """Process the login request."""
        error_msg = self.query_one("#error-msg", Static)
        error_msg.update("")
        
        try:
            if self._is_setup:
                self._handle_setup()
            else:
                self._handle_login()
        except Exception as e:
            error_msg.update(f"❌ {str(e)}")
            logger.error(f"Login error: {e}")
    
    def _handle_setup(self) -> None:
        """Handle first-time setup."""
        pwd = self.query_one("#setup-password", Input).value
        confirm = self.query_one("#setup-confirm", Input).value
        
        if not pwd:
            raise ValueError("Password required")
        if len(pwd) < 8:
            raise ValueError("Password must be at least 8 characters")
        if pwd != confirm:
            raise ValueError("Passwords don't match")
        
        self.app.auth_service.setup_admin(pwd)
        self.app.push_screen("dashboard")
        logger.info("Admin account set up successfully")
    
    def _handle_login(self) -> None:
        """Handle regular login."""
        pwd = self.query_one("#login-password", Input).value
        
        if not pwd:
            raise ValueError("Password required")
        
        self.app.auth_service.authenticate(pwd)
        self.app.push_screen("dashboard")
        logger.info("User authenticated successfully")
