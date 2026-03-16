#!/usr/bin/env python3
"""AI Dashboard - Enterprise AI Orchestration System.

A professional, production-grade TUI for managing AI models, agents, and workflows.

Example:
    >>> from ai_dashboard.app import AIDashboardApp
    >>> app = AIDashboardApp()
    >>> app.run()
"""

from __future__ import annotations

import ctypes
import sys
from typing import Any, ClassVar

from textual.app import App
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header

from ai_dashboard.core.config import Config, get_config
from ai_dashboard.core.logging import initialize_logging, get_logger
from ai_dashboard.services.auth import AuthService
from ai_dashboard.services.model_service import ModelService
from ai_dashboard.services.agent_service import AgentService
from ai_dashboard.services.task_service import TaskService
from ai_dashboard.services.storage import StorageService
from ai_dashboard.screens.login import LoginScreen
from ai_dashboard.screens.dashboard import DashboardScreen
from ai_dashboard.screens.models import ModelsScreen
from ai_dashboard.screens.agents import AgentsScreen
from ai_dashboard.screens.chat import ChatScreen
from ai_dashboard.screens.tasks import TasksScreen
from ai_dashboard.screens.settings import SettingsScreen
from ai_dashboard.styles.theme import get_theme_css, ThemeName

logger = get_logger(__name__)


class AIDashboardApp(App):
    """AI Dashboard TUI Application.
    
    This is the main application class that orchestrates all
    screens, services, and widgets.
    
    Attributes:
        TITLE: Application title.
        BINDINGS: Global keyboard bindings.
        SCREENS: Available screens.
        config: Application configuration.
        auth_service: Authentication service.
        model_service: Model management service.
        agent_service: Agent management service.
        task_service: Task management service.
        storage_service: Storage service.
    
    Example:
        >>> app = AIDashboardApp()
        >>> app.run()
    """
    
    TITLE = "AI Dashboard - Enterprise Edition"
    
    BINDINGS: ClassVar[tuple[Binding, ...]] = (
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("f1", "help", "Help"),
        Binding("f5", "refresh", "Refresh"),
    )
    
    SCREENS: ClassVar[dict[str, type]] = {
        "login": LoginScreen,
        "dashboard": DashboardScreen,
        "models": ModelsScreen,
        "agents": AgentsScreen,
        "chat": ChatScreen,
        "tasks": TasksScreen,
        "settings": SettingsScreen,
    }
    
    CSS = get_theme_css("default")
    
    def __init__(
        self,
        config: Config | None = None,
        theme: ThemeName = "default",
        **kwargs: Any,
    ) -> None:
        """Initialize the AI Dashboard application.
        
        Args:
            config: Optional configuration override.
            theme: UI theme name.
            **kwargs: Additional arguments passed to App.
        """
        # Initialize logging
        initialize_logging()
        
        # Set theme CSS
        self.CSS = get_theme_css(theme)
        
        super().__init__(**kwargs)
        
        # Configuration
        self.config = config or get_config()
        
        # Initialize services
        self.auth_service = AuthService(self.config)
        self.model_service = ModelService()
        self.agent_service = AgentService()
        self.task_service = TaskService()
        self.storage_service = StorageService()
        
        logger.info("AI Dashboard initialized")
    
    def on_mount(self) -> None:
        """Handle application mount event."""
        logger.info("Application mounted, showing login screen")
        self.push_screen("login")
    
    def action_refresh(self) -> None:
        """Refresh the current screen."""
        self.refresh()
        logger.debug("Screen refreshed")
    
    def action_help(self) -> None:
        """Show help."""
        # TODO: Implement help screen
        self.notify("Press 1-6 to navigate between screens, ESC to go back", title="Help")
    
    def run(self) -> None:
        """Run the application with platform fixes."""
        # Fix Windows console issues
        self._fix_windows_console()
        
        logger.info("Starting AI Dashboard application")
        super().run()
    
    def _fix_windows_console(self) -> None:
        """Fix Windows console for TUI applications."""
        if sys.platform != "win32":
            return
        
        is_frozen = getattr(sys, "frozen", False)
        needs_console = (
            is_frozen
            or sys.stdin is None
            or sys.stdout is None
            or sys.stderr is None
        )
        
        if not needs_console:
            return
        
        try:
            kernel32 = ctypes.windll.kernel32
            
            if is_frozen:
                kernel32.FreeConsole()
                kernel32.AllocConsole()
            
            sys.stdin = open("CONIN$", encoding="utf-8", newline="")  # type: ignore
            sys.stdout = open("CONOUT$", "w", encoding="utf-8", newline="")  # type: ignore
            sys.stderr = open("CONOUT$", "w", encoding="utf-8", newline="")  # type: ignore
            
        except (OSError, AttributeError):
            print("Error: Unable to initialize console. Please run from a terminal.")
            sys.exit(1)


def main() -> None:
    """Main entry point for AI Dashboard."""
    app = AIDashboardApp()
    app.run()


if __name__ == "__main__":
    main()
