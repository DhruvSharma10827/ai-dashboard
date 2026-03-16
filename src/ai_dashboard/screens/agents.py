"""Agents screen for AI Dashboard."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.containers import Horizontal
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Button
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import Static

from ai_dashboard.widgets.agent_card import AgentCard

if TYPE_CHECKING:
    from ai_dashboard.app import AIDashboardApp


class AgentsScreen(Screen):
    """Agents management screen."""

    BINDINGS: ClassVar[tuple[Binding, ...]] = (
        Binding("escape", "go_back", "Back"),
        Binding("a", "add_agent", "Add Agent"),
        Binding("r", "refresh", "Refresh"),
        Binding("1", "goto_dashboard", "Dashboard"),
        Binding("2", "goto_models", "Models"),
        Binding("3", "goto_agents", "Agents"),
        Binding("4", "goto_chat", "Chat"),
        Binding("5", "goto_tasks", "Tasks"),
        Binding("6", "goto_settings", "Settings"),
    )

    DEFAULT_CSS = """
    AgentsScreen { layout: vertical; height: 100%; }
    AgentsScreen .container { padding: 1 2; height: 1fr; }
    AgentsScreen .header { layout: horizontal; margin-bottom: 1; }
    AgentsScreen .title { text-style: bold; color: $accent; width: 1fr; }
    AgentsScreen .stats { color: $text-muted; }
    AgentsScreen .toolbar { layout: horizontal; margin-bottom: 1; }
    AgentsScreen .toolbar Button { margin-right: 1; }
    AgentsScreen .agents-grid { layout: horizontal; height: 1fr; }
    """

    @property
    def app(self) -> AIDashboardApp:
        return super().app  # type: ignore

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(classes="container"):
            # Header
            stats = self.app.agent_service.get_agent_statistics()
            with Horizontal(classes="header"):
                yield Static("🦾 Agent Orchestration", classes="title")
                yield Static(
                    f"Running: {stats['running']} | Idle: {stats['idle']} | Total: {stats['total']}",
                    classes="stats",
                )

            # Toolbar
            with Horizontal(classes="toolbar"):
                yield Button("➕ Add Agent", variant="primary", id="add-agent")
                yield Button("🔄 Refresh", id="refresh")
                yield Button("⚙️ Configure All", id="configure")

            # Agents grid
            with VerticalScroll(classes="agents-grid"):
                with Horizontal():
                    for agent in self.app.agent_service.get_all_agents():
                        yield AgentCard(agent, show_actions=True)

        yield Footer()

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_add_agent(self) -> None:
        """Add new agent action."""
        # TODO: Open modal dialog for agent creation
        pass

    def action_goto_dashboard(self) -> None:
        self.app.push_screen("dashboard")

    def action_goto_models(self) -> None:
        self.app.push_screen("models")

    def action_goto_agents(self) -> None:
        pass

    def action_goto_chat(self) -> None:
        self.app.push_screen("chat")

    def action_goto_tasks(self) -> None:
        self.app.push_screen("tasks")

    def action_goto_settings(self) -> None:
        self.app.push_screen("settings")

    def action_refresh(self) -> None:
        self.refresh()
