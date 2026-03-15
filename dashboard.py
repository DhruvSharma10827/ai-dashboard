#!/usr/bin/env python3
"""AI Dashboard - Enterprise AI Orchestration System.

A professional TUI for managing AI models, agents, and workflows.
"""

import ctypes
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import ClassVar

import argon2
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    ListItem,
    Static,
    TabbedContent,
    TabPane,
)

# =============================================================================
# CONFIGURATION
# =============================================================================

CONFIG_DIR = Path.home() / ".ai-dashboard"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class AIModel:
    """AI Model configuration and metadata."""

    id: str
    name: str
    provider: str
    model_type: str = "chat"
    status: str = "available"
    context_size: int = 4096
    supports_vision: bool = False
    supports_tools: bool = False


@dataclass
class Agent:
    """Agent configuration and task tracking."""

    id: str
    name: str
    role: str
    status: str = "idle"
    tasks_completed: int = 0
    model: str = ""


@dataclass
class Task:
    """Task definition and status tracking."""

    id: str
    description: str
    status: str = "pending"
    agent: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Config:
    """Application configuration settings."""

    admin_password_hash: str = ""
    encryption_key: str = ""
    ssh_enabled: bool = True
    ssh_port: int = 2222
    default_provider: str = "ollama"
    api_keys: dict[str, str] = field(default_factory=dict)

    def save(self) -> None:
        """Save configuration to disk."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(
                {
                    "admin_password_hash": self.admin_password_hash,
                    "encryption_key": self.encryption_key,
                    "ssh_enabled": self.ssh_enabled,
                    "ssh_port": self.ssh_port,
                    "default_provider": self.default_provider,
                    "api_keys": self.api_keys,
                },
                f,
                indent=2,
            )

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from disk or return defaults."""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                data = json.load(f)
                return cls(**data)
        return cls()


# =============================================================================
# STYLES
# =============================================================================

CSS = """
/* Main Layout */
Screen {
    background: $surface;
}

.title-bar {
    dock: top;
    height: 3;
    background: $primary;
    padding: 0 2;
    content-align: center middle;
}

.title-text {
    color: $text-on-primary;
    text-style: bold;
}

/* Dashboard */
.dashboard-container {
    padding: 1 2;
}

.stats-bar {
    height: 5;
    background: $panel;
    margin: 1 0;
}

.stat-box {
    width: 1fr;
    padding: 1;
    content-align: center middle;
}

.stat-value {
    text-style: bold;
    color: $accent;
}

.stat-label {
    color: $text-muted;
}

/* Cards */
.card {
    background: $panel;
    border: round $primary;
    margin: 1 0;
    padding: 1;
}

.card-header {
    text-style: bold;
    color: $primary;
    margin-bottom: 1;
}

/* Model Cards */
.model-card {
    height: auto;
    min-height: 3;
    background: $panel;
    border: round $border;
    margin: 0 1;
    padding: 1;
}

.model-card.running {
    border: round $success;
}

.model-card.stopped {
    border: round $error;
}

/* Agent Cards */
.agent-card {
    height: auto;
    min-height: 4;
    background: $panel;
    border: round $border;
    margin: 0 1;
    padding: 1;
}

.agent-card.running {
    border: round $accent;
}

.agent-card.idle {
    border: round $warning;
}

/* Task List */
.task-item {
    height: 2;
    padding: 0 1;
}

.task-item.pending {
    color: $warning;
}

.task-item.running {
    color: $accent;
    text-style: bold;
}

.task-item.completed {
    color: $success;
}

/* Sidebar */
.sidebar {
    width: 20;
    dock: left;
    background: $panel;
}

.sidebar-item {
    height: 3;
    padding: 0 1;
    content-align: left middle;
}

.sidebar-item.active {
    background: $primary;
    color: $text-on-primary;
}

/* Chat */
.chat-container {
    height: 1fr;
}

.chat-messages {
    height: 1fr;
    background: $surface-darken-1;
    padding: 1;
}

.chat-input {
    dock: bottom;
    height: 5;
    background: $panel;
}

/* Status indicators */
.status-online {
    color: $success;
}

.status-offline {
    color: $error;
}

.status-limited {
    color: $warning;
}

/* Buttons */
Button {
    margin: 0 1;
}

Button.primary {
    background: $primary;
    color: $text-on-primary;
}

Button.danger {
    background: $error;
    color: $text-on-error;
}

/* Input */
Input {
    margin: 1 0;
}

/* Tabs */
TabbedContent {
    height: 1fr;
}
"""


# =============================================================================
# WIDGETS
# =============================================================================


class StatusIndicator(Static):
    """Status indicator widget."""

    def __init__(self, status: str, **kwargs):
        super().__init__(**kwargs)
        self.status = status

    def compose(self) -> ComposeResult:
        """Generate child widgets for the status indicator."""
        icons = {
            "online": "🟢",
            "offline": "🔴",
            "limited": "🟡",
            "running": "🔵",
            "idle": "⚪",
        }
        icon = icons.get(self.status, "⚪")
        yield Static(f"{icon} {self.status.upper()}")


class ModelCard(Container):
    """AI Model card widget."""

    def __init__(self, model: AIModel, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.add_class(model.status)

    def compose(self) -> ComposeResult:
        """Generate child widgets for the model card."""
        with Horizontal(classes="model-header"):
            yield Static(f"🤖 {self.model.name}", classes="model-name")
            yield StatusIndicator(self.model.status)
        with Horizontal(classes="model-info"):
            yield Static(f"Provider: {self.model.provider}")
            yield Static(f"Context: {self.model.context_size}K")
        with Horizontal(classes="model-caps"):
            if self.model.supports_vision:
                yield Static("👁️ Vision")
            if self.model.supports_tools:
                yield Static("🔧 Tools")


class AgentCard(Container):
    """Agent card widget."""

    def __init__(self, agent: Agent, **kwargs):
        super().__init__(**kwargs)
        self.agent = agent
        self.add_class(agent.status)

    def compose(self) -> ComposeResult:
        """Generate child widgets for the agent card."""
        icons = {
            "code": "💻",
            "research": "🔍",
            "task": "📋",
            "chat": "💬",
        }
        icon = icons.get(self.agent.role, "🤖")
        with Horizontal(classes="agent-header"):
            yield Static(f"{icon} {self.agent.name}", classes="agent-name")
            yield StatusIndicator(self.agent.status)
        yield Static(f"Tasks completed: {self.agent.tasks_completed}")
        if self.agent.model:
            yield Static(f"Model: {self.agent.model}")


class TaskItem(ListItem):
    """Task list item."""

    def __init__(self, task: Task, **kwargs):
        super().__init__(**kwargs)
        self.task = task
        self.add_class(task.status)


# =============================================================================
# SCREENS
# =============================================================================


class LoginScreen(Screen):
    """Login screen for authentication."""

    CSS_PATH = None
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("enter", "login", "Login"),
        Binding("escape", "quit", "Quit"),
    ]

    def __init__(self, config: Config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self._is_setup = not config.admin_password_hash

    def compose(self) -> ComposeResult:
        """Generate child widgets for the login screen."""
        with Container(classes="login-container"):
            yield Static(
                """
╔══════════════════════════════════════════════════════════════╗
║     █████╗ ██╗    ██╗ ██████╗ ██████╗ ██╗   ██╗              ║
║    ██╔══██╗██║    ██║██╔═══██╗██╔══██╗╚██╗ ██╔╝              ║
║    ███████║██║ █╗ ██║██║   ██║██████╔╝ ╚████╔╝               ║
║    ██╔══██║██║███╗██║██║   ██║██╔══██╗  ╚██╔╝                ║
║    ██║  ██║╚███╔███╔╝╚██████╔╝██║  ██║   ██║                 ║
║    ╚═╝  ╚═╝ ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝   ╚═╝                 ║
║                                                              ║
║           Enterprise AI Dashboard v1.0.0                     ║
╚══════════════════════════════════════════════════════════════╝
""",
                classes="title-text",
            )

            if self._is_setup:
                yield Static("\n🔐 First Time Setup", classes="card-header")
                yield Static("Create an admin password:")
                yield Input(placeholder="Enter password", password=True, id="setup-password")
                yield Input(placeholder="Confirm password", password=True, id="setup-confirm")
            else:
                yield Static("\n🔐 Authentication Required", classes="card-header")
                yield Static("Enter your admin password:")
                yield Input(placeholder="Password", password=True, id="login-password")

            yield Static("", id="error-msg")
            yield Button(
                "Login" if not self._is_setup else "Setup",
                variant="primary",
                id="login-btn",
            )
            yield Footer()

    def action_login(self) -> None:
        """Handle login action."""
        self._do_login()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "login-btn":
            self._do_login()

    def _do_login(self) -> None:
        """Process the login request."""
        if self._is_setup:
            pwd = self.query_one("#setup-password", Input).value
            confirm = self.query_one("#setup-confirm", Input).value
            if not pwd:
                self.query_one("#error-msg", Static).update("❌ Password required")
                return
            if pwd != confirm:
                self.query_one("#error-msg", Static).update("❌ Passwords don't match")
                return
            ph = argon2.PasswordHasher()
            self.config.admin_password_hash = ph.hash(pwd)
            self.config.save()
            self.app.push_screen("dashboard")
        else:
            pwd = self.query_one("#login-password", Input).value
            ph = argon2.PasswordHasher()
            try:
                ph.verify(self.config.admin_password_hash, pwd)
                self.app.push_screen("dashboard")
            except argon2.exceptions.VerifyMismatchError:
                self.query_one("#error-msg", Static).update("❌ Invalid password")


class DashboardScreen(Screen):
    """Main dashboard screen."""

    CSS_PATH = None
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("1", "show_dashboard", "Dashboard"),
        Binding("2", "show_models", "Models"),
        Binding("3", "show_agents", "Agents"),
        Binding("4", "show_chat", "Chat"),
        Binding("5", "show_tasks", "Tasks"),
        Binding("6", "show_settings", "Settings"),
        Binding("q", "quit", "Quit"),
        Binding("?", "help", "Help"),
    ]

    def compose(self) -> ComposeResult:
        """Generate child widgets for the dashboard screen."""
        yield Header()

        with Container(classes="dashboard-container"):
            # Stats bar
            with Horizontal(classes="stats-bar"):
                with Container(classes="stat-box"):
                    yield Static("5", classes="stat-value")
                    yield Static("Models", classes="stat-label")
                with Container(classes="stat-box"):
                    yield Static("4", classes="stat-value")
                    yield Static("Agents", classes="stat-label")
                with Container(classes="stat-box"):
                    yield Static("0", classes="stat-value")
                    yield Static("Running", classes="stat-label")
                with Container(classes="stat-box"):
                    yield Static("0", classes="stat-value")
                    yield Static("Tasks", classes="stat-label")

            # Main content
            with Horizontal():
                # Left panel - Models
                with Container(classes="card", id="models-panel"):
                    yield Static("🤖 AI MODELS", classes="card-header")
                    with VerticalScroll():
                        for model in self.app.models[:5]:
                            yield ModelCard(model)

                # Right panel - Agents
                with Container(classes="card", id="agents-panel"):
                    yield Static("🤖 AGENTS", classes="card-header")
                    with VerticalScroll():
                        for agent in self.app.agents:
                            yield AgentCard(agent)

            # System status
            with Container(classes="card"):
                yield Static("📊 SYSTEM STATUS", classes="card-header")
                with Horizontal():
                    yield Static("CPU: ████████░░ 78%")
                    yield Static("MEM: ██████░░░░ 62%")
                    yield Static("GPU: ███████░░░ 45%")
                yield Static("SSH: 🟢 Port 2222 | MCP: 🟢 Running | Cache: 256MB")

        yield Footer()

    def action_show_dashboard(self) -> None:
        """Navigate to dashboard screen."""
        self.app.push_screen("dashboard")

    def action_show_models(self) -> None:
        """Navigate to models screen."""
        self.app.push_screen("models")

    def action_show_agents(self) -> None:
        """Navigate to agents screen."""
        self.app.push_screen("agents")

    def action_show_chat(self) -> None:
        """Navigate to chat screen."""
        self.app.push_screen("chat")

    def action_show_tasks(self) -> None:
        """Navigate to tasks screen."""
        self.app.push_screen("tasks")

    def action_show_settings(self) -> None:
        """Navigate to settings screen."""
        self.app.push_screen("settings")


class ModelsScreen(Screen):
    """AI Models management screen."""

    CSS_PATH = None
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("escape", "back", "Back"),
        Binding("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        """Generate child widgets for the models screen."""
        yield Header()

        with TabbedContent():
            with TabPane("Local Models"):
                with Container(classes="card"):
                    yield Static("🟢 Ollama (Running)", classes="card-header")
                    yield Static("Host: localhost:11434 | Models: 3 | GPU: Enabled")
                    with Horizontal():
                        yield Button("Start", variant="primary")
                        yield Button("Stop", variant="error")
                        yield Button("Pull Model")

                with Container(classes="card"):
                    yield Static("⚪ Llama.cpp (Stopped)", classes="card-header")
                    yield Static("GPU Layers: 35 | Context: 4096 | Threads: 4")
                    with Horizontal():
                        yield Button("Start", variant="primary")
                        yield Button("Configure")

            with TabPane("Cloud Providers"):
                with Container(classes="card"):
                    yield Static("🟢 OpenAI", classes="card-header")
                    yield Static("Model: gpt-4-turbo | API Key: ✓ Set | Usage: $1.20")
                    yield Button("Configure", variant="primary")

                with Container(classes="card"):
                    yield Static("🟢 Claude (Anthropic)", classes="card-header")
                    yield Static("Model: claude-3-opus | API Key: ✓ Set | Usage: $0.45")
                    yield Button("Configure", variant="primary")

                with Container(classes="card"):
                    yield Static("🟢 Gemini (Google)", classes="card-header")
                    yield Static("Model: gemini-pro | API Key: ✓ Set | Usage: $0.10")
                    yield Button("Configure", variant="primary")

        yield Footer()

    def action_back(self) -> None:
        """Navigate back to previous screen."""
        self.app.pop_screen()


class AgentsScreen(Screen):
    """Agents management screen."""

    CSS_PATH = None
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("escape", "back", "Back"),
        Binding("a", "add_agent", "Add Agent"),
    ]

    def compose(self) -> ComposeResult:
        """Generate child widgets for the agents screen."""
        yield Header()

        with Container(classes="dashboard-container"):
            yield Static("🤖 AGENT ORCHESTRATION", classes="card-header")
            yield Static("Active: 2 | Pending: 8 | Completed Today: 15")

            with Horizontal():
                for agent in self.app.agents:
                    yield AgentCard(agent)

        yield Footer()

    def action_back(self) -> None:
        """Navigate back to previous screen."""
        self.app.pop_screen()


class ChatScreen(Screen):
    """Chat interface screen."""

    CSS_PATH = None
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("escape", "back", "Back"),
        Binding("enter", "send", "Send"),
    ]

    messages = reactive([])

    def compose(self) -> ComposeResult:
        """Generate child widgets for the chat screen."""
        yield Header()

        with Container(classes="chat-container"):
            yield Static("💬 Chat Interface", classes="card-header")
            yield Static("Model: Claude 3 Opus | Context: 8K / 200K", id="chat-info")

            with VerticalScroll(classes="chat-messages", id="messages"):
                yield Static("Welcome to AI Dashboard Chat!")
                yield Static("Type a message below to start.")

            with Horizontal(classes="chat-input"):
                yield Input(placeholder="Type your message...", id="chat-input")
                yield Button("Send", variant="primary", id="send-btn")

        yield Footer()

    def action_back(self) -> None:
        """Navigate back to previous screen."""
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "send-btn":
            self._send_message()

    def action_send(self) -> None:
        """Handle send action."""
        self._send_message()

    def _send_message(self) -> None:
        """Process and send the chat message."""
        inp = self.query_one("#chat-input", Input)
        msg = inp.value
        if msg:
            container = self.query_one("#messages", VerticalScroll)
            container.mount(Static(f"👤 You: {msg}"))
            container.mount(Static("🤖 AI: Processing..."))
            inp.value = ""


class TasksScreen(Screen):
    """Tasks management screen."""

    CSS_PATH = None
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("escape", "back", "Back"),
        Binding("n", "new_task", "New Task"),
    ]

    def compose(self) -> ComposeResult:
        """Generate child widgets for the tasks screen."""
        yield Header()

        with Container(classes="dashboard-container"):
            yield Static("📋 TASK MANAGEMENT", classes="card-header")
            with Horizontal():
                yield Button("New Task", variant="primary")
                yield Button("Schedule")
                yield Button("Templates")
                yield Button("History")

            with Container(classes="card"):
                yield Static("Running Tasks", classes="card-header")
                yield Static("No running tasks")

            with Container(classes="card"):
                yield Static("Pending Tasks", classes="card-header")
                yield Static("No pending tasks")

            with Container(classes="card"):
                yield Static("Completed Today", classes="card-header")
                yield Static("No completed tasks")

        yield Footer()

    def action_back(self) -> None:
        """Navigate back to previous screen."""
        self.app.pop_screen()


class SettingsScreen(Screen):
    """Settings screen."""

    CSS_PATH = None
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("escape", "back", "Back"),
        Binding("s", "save", "Save"),
    ]

    def compose(self) -> ComposeResult:
        """Generate child widgets for the settings screen."""
        yield Header()

        with TabbedContent():
            with TabPane("General"):
                with Container(classes="card"):
                    yield Static("App Name:")
                    yield Input(value="AI Dashboard")
                    yield Static("Log Level:")
                    yield Input(value="info")

            with TabPane("Security"):
                with Container(classes="card"):
                    yield Button("Change Admin Password", variant="primary")
                    yield Static("Session Timeout: 30 minutes")
                    yield Static("2FA: Disabled")

            with TabPane("SSH"):
                with Container(classes="card"):
                    yield Static("SSH Port:")
                    yield Input(value="2222")
                    yield Static("Password Auth: Enabled")
                    yield Static("Key Auth: Enabled")

            with TabPane("API Keys"):
                with Container(classes="card"):
                    yield Static("OpenAI API Key:")
                    yield Input(value="sk-...", password=True)
                    yield Static("Anthropic API Key:")
                    yield Input(value="sk-ant-...", password=True)

        yield Footer()

    def action_back(self) -> None:
        """Navigate back to previous screen."""
        self.app.pop_screen()


# =============================================================================
# MAIN APP
# =============================================================================


class AIDashboardApp(App):
    """AI Dashboard TUI Application."""

    CSS = CSS
    TITLE = "AI Dashboard"
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("q", "quit", "Quit", show=False),
    ]

    SCREENS: ClassVar[dict[str, type[Screen]]] = {
        "login": LoginScreen,
        "dashboard": DashboardScreen,
        "models": ModelsScreen,
        "agents": AgentsScreen,
        "chat": ChatScreen,
        "tasks": TasksScreen,
        "settings": SettingsScreen,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = Config.load()

        # Initialize data
        self.models = [
            AIModel("ollama-llama3.2", "Llama 3.2", "ollama", "chat", "running", 128000),
            AIModel("ollama-mistral", "Mistral", "ollama", "chat", "running", 32000),
            AIModel("ollama-codellama", "CodeLlama", "ollama", "chat", "available", 16384),
            AIModel(
                "openai-gpt4",
                "GPT-4 Turbo",
                "openai",
                "chat",
                "available",
                128000,
                True,
                True,
            ),
            AIModel(
                "claude-opus",
                "Claude 3 Opus",
                "claude",
                "chat",
                "available",
                200000,
                True,
                True,
            ),
        ]

        self.agents = [
            Agent("code", "Code Agent", "code", "idle", 12, "codellama"),
            Agent("research", "Research Agent", "research", "running", 3, "llama3.2"),
            Agent("task", "Task Agent", "task", "idle", 5, "llama3.2"),
            Agent("chat", "Chat Agent", "chat", "running", 8, "claude-3-opus"),
        ]

        self.tasks: list[Task] = []

    def on_mount(self) -> None:
        """Handle app mount event."""
        if not self.config.admin_password_hash:
            self.push_screen("login")
        else:
            self.push_screen("login")


# =============================================================================
# ENTRY POINT
# =============================================================================


def fix_windows_console() -> None:
    """Fix Windows console for Textual TUI applications.

    When running from PyInstaller or certain contexts on Windows,
    sys.stdin/stdout/stderr may be None, causing Textual's Windows
    driver to fail. This function reassigns them to proper console
    handles.
    """
    if sys.platform != "win32":
        return

    # Check if we need to fix the console
    if sys.stdin is None or sys.stdout is None or sys.stderr is None:
        try:
            kernel32 = ctypes.windll.kernel32

            # Get standard handles
            stdin_handle = kernel32.GetStdHandle(-10)  # STD_INPUT_HANDLE
            stdout_handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            stderr_handle = kernel32.GetStdHandle(-12)  # STD_ERROR_HANDLE

            # Open console handles if needed
            # Note: These handles must persist for app lifetime, no context manager
            if sys.stdin is None and stdin_handle:
                sys.stdin = open("CONIN$", encoding="utf-8", newline="")  # noqa: SIM115
            if sys.stdout is None and stdout_handle:
                sys.stdout = open("CONOUT$", "w", encoding="utf-8", newline="")  # noqa: SIM115
            if sys.stderr is None and stderr_handle:
                sys.stderr = open("CONOUT$", "w", encoding="utf-8", newline="")  # noqa: SIM115

        except (OSError, AttributeError):
            # If we can't fix the console, try to open a new console window
            try:
                ctypes.windll.kernel32.AllocConsole()
                # Note: These handles must persist for app lifetime, no context manager
                sys.stdin = open("CONIN$", encoding="utf-8", newline="")  # noqa: SIM115
                sys.stdout = open("CONOUT$", "w", encoding="utf-8", newline="")  # noqa: SIM115
                sys.stderr = open("CONOUT$", "w", encoding="utf-8", newline="")  # noqa: SIM115
            except (OSError, AttributeError):
                print("Error: Unable to initialize console. Please run from a terminal.")
                sys.exit(1)


def main() -> None:
    """Main entry point for the AI Dashboard application."""
    # Fix Windows console issues before running the app
    fix_windows_console()

    app = AIDashboardApp()
    app.run()


if __name__ == "__main__":
    main()
