"""Chat screen for AI Dashboard."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.containers import Horizontal
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import Input
from textual.widgets import Static

if TYPE_CHECKING:
    from ai_dashboard.app import AIDashboardApp


class ChatScreen(Screen):
    """Chat interface screen."""

    BINDINGS: ClassVar[tuple[Binding, ...]] = (
        Binding("escape", "go_back", "Back"),
        Binding("enter", "send_message", "Send"),
        Binding("ctrl+l", "clear_chat", "Clear"),
        Binding("1", "goto_dashboard", "Dashboard"),
        Binding("2", "goto_models", "Models"),
        Binding("3", "goto_agents", "Agents"),
        Binding("4", "goto_chat", "Chat"),
        Binding("5", "goto_tasks", "Tasks"),
        Binding("6", "goto_settings", "Settings"),
    )

    DEFAULT_CSS = """
    ChatScreen { layout: vertical; height: 100%; }
    ChatScreen .chat-container { padding: 1 2; height: 1fr; layout: vertical; }
    ChatScreen .chat-header { background: $panel; padding: 1; margin-bottom: 1; }
    ChatScreen .chat-title { text-style: bold; color: $accent; }
    ChatScreen .chat-info { color: $text-muted; }
    ChatScreen .messages-container { height: 1fr; background: $surface; border: round $border; padding: 1; margin-bottom: 1; }
    ChatScreen .message-user { color: $accent; margin: 1 0; }
    ChatScreen .message-assistant { color: $text; margin: 1 0; }
    ChatScreen .message-system { color: $text-muted; margin: 1 0; font-style: italic; }
    ChatScreen .input-container { layout: horizontal; height: auto; }
    ChatScreen .input-container Input { width: 1fr; margin-right: 1; }
    """

    messages: reactive[list[tuple[str, str]]] = reactive([])

    @property
    def app(self) -> AIDashboardApp:
        return super().app  # type: ignore

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(classes="chat-container"):
            # Chat header
            with Container(classes="chat-header"):
                yield Static("💬 Chat Interface", classes="chat-title")
                yield Static("Model: Claude 3 Opus | Context: 8K / 200K", classes="chat-info")

            # Messages
            with VerticalScroll(classes="messages-container", id="messages"):
                yield Static("Welcome to AI Dashboard Chat!", classes="message-system")
                yield Static("Type a message below to start.", classes="message-system")

            # Input area
            with Horizontal(classes="input-container"):
                yield Input(placeholder="Type your message...", id="chat-input")
                yield Button("Send", variant="primary", id="send-btn")

        yield Footer()

    def action_send_message(self) -> None:
        """Send message from keyboard."""
        self._send_message()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "send-btn":
            event.stop()
            self._send_message()

    def _send_message(self) -> None:
        """Send the chat message."""
        input_widget = self.query_one("#chat-input", Input)
        message = input_widget.value.strip()

        if not message:
            return

        messages_container = self.query_one("#messages", VerticalScroll)

        # Add user message
        messages_container.mount(Static(f"👤 You: {message}", classes="message-user"))

        # Simulate AI response (TODO: integrate with actual AI)
        messages_container.mount(Static("🤖 AI: Processing...", classes="message-assistant"))

        input_widget.value = ""

        # Scroll to bottom
        messages_container.scroll_end()

    def action_clear_chat(self) -> None:
        """Clear chat messages."""
        messages_container = self.query_one("#messages", VerticalScroll)
        for child in list(messages_container.children):
            child.remove()

        messages_container.mount(Static("Chat cleared.", classes="message-system"))

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_goto_dashboard(self) -> None:
        self.app.push_screen("dashboard")

    def action_goto_models(self) -> None:
        self.app.push_screen("models")

    def action_goto_agents(self) -> None:
        self.app.push_screen("agents")

    def action_goto_chat(self) -> None:
        pass

    def action_goto_tasks(self) -> None:
        self.app.push_screen("tasks")

    def action_goto_settings(self) -> None:
        self.app.push_screen("settings")
