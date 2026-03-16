"""Tasks screen for AI Dashboard."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static, Button

from ai_dashboard.widgets.task_item import TaskItem

if TYPE_CHECKING:
    from ai_dashboard.app import AIDashboardApp


class TasksScreen(Screen):
    """Tasks management screen."""
    
    BINDINGS: ClassVar[tuple[Binding, ...]] = (
        Binding("escape", "go_back", "Back"),
        Binding("n", "new_task", "New Task"),
        Binding("r", "refresh", "Refresh"),
        Binding("c", "clear_completed", "Clear Completed"),
        Binding("1", "goto_dashboard", "Dashboard"),
        Binding("2", "goto_models", "Models"),
        Binding("3", "goto_agents", "Agents"),
        Binding("4", "goto_chat", "Chat"),
        Binding("5", "goto_tasks", "Tasks"),
        Binding("6", "goto_settings", "Settings"),
    )
    
    DEFAULT_CSS = """
    TasksScreen { layout: vertical; height: 100%; }
    TasksScreen .container { padding: 1 2; height: 1fr; layout: vertical; }
    TasksScreen .header { layout: horizontal; margin-bottom: 1; }
    TasksScreen .title { text-style: bold; color: $accent; width: 1fr; }
    TasksScreen .stats { color: $text-muted; }
    TasksScreen .toolbar { layout: horizontal; margin-bottom: 1; }
    TasksScreen .toolbar Button { margin-right: 1; }
    TasksScreen .section { margin-bottom: 1; }
    TasksScreen .section-title { text-style: bold; color: $text; margin-bottom: 1; }
    TasksScreen .tasks-list { height: 1fr; }
    TasksScreen .empty { color: $text-muted; text-align: center; padding: 2; }
    """
    
    @property
    def app(self) -> "AIDashboardApp":
        return super().app  # type: ignore
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Container(classes="container"):
            # Header with stats
            stats = self.app.task_service.get_task_statistics()
            with Horizontal(classes="header"):
                yield Static("📋 Task Management", classes="title")
                yield Static(
                    f"Running: {stats['running']} | Pending: {stats['pending']} | Completed: {stats['completed']}",
                    classes="stats",
                )
            
            # Toolbar
            with Horizontal(classes="toolbar"):
                yield Button("➕ New Task", variant="primary", id="new-task")
                yield Button("📊 Schedule", id="schedule")
                yield Button("📁 Templates", id="templates")
                yield Button("🗑️ Clear Completed", id="clear")
            
            # Task lists
            with VerticalScroll(classes="tasks-list"):
                # Running tasks
                with Container(classes="section"):
                    yield Static("▶️ Running Tasks", classes="section-title")
                    running = self.app.task_service.get_running_tasks()
                    if running:
                        for task in running:
                            yield TaskItem(task)
                    else:
                        yield Static("No running tasks", classes="empty")
                
                # Pending tasks
                with Container(classes="section"):
                    yield Static("⏳ Pending Tasks", classes="section-title")
                    pending = self.app.task_service.get_pending_tasks()
                    if pending:
                        for task in pending:
                            yield TaskItem(task)
                    else:
                        yield Static("No pending tasks", classes="empty")
                
                # Completed tasks
                with Container(classes="section"):
                    yield Static("✅ Completed Today", classes="section-title")
                    completed = self.app.task_service.get_completed_tasks()
                    if completed:
                        for task in completed[:5]:
                            yield TaskItem(task)
                    else:
                        yield Static("No completed tasks today", classes="empty")
        
        yield Footer()
    
    def action_new_task(self) -> None:
        """Create new task action."""
        # TODO: Open modal dialog for task creation
        pass
    
    def action_clear_completed(self) -> None:
        """Clear completed tasks."""
        count = self.app.task_service.clear_completed_tasks()
        if count > 0:
            self.refresh()
    
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
        pass
    
    def action_goto_settings(self) -> None:
        self.app.push_screen("settings")
    
    def action_refresh(self) -> None:
        self.refresh()
