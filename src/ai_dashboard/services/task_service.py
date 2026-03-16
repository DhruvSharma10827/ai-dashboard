"""Task service for AI Dashboard.

This module provides task management functionality,
including creation, scheduling, and execution tracking.

Example:
    >>> service = TaskService()
    >>> service.create_task(Task(id="task-1", title="Analyze code"))
    >>> task = service.get_task("task-1")
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from ai_dashboard.core.exceptions import TaskError, TaskNotFoundError
from ai_dashboard.core.logging import get_logger
from ai_dashboard.models.task import Task, TaskPriority, TaskStatus

logger = get_logger(__name__)


class TaskService:
    """Service for managing tasks.
    
    This service handles:
    - Task creation and removal
    - Task scheduling
    - Task execution tracking
    - Task statistics
    
    Attributes:
        tasks: Dictionary of tasks.
    """
    
    def __init__(self) -> None:
        """Initialize task service."""
        self._tasks: dict[str, Task] = {}
        self._task_counter: int = 0
    
    def _generate_task_id(self) -> str:
        """Generate a unique task ID.
        
        Returns:
            Unique task ID.
        """
        self._task_counter += 1
        return f"task-{self._task_counter:04d}"
    
    def create_task(
        self,
        title: str,
        description: str = "",
        priority: str = "normal",
        agent_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> Task:
        """Create a new task.
        
        Args:
            title: Task title.
            description: Task description.
            priority: Task priority.
            agent_id: Agent to assign.
            tags: Task tags.
            
        Returns:
            Created task.
        """
        task = Task(
            id=self._generate_task_id(),
            title=title,
            description=description,
            priority=priority,
            agent_id=agent_id,
            tags=tags or [],
        )
        
        self._tasks[task.id] = task
        logger.info(f"Created task: {task.id} - {title}")
        return task
    
    def delete_task(self, task_id: str) -> None:
        """Delete a task.
        
        Args:
            task_id: ID of task to delete.
            
        Raises:
            TaskNotFoundError: If task doesn't exist.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        
        del self._tasks[task_id]
        logger.info(f"Deleted task: {task_id}")
    
    def get_task(self, task_id: str) -> Task:
        """Get a task by ID.
        
        Args:
            task_id: Task ID.
            
        Returns:
            Task instance.
            
        Raises:
            TaskNotFoundError: If task doesn't exist.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        return self._tasks[task_id]
    
    def get_all_tasks(self) -> list[Task]:
        """Get all tasks.
        
        Returns:
            List of all tasks.
        """
        return list(self._tasks.values())
    
    def get_tasks_by_status(self, status: str) -> list[Task]:
        """Get tasks by status.
        
        Args:
            status: Status to filter by.
            
        Returns:
            List of tasks with the status.
        """
        return [t for t in self._tasks.values() if t.status == status]
    
    def get_tasks_by_agent(self, agent_id: str) -> list[Task]:
        """Get tasks assigned to an agent.
        
        Args:
            agent_id: Agent ID.
            
        Returns:
            List of tasks for the agent.
        """
        return [t for t in self._tasks.values() if t.agent_id == agent_id]
    
    def get_pending_tasks(self) -> list[Task]:
        """Get all pending tasks.
        
        Returns:
            List of pending tasks.
        """
        return self.get_tasks_by_status("pending")
    
    def get_running_tasks(self) -> list[Task]:
        """Get all running tasks.
        
        Returns:
            List of running tasks.
        """
        return self.get_tasks_by_status("running")
    
    def get_completed_tasks(self) -> list[Task]:
        """Get all completed tasks.
        
        Returns:
            List of completed tasks.
        """
        return self.get_tasks_by_status("completed")
    
    def get_failed_tasks(self) -> list[Task]:
        """Get all failed tasks.
        
        Returns:
            List of failed tasks.
        """
        return self.get_tasks_by_status("failed")
    
    def start_task(self, task_id: str, agent_id: Optional[str] = None) -> None:
        """Start a task.
        
        Args:
            task_id: Task ID.
            agent_id: Agent ID to assign.
        """
        task = self.get_task(task_id)
        task.start(agent_id)
        logger.info(f"Started task: {task_id}")
    
    def complete_task(self, task_id: str, result: Optional[str] = None) -> None:
        """Mark a task as completed.
        
        Args:
            task_id: Task ID.
            result: Task result.
        """
        task = self.get_task(task_id)
        task.complete(result)
        logger.info(f"Completed task: {task_id}")
    
    def fail_task(self, task_id: str, error: str) -> None:
        """Mark a task as failed.
        
        Args:
            task_id: Task ID.
            error: Error message.
        """
        task = self.get_task(task_id)
        task.fail(error)
        logger.warning(f"Failed task: {task_id} - {error}")
    
    def cancel_task(self, task_id: str) -> None:
        """Cancel a task.
        
        Args:
            task_id: Task ID.
        """
        task = self.get_task(task_id)
        task.cancel()
        logger.info(f"Cancelled task: {task_id}")
    
    def retry_task(self, task_id: str) -> None:
        """Retry a failed task.
        
        Args:
            task_id: Task ID.
            
        Raises:
            TaskError: If task cannot be retried.
        """
        task = self.get_task(task_id)
        
        if not task.can_retry:
            raise TaskError(
                f"Task cannot be retried: {task_id}",
                task_id=task_id,
            )
        
        task.retry_count += 1
        task.status = "pending"
        task.error = None
        task.completed_at = None
        logger.info(f"Retrying task: {task_id} (attempt {task.retry_count})")
    
    def update_task_progress(
        self,
        task_id: str,
        progress: int,
        message: Optional[str] = None,
    ) -> None:
        """Update task progress.
        
        Args:
            task_id: Task ID.
            progress: Progress percentage (0-100).
            message: Progress message.
        """
        task = self.get_task(task_id)
        task.update_progress(progress, message)
    
    def get_task_count(self) -> int:
        """Get total task count.
        
        Returns:
            Number of tasks.
        """
        return len(self._tasks)
    
    def get_task_statistics(self) -> dict:
        """Get task statistics.
        
        Returns:
            Dictionary of statistics.
        """
        tasks = self._tasks.values()
        return {
            "total": len(tasks),
            "pending": len([t for t in tasks if t.status == "pending"]),
            "running": len([t for t in tasks if t.status == "running"]),
            "completed": len([t for t in tasks if t.status == "completed"]),
            "failed": len([t for t in tasks if t.status == "failed"]),
        }
    
    def clear_completed_tasks(self) -> int:
        """Clear all completed tasks.
        
        Returns:
            Number of tasks cleared.
        """
        to_delete = [t.id for t in self._tasks.values() if t.is_complete]
        for task_id in to_delete:
            del self._tasks[task_id]
        
        if to_delete:
            logger.info(f"Cleared {len(to_delete)} completed tasks")
        
        return len(to_delete)
    
    def get_tasks_by_priority(self, priority: str) -> list[Task]:
        """Get tasks by priority.
        
        Args:
            priority: Priority to filter by.
            
        Returns:
            List of tasks with the priority.
        """
        return [t for t in self._tasks.values() if t.priority == priority]
    
    def get_high_priority_tasks(self) -> list[Task]:
        """Get all high priority tasks.
        
        Returns:
            List of high priority tasks.
        """
        return [t for t in self._tasks.values() if t.priority in ("high", "urgent")]
