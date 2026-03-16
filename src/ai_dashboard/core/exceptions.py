"""Custom exceptions for AI Dashboard.

This module defines a comprehensive exception hierarchy for the application,
allowing for precise error handling and meaningful error messages.

Exception Hierarchy:
    AIDashboardError (base)
    ├── ConfigurationError
    ├── AuthenticationError
    ├── ModelError
    │   ├── ModelNotFoundError
    │   └── ModelConnectionError
    ├── AgentError
    │   ├── AgentNotFoundError
    │   └── AgentBusyError
    ├── TaskError
    │   ├── TaskNotFoundError
    │   └── TaskExecutionError
    └── ValidationError
"""

from __future__ import annotations

from typing import Any


class AIDashboardError(Exception):
    """Base exception for all AI Dashboard errors.

    Attributes:
        message: Human-readable error message.
        error_code: Optional error code for programmatic handling.
        details: Additional error details.
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"[{self.error_code}] {self.message} - {self.details}"
        return f"[{self.error_code}] {self.message}"

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class ConfigurationError(AIDashboardError):
    """Raised when there is a configuration-related error."""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, "CONFIG_ERROR", details)


class AuthenticationError(AIDashboardError):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, "AUTH_ERROR", details)


class ModelError(AIDashboardError):
    """Base exception for model-related errors."""

    def __init__(
        self,
        message: str,
        model_id: str | None = None,
        error_code: str = "MODEL_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        details = details or {}
        if model_id:
            details["model_id"] = model_id
        super().__init__(message, error_code, details)


class ModelNotFoundError(ModelError):
    """Raised when a requested model is not found."""

    def __init__(self, model_id: str) -> None:
        super().__init__(
            f"Model not found: {model_id}",
            model_id=model_id,
            error_code="MODEL_NOT_FOUND",
        )


class ModelConnectionError(ModelError):
    """Raised when connection to a model fails."""

    def __init__(
        self,
        model_id: str,
        reason: str | None = None,
    ) -> None:
        message = f"Failed to connect to model: {model_id}"
        if reason:
            message += f" - {reason}"
        super().__init__(message, model_id, "MODEL_CONNECTION_ERROR")


class AgentError(AIDashboardError):
    """Base exception for agent-related errors."""

    def __init__(
        self,
        message: str,
        agent_id: str | None = None,
        error_code: str = "AGENT_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        details = details or {}
        if agent_id:
            details["agent_id"] = agent_id
        super().__init__(message, error_code, details)


class AgentNotFoundError(AgentError):
    """Raised when a requested agent is not found."""

    def __init__(self, agent_id: str) -> None:
        super().__init__(
            f"Agent not found: {agent_id}",
            agent_id=agent_id,
            error_code="AGENT_NOT_FOUND",
        )


class AgentBusyError(AgentError):
    """Raised when trying to use a busy agent."""

    def __init__(self, agent_id: str, current_task: str | None = None) -> None:
        message = f"Agent is busy: {agent_id}"
        details = {}
        if current_task:
            details["current_task"] = current_task
            message += f" (working on: {current_task})"
        super().__init__(message, agent_id, "AGENT_BUSY", details)


class TaskError(AIDashboardError):
    """Base exception for task-related errors."""

    def __init__(
        self,
        message: str,
        task_id: str | None = None,
        error_code: str = "TASK_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        details = details or {}
        if task_id:
            details["task_id"] = task_id
        super().__init__(message, error_code, details)


class TaskNotFoundError(TaskError):
    """Raised when a requested task is not found."""

    def __init__(self, task_id: str) -> None:
        super().__init__(
            f"Task not found: {task_id}",
            task_id=task_id,
            error_code="TASK_NOT_FOUND",
        )


class TaskExecutionError(TaskError):
    """Raised when task execution fails."""

    def __init__(
        self,
        task_id: str,
        reason: str | None = None,
    ) -> None:
        message = f"Task execution failed: {task_id}"
        if reason:
            message += f" - {reason}"
        super().__init__(message, task_id, "TASK_EXECUTION_ERROR")


class ValidationError(AIDashboardError):
    """Raised when validation fails."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any | None = None,
    ) -> None:
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        super().__init__(message, "VALIDATION_ERROR", details)


class SecurityError(AIDashboardError):
    """Raised when a security violation is detected."""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, "SECURITY_ERROR", details)


class RateLimitError(AIDashboardError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        provider: str,
        retry_after: int | None = None,
    ) -> None:
        message = f"Rate limit exceeded for {provider}"
        details = {"provider": provider}
        if retry_after:
            details["retry_after"] = retry_after
            message += f". Retry after {retry_after} seconds."
        super().__init__(message, "RATE_LIMIT_ERROR", details)
