"""Agent data model.

This module defines the Agent dataclass and related enums for
representing AI agents and their states.

Example:
    >>> agent = Agent(
    ...     id="code-agent",
    ...     name="Code Agent",
    ...     role="code",
    ...     model_id="codellama",
    ... )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class AgentStatus(Enum):
    """Enumeration of possible agent states.
    
    Attributes:
        IDLE: Agent is idle and available.
        RUNNING: Agent is currently running a task.
        PAUSED: Agent is paused.
        ERROR: Agent has encountered an error.
        STOPPED: Agent is stopped.
    """
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def icon(self) -> str:
        """Get the icon for this status."""
        icons = {
            AgentStatus.IDLE: "⚪",
            AgentStatus.RUNNING: "🔵",
            AgentStatus.PAUSED: "🟡",
            AgentStatus.ERROR: "🔴",
            AgentStatus.STOPPED: "⚫",
        }
        return icons.get(self, "⚪")


class AgentRole(Enum):
    """Enumeration of agent roles.
    
    Attributes:
        CODE: Code generation and review agent.
        RESEARCH: Research and information gathering agent.
        TASK: Task execution and management agent.
        CHAT: Conversational assistant agent.
        DATA: Data processing and analysis agent.
        TESTING: Testing and QA agent.
    """
    CODE = "code"
    RESEARCH = "research"
    TASK = "task"
    CHAT = "chat"
    DATA = "data"
    TESTING = "testing"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def icon(self) -> str:
        """Get the icon for this role."""
        icons = {
            AgentRole.CODE: "💻",
            AgentRole.RESEARCH: "🔍",
            AgentRole.TASK: "📋",
            AgentRole.CHAT: "💬",
            AgentRole.DATA: "📊",
            AgentRole.TESTING: "🧪",
        }
        return icons.get(self, "🤖")
    
    @property
    def display_name(self) -> str:
        """Get the display name for this role."""
        names = {
            AgentRole.CODE: "Code Agent",
            AgentRole.RESEARCH: "Research Agent",
            AgentRole.TASK: "Task Agent",
            AgentRole.CHAT: "Chat Agent",
            AgentRole.DATA: "Data Agent",
            AgentRole.TESTING: "Testing Agent",
        }
        return names.get(self, "Agent")


@dataclass
class Agent:
    """Agent configuration and task tracking.
    
    This class represents an AI agent that can execute tasks
    using a specific AI model with a defined role.
    
    Attributes:
        id: Unique identifier for the agent.
        name: Human-readable agent name.
        role: Agent role/specialization.
        status: Current status of the agent.
        model_id: ID of the model this agent uses.
        system_prompt: System prompt for the agent.
        tasks_completed: Number of tasks completed.
        tasks_failed: Number of tasks failed.
        current_task_id: ID of current task being executed.
        created_at: When the agent was created.
        last_active: When the agent was last active.
        max_concurrent_tasks: Maximum concurrent tasks.
        priority: Agent priority (higher = more important).
        metadata: Additional metadata.
    
    Example:
        >>> agent = Agent(
        ...     id="research-1",
        ...     name="Research Agent",
        ...     role="research",
        ...     model_id="llama3.2",
        ... )
    """
    id: str
    name: str
    role: str
    status: str = "idle"
    model_id: Optional[str] = None
    system_prompt: Optional[str] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    current_task_id: Optional[str] = None
    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    max_concurrent_tasks: int = 1
    priority: int = 0
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Initialize default values after creation."""
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def is_available(self) -> bool:
        """Check if agent is available for new tasks."""
        return self.status == "idle" and self.current_task_id is None
    
    @property
    def success_rate(self) -> float:
        """Calculate the agent's success rate."""
        total = self.tasks_completed + self.tasks_failed
        if total == 0:
            return 0.0
        return self.tasks_completed / total
    
    @property
    def role_icon(self) -> str:
        """Get the icon for this agent's role."""
        try:
            role = AgentRole(self.role)
            return role.icon
        except ValueError:
            return "🤖"
    
    def start_task(self, task_id: str) -> None:
        """Mark agent as starting a task.
        
        Args:
            task_id: ID of the task to start.
        """
        self.status = "running"
        self.current_task_id = task_id
        self.last_active = datetime.now()
    
    def complete_task(self, success: bool = True) -> None:
        """Mark task as completed.
        
        Args:
            success: Whether the task was successful.
        """
        if success:
            self.tasks_completed += 1
        else:
            self.tasks_failed += 1
        self.status = "idle"
        self.current_task_id = None
        self.last_active = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert agent to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "status": self.status,
            "model_id": self.model_id,
            "system_prompt": self.system_prompt,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "current_task_id": self.current_task_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "priority": self.priority,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> Agent:
        """Create agent from dictionary."""
        if data.get("created_at"):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("last_active"):
            data["last_active"] = datetime.fromisoformat(data["last_active"])
        return cls(**data)
