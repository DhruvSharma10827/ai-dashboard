"""Status indicator widget for displaying status states."""

from __future__ import annotations

from typing import Literal

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static

StatusType = Literal[
    "online", "offline", "limited", "running", "idle", "available", "stopped", "loading", "error"
]


class StatusIndicator(Horizontal):
    """Widget for displaying status with icon and label.

    This widget displays a status indicator with an appropriate
    icon and color based on the status type.

    Attributes:
        status: The status type to display.
        show_label: Whether to show the status label.

    Example:
        >>> indicator = StatusIndicator(status="running")
        >>> indicator = StatusIndicator(status="online", show_label=False)
    """

    # Status icons mapping
    STATUS_ICONS: dict[str, str] = {
        "online": "🟢",
        "offline": "🔴",
        "limited": "🟡",
        "running": "🔵",
        "idle": "⚪",
        "available": "🟢",
        "stopped": "⚫",
        "loading": "🟡",
        "error": "🔴",
    }

    # Status display names
    STATUS_LABELS: dict[str, str] = {
        "online": "Online",
        "offline": "Offline",
        "limited": "Limited",
        "running": "Running",
        "idle": "Idle",
        "available": "Available",
        "stopped": "Stopped",
        "loading": "Loading",
        "error": "Error",
    }

    DEFAULT_CSS = """
    StatusIndicator {
        height: auto;
        width: auto;
        align: right middle;
        padding: 0 1;
    }
    
    StatusIndicator .status-icon {
        width: auto;
    }
    
    StatusIndicator .status-label {
        width: auto;
        color: $text;
        margin-left: 1;
    }
    
    StatusIndicator.online .status-label { color: $success; }
    StatusIndicator.offline .status-label { color: $error; }
    StatusIndicator.limited .status-label { color: $warning; }
    StatusIndicator.running .status-label { color: $accent; }
    StatusIndicator.idle .status-label { color: $text-muted; }
    StatusIndicator.available .status-label { color: $success; }
    StatusIndicator.stopped .status-label { color: $text-muted; }
    StatusIndicator.loading .status-label { color: $warning; }
    StatusIndicator.error .status-label { color: $error; }
    """

    def __init__(
        self,
        status: StatusType = "idle",
        show_label: bool = True,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize status indicator.

        Args:
            status: Status type.
            show_label: Whether to show the label.
            name: Widget name.
            id: Widget ID.
            classes: Additional CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
        self.status = status
        self.show_label = show_label
        self.add_class(status)

    def compose(self) -> ComposeResult:
        """Compose the status indicator widget."""
        icon = self.STATUS_ICONS.get(self.status, "⚪")

        yield Static(icon, classes="status-icon")

        if self.show_label:
            label = self.STATUS_LABELS.get(self.status, self.status.title())
            yield Static(label, classes="status-label")

    def update_status(self, status: StatusType) -> None:
        """Update the status.

        Args:
            status: New status type.
        """
        # Remove old status class
        self.remove_class(self.status)

        # Update status
        self.status = status
        self.add_class(status)

        # Update icon
        icon = self.STATUS_ICONS.get(status, "⚪")
        icon_widget = self.query_one(".status-icon", Static)
        icon_widget.update(icon)

        # Update label if visible
        if self.show_label:
            label = self.STATUS_LABELS.get(status, status.title())
            label_widget = self.query_one(".status-label", Static)
            label_widget.update(label)
