"""Agent card widget for displaying agent information."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Static

from ai_dashboard.models.agent import Agent
from ai_dashboard.widgets.status_indicator import StatusIndicator

if TYPE_CHECKING:
    pass


class AgentCard(Container):
    """Widget for displaying an agent card.
    
    This widget displays agent information including name,
    role, status, and task statistics.
    
    Attributes:
        agent: The agent to display.
    
    Example:
        >>> agent = Agent(id="code-1", name="Code Agent", role="code")
        >>> card = AgentCard(agent)
    """
    
    # Role icons mapping
    ROLE_ICONS: dict[str, str] = {
        "code": "💻",
        "research": "🔍",
        "task": "📋",
        "chat": "💬",
        "data": "📊",
        "testing": "🧪",
    }
    
    DEFAULT_CSS = """
    AgentCard {
        height: auto;
        min-height: 7;
        background: $surface;
        border: round $border;
        margin: 0 1 1 0;
        padding: 1;
        width: 1fr;
    }
    
    AgentCard:hover {
        border: round $accent;
    }
    
    AgentCard.running {
        border: round $success;
    }
    
    AgentCard.idle {
        border: round $warning;
    }
    
    AgentCard.paused {
        border: round $accent;
    }
    
    AgentCard.error {
        border: round $error;
    }
    
    AgentCard .agent-header {
        height: auto;
        layout: horizontal;
        margin-bottom: 1;
    }
    
    AgentCard .agent-icon {
        width: 3;
        content-align: center middle;
        color: $accent;
    }
    
    AgentCard .agent-name-container {
        width: 1fr;
    }
    
    AgentCard .agent-name {
        text-style: bold;
        color: $text;
    }
    
    AgentCard .agent-role {
        color: $text-muted;
        font-size: 0.9em;
    }
    
    AgentCard .agent-status {
        width: auto;
    }
    
    AgentCard .agent-stats {
        height: auto;
        layout: horizontal;
        margin-bottom: 1;
    }
    
    AgentCard .stat {
        width: 1fr;
        text-align: center;
    }
    
    AgentCard .stat-value {
        text-style: bold;
        color: $accent;
    }
    
    AgentCard .stat-label {
        color: $text-muted;
        font-size: 0.8em;
    }
    
    AgentCard .agent-model {
        color: $text-muted;
        margin-bottom: 1;
    }
    
    AgentCard .agent-actions {
        height: auto;
        layout: horizontal;
        margin-top: 1;
    }
    
    AgentCard .agent-actions Button {
        min-width: 8;
        margin: 0 1 0 0;
    }
    """
    
    def __init__(
        self,
        agent: Agent,
        *,
        show_actions: bool = False,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize agent card.
        
        Args:
            agent: Agent to display.
            show_actions: Whether to show action buttons.
            name: Widget name.
            id: Widget ID.
            classes: Additional CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
        self.agent = agent
        self.show_actions = show_actions
        
        # Add status class
        if agent.status:
            self.add_class(agent.status)
    
    def compose(self) -> ComposeResult:
        """Compose the agent card widget."""
        icon = self.ROLE_ICONS.get(self.agent.role, "🤖")
        
        # Header with icon, name, and status
        with Horizontal(classes="agent-header"):
            yield Static(icon, classes="agent-icon")
            with Vertical(classes="agent-name-container"):
                yield Static(self.agent.name, classes="agent-name")
                yield Static(self.agent.role.title(), classes="agent-role")
            with Container(classes="agent-status"):
                yield StatusIndicator(self.agent.status)
        
        # Stats row
        with Horizontal(classes="agent-stats"):
            with Container(classes="stat"):
                yield Static(str(self.agent.tasks_completed), classes="stat-value")
                yield Static("Completed", classes="stat-label")
            with Container(classes="stat"):
                yield Static(str(self.agent.tasks_failed), classes="stat-value")
                yield Static("Failed", classes="stat-label")
            with Container(classes="stat"):
                success_rate = f"{self.agent.success_rate:.0%}" if self.agent.success_rate > 0 else "N/A"
                yield Static(success_rate, classes="stat-value")
                yield Static("Success", classes="stat-label")
        
        # Model info
        if self.agent.model_id:
            yield Static(f"Model: {self.agent.model_id}", classes="agent-model")
        
        # Current task
        if self.agent.current_task_id:
            yield Static(f"Current: {self.agent.current_task_id}", classes="agent-model")
        
        # Actions (optional)
        if self.show_actions:
            with Horizontal(classes="agent-actions"):
                yield Button("Configure", variant="primary", id="configure")
                if self.agent.status == "running":
                    yield Button("Pause", variant="warning", id="pause")
                elif self.agent.status == "paused":
                    yield Button("Resume", variant="success", id="resume")
                else:
                    yield Button("Start", variant="success", id="start")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        event.stop()
