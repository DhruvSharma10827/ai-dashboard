"""Task data model.

This module defines the Task dataclass and related enums for
representing tasks and their states.

Example:
    >>> task = Task(
    ...     id="task-001",
    ...     title="Analyze codebase",
    ...     description="Analyze the project structure",
    ...     agent_id="research-agent",
    ... )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class TaskStatus(Enum):
    """Enumeration of possible task states.
    
    Attributes:
        PENDING: Task is pending execution.
        QUEUED: Task is queued for execution.
        RUNNING: Task is currently running.
        COMPLETED: Task completed successfully.
        FAILED: Task execution failed.
        CANCELLED: Task was cancelled.
        PAUSED: Task is paused.
    """
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def icon(self) -> str:
        """Get the icon for this status."""
        icons = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.QUEUED: "📥",
            TaskStatus.RUNNING: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.CANCELLED: "🚫",
            TaskStatus.PAUSED: "⏸️",
        }
        return icons.get(self, "❓")
    
    @property
    def is_terminal(self) -> bool:
        """Check if this is a terminal state."""
        return self in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)


class TaskPriority(Enum):
    """Enumeration of task priorities.
    
    Attributes:
        LOW: Low priority task.
        NORMAL: Normal priority task.
        HIGH: High priority task.
        URGENT: Urgent priority task.
    """
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3
    
    def __str__(self) -> str:
        return self.name.lower()
    
    @property
    def icon(self) -> str:
        """Get the icon for this priority."""
        icons = {
            TaskPriority.LOW: "🔽",
            TaskPriority.NORMAL: "➡️",
            TaskPriority.HIGH: "🔼",
            TaskPriority.URGENT: "🔴",
        }
        return icons.get(self, "➡️")


@dataclass
class Task:
    """Task definition and status tracking.
    
    This class represents a task that can be executed by an agent,
    including its status, timing, and result information.
    
    Attributes:
        id: Unique identifier for the task.
        title: Short title for the task.
        description: Detailed task description.
        status: Current status of the task.
        priority: Task priority level.
        agent_id: ID of the agent assigned to this task.
        created_at: When the task was created.
        started_at: When task execution started.
        completed_at: When task execution completed.
        result: Result of the task execution.
        error: Error message if task failed.
        progress: Progress percentage (0-100).
        parent_task_id: ID of parent task (for subtasks).
        tags: Tags for categorization.
        metadata: Additional metadata.
        max_retries: Maximum retry attempts.
        retry_count: Current retry count.
        timeout_seconds: Task timeout in seconds.
    
    Example:
        >>> task = Task(
        ...     id="task-001",
        ...     title="Generate documentation",
        ...     description="Generate API documentation for the project",
        ...     priority="high",
        ... )
    """
    id: str
    title: str
    description: str = ""
    status: str = "pending"
    priority: str = "normal"
    agent_id: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None
    progress: int = 0
    parent_task_id: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    max_retries: int = 3
    retry_count: int = 0
    timeout_seconds: int = 300
    
    def __post_init__(self) -> None:
        """Initialize default values after creation."""
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate task duration in seconds."""
        if self.started_at is None:
            return None
        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()
    
    @property
    def is_complete(self) -> bool:
        """Check if task is in a terminal state."""
        return self.status in ("completed", "failed", "cancelled")
    
    @property
    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return (
            self.status == "failed"
            and self.retry_count < self.max_retries
        )
    
    def start(self, agent_id: Optional[str] = None) -> None:
        """Mark task as started.
        
        Args:
            agent_id: ID of the agent starting the task.
        """
        self.status = "running"
        self.started_at = datetime.now()
        if agent_id:
            self.agent_id = agent_id
    
    def complete(self, result: Optional[str] = None) -> None:
        """Mark task as completed.
        
        Args:
            result: Task result.
        """
        self.status = "completed"
        self.completed_at = datetime.now()
        self.progress = 100
        if result:
            self.result = result
    
    def fail(self, error: str) -> None:
        """Mark task as failed.
        
        Args:
            error: Error message.
        """
        self.status = "failed"
        self.completed_at = datetime.now()
        self.error = error
    
    def cancel(self) -> None:
        """Cancel the task."""
        self.status = "cancelled"
        self.completed_at = datetime.now()
    
    def update_progress(self, progress: int, message: Optional[str] = None) -> None:
        """Update task progress.
        
        Args:
            progress: Progress percentage (0-100).
            message: Optional progress message.
        """
        self.progress = max(0, min(100, progress))
        if message:
            self.metadata["progress_message"] = message
    
    def to_dict(self) -> dict:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "agent_id": self.agent_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "progress": self.progress,
            "parent_task_id": self.parent_task_id,
            "tags": self.tags,
            "metadata": self.metadata,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "timeout_seconds": self.timeout_seconds,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> Task:
        """Create task from dictionary."""
        datetime_fields = ["created_at", "started_at", "completed_at"]
        for field_name in datetime_fields:
            if data.get(field_name):
                data[field_name] = datetime.fromisoformat(data[field_name])
        return cls(**data)
