"""Task item widget for displaying task information."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container
from textual.containers import Horizontal
from textual.widgets import Static

from ai_dashboard.models.task import Task

if TYPE_CHECKING:
    pass


class TaskItem(Container):
    """Widget for displaying a task item.

    This widget displays task information including title,
    status, priority, and progress.

    Attributes:
        task: The task to display.

    Example:
        >>> task = Task(id="task-1", title="Analyze code")
        >>> item = TaskItem(task)
    """

    # Status icons
    STATUS_ICONS: dict[str, str] = {
        "pending": "⏳",
        "queued": "📥",
        "running": "🔄",
        "completed": "✅",
        "failed": "❌",
        "cancelled": "🚫",
        "paused": "⏸️",
    }

    # Priority indicators
    PRIORITY_ICONS: dict[str, str] = {
        "low": "🔽",
        "normal": "➡️",
        "high": "🔼",
        "urgent": "🔴",
    }

    DEFAULT_CSS = """
    TaskItem {
        height: auto;
        min-height: 3;
        background: $surface;
        border: round $border;
        margin: 0 0 1 0;
        padding: 1;
    }
    
    TaskItem:hover {
        border: round $accent;
    }
    
    TaskItem.pending {
        border: round $warning;
    }
    
    TaskItem.running {
        border: round $accent;
    }
    
    TaskItem.completed {
        border: round $success;
    }
    
    TaskItem.failed {
        border: round $error;
    }
    
    TaskItem.cancelled {
        border: round $border;
        text-opacity: 0.5;
    }
    
    TaskItem .task-header {
        layout: horizontal;
        height: auto;
    }
    
    TaskItem .task-icon {
        width: 3;
        content-align: center middle;
    }
    
    TaskItem .task-title-container {
        width: 1fr;
    }
    
    TaskItem .task-title {
        text-style: bold;
        color: $text;
    }
    
    TaskItem .task-meta {
        color: $text-muted;
        font-size: 0.9em;
    }
    
    TaskItem .task-priority {
        width: auto;
        margin-left: 1;
    }
    
    TaskItem .task-status-container {
        width: auto;
    }
    
    TaskItem .task-status {
        color: $text-muted;
    }
    
    TaskItem.running .task-status {
        color: $accent;
    }
    
    TaskItem.completed .task-status {
        color: $success;
    }
    
    TaskItem.failed .task-status {
        color: $error;
    }
    
    TaskItem .task-progress {
        height: 1;
        background: $panel;
        margin-top: 1;
    }
    
    TaskItem .task-progress-bar {
        height: 1;
        background: $accent;
    }
    """

    def __init__(
        self,
        task: Task,
        *,
        show_progress: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize task item.

        Args:
            task: Task to display.
            show_progress: Whether to show progress bar.
            name: Widget name.
            id: Widget ID.
            classes: Additional CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
        self.task = task
        self.show_progress = show_progress

        # Add status class
        if task.status:
            self.add_class(task.status)

    def compose(self) -> ComposeResult:
        """Compose the task item widget."""
        status_icon = self.STATUS_ICONS.get(self.task.status, "❓")
        priority_icon = self.PRIORITY_ICONS.get(self.task.priority, "➡️")

        with Horizontal(classes="task-header"):
            yield Static(status_icon, classes="task-icon")

            with Container(classes="task-title-container"):
                yield Static(self.task.title, classes="task-title")

                # Meta info
                meta_parts = []
                if self.task.agent_id:
                    meta_parts.append(f"Agent: {self.task.agent_id}")
                if self.task.duration_seconds:
                    duration = self._format_duration(self.task.duration_seconds)
                    meta_parts.append(f"Duration: {duration}")
                if meta_parts:
                    yield Static("  |  ".join(meta_parts), classes="task-meta")

            yield Static(priority_icon, classes="task-priority")

            with Container(classes="task-status-container"):
                status_text = self.task.status.title()
                if self.task.progress > 0 and self.task.progress < 100:
                    status_text = f"{status_text} ({self.task.progress}%)"
                yield Static(status_text, classes="task-status")

        # Progress bar for running tasks
        if self.show_progress and self.task.status == "running" and self.task.progress > 0:
            with Container(classes="task-progress"):
                # Use a simple text-based progress representation
                progress_chars = int(self.task.progress / 10)
                bar = "█" * progress_chars + "░" * (10 - progress_chars)
                yield Static(bar, classes="task-progress-bar")

    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human readable.

        Args:
            seconds: Duration in seconds.

        Returns:
            Formatted duration string.
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        if seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"

    def update_progress(self, progress: int) -> None:
        """Update task progress.

        Args:
            progress: New progress value (0-100).
        """
        self.task.update_progress(progress)
        # Force re-render
        self.refresh()
