"""Models screen for AI Dashboard."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static, TabbedContent, TabPane

from ai_dashboard.widgets.model_card import ModelCard

if TYPE_CHECKING:
    from ai_dashboard.app import AIDashboardApp


class ModelsScreen(Screen):
    """AI Models management screen."""
    
    BINDINGS: ClassVar[tuple[Binding, ...]] = (
        Binding("escape", "go_back", "Back"),
        Binding("r", "refresh", "Refresh"),
        Binding("1", "goto_dashboard", "Dashboard"),
        Binding("2", "goto_models", "Models"),
        Binding("3", "goto_agents", "Agents"),
        Binding("4", "goto_chat", "Chat"),
        Binding("5", "goto_tasks", "Tasks"),
        Binding("6", "goto_settings", "Settings"),
    )
    
    DEFAULT_CSS = """
    ModelsScreen { layout: vertical; height: 100%; }
    ModelsScreen .container { padding: 1 2; height: 1fr; }
    ModelsScreen .section { margin: 1 0; }
    ModelsScreen .section-title { text-style: bold; color: $accent; margin-bottom: 1; }
    """
    
    @property
    def app(self) -> "AIDashboardApp":
        return super().app  # type: ignore
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(classes="container"):
            with TabbedContent():
                with TabPane("Local Models"):
                    with VerticalScroll():
                        for model in self.app.model_service.get_models_by_provider("ollama"):
                            yield ModelCard(model, show_actions=True)
                with TabPane("Cloud Providers"):
                    with VerticalScroll():
                        for model in self.app.model_service.get_all_models():
                            if not model.is_local:
                                yield ModelCard(model, show_actions=True)
        yield Footer()
    
    def action_go_back(self) -> None:
        self.app.pop_screen()
    
    def action_goto_dashboard(self) -> None:
        self.app.push_screen("dashboard")
    
    def action_goto_models(self) -> None:
        pass
    
    def action_goto_agents(self) -> None:
        self.app.push_screen("agents")
    
    def action_goto_chat(self) -> None:
        self.app.push_screen("chat")
    
    def action_goto_tasks(self) -> None:
        self.app.push_screen("tasks")
    
    def action_goto_settings(self) -> None:
        self.app.push_screen("settings")
    
    def action_refresh(self) -> None:
        self.refresh()
