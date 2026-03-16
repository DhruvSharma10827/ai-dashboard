"""Settings screen for AI Dashboard."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static, TabbedContent, TabPane, Input, Button, Switch

if TYPE_CHECKING:
    from ai_dashboard.app import AIDashboardApp


class SettingsScreen(Screen):
    """Settings management screen."""
    
    BINDINGS: ClassVar[tuple[Binding, ...]] = (
        Binding("escape", "go_back", "Back"),
        Binding("ctrl+s", "save", "Save"),
        Binding("1", "goto_dashboard", "Dashboard"),
        Binding("2", "goto_models", "Models"),
        Binding("3", "goto_agents", "Agents"),
        Binding("4", "goto_chat", "Chat"),
        Binding("5", "goto_tasks", "Tasks"),
        Binding("6", "goto_settings", "Settings"),
    )
    
    DEFAULT_CSS = """
    SettingsScreen { layout: vertical; height: 100%; }
    SettingsScreen .container { padding: 1 2; height: 1fr; }
    SettingsScreen .setting-group { background: $panel; border: round $border; padding: 1 2; margin: 1 0; }
    SettingsScreen .setting-group-title { text-style: bold; color: $accent; margin-bottom: 1; }
    SettingsScreen .setting-row { layout: horizontal; margin: 1 0; }
    SettingsScreen .setting-label { width: 20; color: $text; }
    SettingsScreen .setting-value { width: 1fr; }
    SettingsScreen .setting-description { color: $text-muted; margin-top: 0; font-size: 0.9em; }
    SettingsScreen Input { width: 1fr; }
    """
    
    @property
    def app(self) -> "AIDashboardApp":
        return super().app  # type: ignore
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Container(classes="container"):
            with TabbedContent():
                # General Settings
                with TabPane("General"):
                    with VerticalScroll():
                        with Container(classes="setting-group"):
                            yield Static("🎨 Appearance", classes="setting-group-title")
                            
                            with Horizontal(classes="setting-row"):
                                yield Static("Theme:", classes="setting-label")
                                yield Input(value="default", placeholder="default, dark, light, dracula, nord")
                            
                            with Horizontal(classes="setting-row"):
                                yield Static("Animations:", classes="setting-label")
                                yield Switch(value=True)
                        
                        with Container(classes="setting-group"):
                            yield Static("🤖 AI Settings", classes="setting-group-title")
                            
                            with Horizontal(classes="setting-row"):
                                yield Static("Default Provider:", classes="setting-label")
                                yield Input(value=self.app.config.ai.default_provider)
                            
                            with Horizontal(classes="setting-row"):
                                yield Static("Default Model:", classes="setting-label")
                                yield Input(value=self.app.config.ai.default_model)
                
                # Security Settings
                with TabPane("Security"):
                    with VerticalScroll():
                        with Container(classes="setting-group"):
                            yield Static("🔐 Authentication", classes="setting-group-title")
                            
                            yield Button("Change Admin Password", variant="primary", id="change-password")
                            
                            with Horizontal(classes="setting-row"):
                                yield Static("Session Timeout:", classes="setting-label")
                                yield Input(value=str(self.app.config.security.session_timeout), placeholder="Minutes")
                            
                            with Horizontal(classes="setting-row"):
                                yield Static("2FA Enabled:", classes="setting-label")
                                yield Switch(value=self.app.config.security.two_factor_enabled)
                        
                        with Container(classes="setting-group"):
                            yield Static("🔒 Security Options", classes="setting-group-title")
                            
                            with Horizontal(classes="setting-row"):
                                yield Static("Max Login Attempts:", classes="setting-label")
                                yield Input(value=str(self.app.config.security.max_login_attempts))
                
                # SSH Settings
                with TabPane("SSH"):
                    with VerticalScroll():
                        with Container(classes="setting-group"):
                            yield Static("🌐 SSH Server", classes="setting-group-title")
                            
                            with Horizontal(classes="setting-row"):
                                yield Static("Enabled:", classes="setting-label")
                                yield Switch(value=self.app.config.ssh.enabled)
                            
                            with Horizontal(classes="setting-row"):
                                yield Static("Port:", classes="setting-label")
                                yield Input(value=str(self.app.config.ssh.port))
                            
                            with Horizontal(classes="setting-row"):
                                yield Static("Password Auth:", classes="setting-label")
                                yield Switch(value=self.app.config.ssh.password_auth)
                            
                            with Horizontal(classes="setting-row"):
                                yield Static("Key Auth:", classes="setting-label")
                                yield Switch(value=self.app.config.ssh.key_auth)
                
                # API Keys
                with TabPane("API Keys"):
                    with VerticalScroll():
                        with Container(classes="setting-group"):
                            yield Static("🔑 Provider API Keys", classes="setting-group-title")
                            
                            with Horizontal(classes="setting-row"):
                                yield Static("OpenAI:", classes="setting-label")
                                yield Input(password=True, placeholder="sk-...")
                            
                            with Horizontal(classes="setting-row"):
                                yield Static("Anthropic:", classes="setting-label")
                                yield Input(password=True, placeholder="sk-ant-...")
                            
                            with Horizontal(classes="setting-row"):
                                yield Static("Google:", classes="setting-label")
                                yield Input(password=True, placeholder="AIza...")
                            
                            with Horizontal(classes="setting-row"):
                                yield Static("Groq:", classes="setting-label")
                                yield Input(password=True, placeholder="gsk_...")
        
        yield Footer()
    
    def action_save(self) -> None:
        """Save settings action."""
        # TODO: Implement settings save
        pass
    
    def action_go_back(self) -> None:
        self.app.pop_screen()
    
    def action_goto_dashboard(self) -> None:
        self.app.push_screen("dashboard")
    
    def action_goto_models(self) -> None:
        self.app.push_screen("models")
    
    def action_goto_agents(self) -> None:
        self.app.push_screen("agents")
    
    def action_goto_chat(self) -> None:
        self.app.push_screen("chat")
    
    def action_goto_tasks(self) -> None:
        self.app.push_screen("tasks")
    
    def action_goto_settings(self) -> None:
        pass
