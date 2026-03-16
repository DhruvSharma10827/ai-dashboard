"""Model card widget for displaying AI model information."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.widgets import Button
from textual.widgets import Static

from ai_dashboard.models.ai_model import AIModel
from ai_dashboard.widgets.status_indicator import StatusIndicator

if TYPE_CHECKING:
    pass


class ModelCard(Container):
    """Widget for displaying an AI model card.

    This widget displays model information including name,
    provider, context size, and capabilities.

    Attributes:
        model: The AI model to display.

    Example:
        >>> model = AIModel(id="gpt-4", name="GPT-4", provider="openai")
        >>> card = ModelCard(model)
    """

    DEFAULT_CSS = """
    ModelCard {
        height: auto;
        min-height: 6;
        background: $surface;
        border: round $border;
        margin: 0 0 1 0;
        padding: 1;
    }
    
    ModelCard:hover {
        border: round $accent;
    }
    
    ModelCard.running {
        border: round $success;
    }
    
    ModelCard.available {
        border: round $accent;
    }
    
    ModelCard.stopped {
        border: round $error;
    }
    
    ModelCard.loading {
        border: round $warning;
    }
    
    ModelCard .model-header {
        height: auto;
        layout: horizontal;
        margin-bottom: 1;
    }
    
    ModelCard .model-name {
        text-style: bold;
        color: $text;
        width: 1fr;
        content-align: left middle;
    }
    
    ModelCard .model-status {
        width: auto;
    }
    
    ModelCard .model-body {
        height: auto;
        layout: vertical;
    }
    
    ModelCard .model-info {
        color: $text-muted;
        margin-bottom: 1;
    }
    
    ModelCard .model-caps {
        height: auto;
        layout: horizontal;
    }
    
    ModelCard .capability {
        color: $accent;
        margin-right: 2;
    }
    
    ModelCard .model-actions {
        height: auto;
        layout: horizontal;
        margin-top: 1;
    }
    
    ModelCard .model-actions Button {
        min-width: 8;
        margin: 0 1 0 0;
    }
    """

    def __init__(
        self,
        model: AIModel,
        *,
        show_actions: bool = False,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize model card.

        Args:
            model: AI model to display.
            show_actions: Whether to show action buttons.
            name: Widget name.
            id: Widget ID.
            classes: Additional CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
        self.model = model
        self.show_actions = show_actions

        # Add status class
        if model.status:
            self.add_class(model.status)

    def compose(self) -> ComposeResult:
        """Compose the model card widget."""
        # Header with name and status
        with Horizontal(classes="model-header"):
            yield Static(f"🤖 {self.model.name}", classes="model-name")
            with Container(classes="model-status"):
                yield StatusIndicator(self.model.status)

        # Body with info and capabilities
        with Vertical(classes="model-body"):
            # Model info
            info_parts = [
                f"Provider: {self.model.provider}",
                f"Context: {self.model.context_size_display}",
            ]
            yield Static("  |  ".join(info_parts), classes="model-info")

            # Capabilities
            caps = self.model.capabilities
            if caps:
                with Horizontal(classes="model-caps"):
                    for cap in caps:
                        icon = {"Vision": "👁️", "Tools": "🔧", "Streaming": "📡"}.get(cap, "✓")
                        yield Static(f"{icon} {cap}", classes="capability")

        # Actions (optional)
        if self.show_actions:
            with Horizontal(classes="model-actions"):
                yield Button("Configure", variant="primary", id="configure")
                if self.model.is_local:
                    if self.model.status == "running":
                        yield Button("Stop", variant="error", id="stop")
                    else:
                        yield Button("Start", variant="success", id="start")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        # Emit custom events that parent screens can handle
        event.stop()
