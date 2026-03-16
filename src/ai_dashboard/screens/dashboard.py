"""Dashboard screen for AI Dashboard."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.containers import Horizontal
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import Static

from ai_dashboard.widgets.agent_card import AgentCard
from ai_dashboard.widgets.model_card import ModelCard
from ai_dashboard.widgets.stat_box import StatBox

if TYPE_CHECKING:
    from ai_dashboard.app import AIDashboardApp


class DashboardScreen(Screen):
    """Main dashboard screen.

    This screen displays:
    - Statistics overview
    - Model cards
    - Agent cards
    - System status

    Attributes:
        BINDINGS: Keyboard bindings for navigation.
    """

    BINDINGS: ClassVar[tuple[Binding, ...]] = (
        Binding("1", "goto_dashboard", "Dashboard"),
        Binding("2", "goto_models", "Models"),
        Binding("3", "goto_agents", "Agents"),
        Binding("4", "goto_chat", "Chat"),
        Binding("5", "goto_tasks", "Tasks"),
        Binding("6", "goto_settings", "Settings"),
        Binding("r", "refresh", "Refresh"),
        Binding("q", "quit", "Quit"),
    )

    DEFAULT_CSS = """
    DashboardScreen {
        layout: vertical;
        height: 100%;
    }
    
    DashboardScreen .dashboard-container {
        padding: 1 2;
        height: 1fr;
        overflow-y: scroll;
    }
    
    DashboardScreen .stats-row {
        layout: horizontal;
        height: auto;
        margin-bottom: 1;
    }
    
    DashboardScreen .stats-row StatBox {
        margin: 0 1;
    }
    
    DashboardScreen .content-row {
        layout: horizontal;
        height: 1fr;
    }
    
    DashboardScreen .panel {
        width: 1fr;
        height: 100%;
        background: $panel;
        border: round $border;
        margin: 0 1;
        padding: 1;
    }
    
    DashboardScreen .panel-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        padding: 0 1;
    }
    
    DashboardScreen .status-bar {
        layout: horizontal;
        background: $panel;
        border: round $border;
        padding: 1;
        margin: 1 2;
    }
    
    DashboardScreen .status-item {
        color: $text;
        margin: 0 2;
    }
    """

    @property
    def app(self) -> AIDashboardApp:
        """Get the app instance."""
        return super().app  # type: ignore

    def compose(self) -> ComposeResult:
        """Compose the dashboard screen."""
        yield Header()

        with Container(classes="dashboard-container"):
            # Statistics row
            with Horizontal(classes="stats-row"):
                yield StatBox(
                    str(len(self.app.model_service.get_all_models())),
                    "Models",
                    icon="🤖",
                )
                yield StatBox(
                    str(len(self.app.agent_service.get_all_agents())),
                    "Agents",
                    icon="🦾",
                )
                yield StatBox(
                    str(self.app.agent_service.get_running_agent_count()),
                    "Running",
                    icon="▶️",
                    trend="up",
                )
                yield StatBox(
                    str(self.app.task_service.get_task_count()),
                    "Tasks",
                    icon="📋",
                )

            # Main content
            with Horizontal(classes="content-row"):
                # Models panel
                with Container(classes="panel"):
                    yield Static("🤖 AI Models", classes="panel-title")
                    with VerticalScroll():
                        for model in self.app.model_service.get_all_models()[:5]:
                            yield ModelCard(model)

                # Agents panel
                with Container(classes="panel"):
                    yield Static("🦾 Agents", classes="panel-title")
                    with VerticalScroll():
                        for agent in self.app.agent_service.get_all_agents():
                            yield AgentCard(agent)

            # System status
            with Horizontal(classes="status-bar"):
                yield Static("📊 System Status:", classes="status-item")
                yield Static("CPU: ████████░░ 78%", classes="status-item")
                yield Static("MEM: ██████░░░░ 62%", classes="status-item")
                yield Static("GPU: ███████░░░ 45%", classes="status-item")

        yield Footer()

    def action_goto_dashboard(self) -> None:
        """Navigate to dashboard."""
        pass  # Already on dashboard

    def action_goto_models(self) -> None:
        """Navigate to models screen."""
        self.app.push_screen("models")

    def action_goto_agents(self) -> None:
        """Navigate to agents screen."""
        self.app.push_screen("agents")

    def action_goto_chat(self) -> None:
        """Navigate to chat screen."""
        self.app.push_screen("chat")

    def action_goto_tasks(self) -> None:
        """Navigate to tasks screen."""
        self.app.push_screen("tasks")

    def action_goto_settings(self) -> None:
        """Navigate to settings screen."""
        self.app.push_screen("settings")

    def action_refresh(self) -> None:
        """Refresh the dashboard."""
        self.refresh()
