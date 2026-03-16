"""Stat box widget for displaying statistics."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static


class StatBox(Container):
    """Widget for displaying a statistic box.

    This widget displays a value with a label, optionally
    with an icon and trend indicator.

    Attributes:
        value: The statistic value to display.
        label: The label for the statistic.
        icon: Optional icon to display.
        trend: Optional trend indicator (up, down, neutral).

    Example:
        >>> box = StatBox(value="5", label="Models", icon="🤖")
        >>> box = StatBox(value="78%", label="CPU", trend="up")
    """

    TREND_ICONS = {
        "up": "📈",
        "down": "📉",
        "neutral": "➡️",
    }

    DEFAULT_CSS = """
    StatBox {
        width: 1fr;
        height: auto;
        min-height: 5;
        background: $panel;
        border: round $border;
        padding: 1;
        margin: 0;
        align: center middle;
    }
    
    StatBox:hover {
        border: round $accent;
    }
    
    StatBox .stat-icon {
        text-align: center;
        margin-bottom: 1;
    }
    
    StatBox .stat-value-container {
        height: auto;
        text-align: center;
    }
    
    StatBox .stat-value {
        text-style: bold;
        color: $accent;
        font-size: 1.5em;
        text-align: center;
    }
    
    StatBox .stat-trend {
        display: inline;
        margin-left: 1;
    }
    
    StatBox .stat-label {
        color: $text-muted;
        text-align: center;
        margin-top: 1;
    }
    
    StatBox.trend-up .stat-value { color: $success; }
    StatBox.trend-down .stat-value { color: $error; }
    StatBox.trend-neutral .stat-value { color: $warning; }
    """

    def __init__(
        self,
        value: str | int | float,
        label: str,
        *,
        icon: str | None = None,
        trend: str | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize stat box.

        Args:
            value: Statistic value.
            label: Label for the statistic.
            icon: Optional icon.
            trend: Trend indicator (up, down, neutral).
            name: Widget name.
            id: Widget ID.
            classes: Additional CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
        self._value = str(value)
        self._label = label
        self._icon = icon
        self._trend = trend

        if trend:
            self.add_class(f"trend-{trend}")

    def compose(self) -> ComposeResult:
        """Compose the stat box widget."""
        if self._icon:
            yield Static(self._icon, classes="stat-icon")

        with Container(classes="stat-value-container"):
            value_text = self._value
            if self._trend:
                trend_icon = self.TREND_ICONS.get(self._trend, "")
                value_text = f"{value_text} {trend_icon}"
            yield Static(value_text, classes="stat-value")

        yield Static(self._label, classes="stat-label")

    @property
    def value(self) -> str:
        """Get the current value."""
        return self._value

    def update_value(self, value: str | int | float) -> None:
        """Update the displayed value.

        Args:
            value: New value to display.
        """
        self._value = str(value)
        try:
            value_widget = self.query_one(".stat-value", Static)
            value_text = self._value
            if self._trend:
                trend_icon = self.TREND_ICONS.get(self._trend, "")
                value_text = f"{value_text} {trend_icon}"
            value_widget.update(value_text)
        except Exception:
            pass

    def update_label(self, label: str) -> None:
        """Update the label.

        Args:
            label: New label.
        """
        self._label = label
        try:
            label_widget = self.query_one(".stat-label", Static)
            label_widget.update(label)
        except Exception:
            pass
