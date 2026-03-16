"""Agent service for AI Dashboard.

This module provides agent management functionality,
including creation, assignment, and task execution.

Example:
    >>> service = AgentService()
    >>> service.create_agent(Agent(id="code-1", name="Code Agent", role="code"))
    >>> agent = service.get_agent("code-1")
"""

from __future__ import annotations

from typing import Optional

from ai_dashboard.core.exceptions import AgentBusyError, AgentError, AgentNotFoundError
from ai_dashboard.core.logging import get_logger
from ai_dashboard.models.agent import Agent

logger = get_logger(__name__)


class AgentService:
    """Service for managing AI agents.
    
    This service handles:
    - Agent creation and removal
    - Agent status tracking
    - Task assignment
    - Agent statistics
    
    Attributes:
        agents: Dictionary of registered agents.
    """
    
    def __init__(self) -> None:
        """Initialize agent service with default agents."""
        self._agents: dict[str, Agent] = {}
        self._initialize_default_agents()
    
    def _initialize_default_agents(self) -> None:
        """Initialize default AI agents."""
        default_agents = [
            Agent(
                id="agent-code",
                name="Code Agent",
                role="code",
                status="idle",
                tasks_completed=12,
                model_id="ollama-codellama",
                system_prompt="You are an expert programmer. Help with code generation, review, and debugging.",
            ),
            Agent(
                id="agent-research",
                name="Research Agent",
                role="research",
                status="running",
                tasks_completed=3,
                model_id="ollama-llama3.2",
                system_prompt="You are a research assistant. Help gather and analyze information.",
            ),
            Agent(
                id="agent-task",
                name="Task Agent",
                role="task",
                status="idle",
                tasks_completed=5,
                model_id="ollama-llama3.2",
                system_prompt="You are a task management assistant. Help organize and track tasks.",
            ),
            Agent(
                id="agent-chat",
                name="Chat Agent",
                role="chat",
                status="running",
                tasks_completed=8,
                model_id="claude-opus",
                system_prompt="You are a helpful conversational assistant.",
            ),
        ]
        
        for agent in default_agents:
            self._agents[agent.id] = agent
    
    def create_agent(self, agent: Agent) -> None:
        """Create a new agent.
        
        Args:
            agent: Agent to create.
            
        Raises:
            AgentError: If agent ID already exists.
        """
        if agent.id in self._agents:
            raise AgentError(
                f"Agent already exists: {agent.id}",
                agent_id=agent.id,
            )
        
        self._agents[agent.id] = agent
        logger.info(f"Created agent: {agent.name} (role: {agent.role})")
    
    def delete_agent(self, agent_id: str) -> None:
        """Delete an agent.
        
        Args:
            agent_id: ID of agent to delete.
            
        Raises:
            AgentNotFoundError: If agent doesn't exist.
        """
        if agent_id not in self._agents:
            raise AgentNotFoundError(agent_id)
        
        del self._agents[agent_id]
        logger.info(f"Deleted agent: {agent_id}")
    
    def get_agent(self, agent_id: str) -> Agent:
        """Get an agent by ID.
        
        Args:
            agent_id: Agent ID.
            
        Returns:
            Agent instance.
            
        Raises:
            AgentNotFoundError: If agent doesn't exist.
        """
        if agent_id not in self._agents:
            raise AgentNotFoundError(agent_id)
        return self._agents[agent_id]
    
    def get_all_agents(self) -> list[Agent]:
        """Get all agents.
        
        Returns:
            List of all agents.
        """
        return list(self._agents.values())
    
    def get_agents_by_role(self, role: str) -> list[Agent]:
        """Get agents by role.
        
        Args:
            role: Role to filter by.
            
        Returns:
            List of agents with the role.
        """
        return [a for a in self._agents.values() if a.role == role]
    
    def get_agents_by_status(self, status: str) -> list[Agent]:
        """Get agents by status.
        
        Args:
            status: Status to filter by.
            
        Returns:
            List of agents with the status.
        """
        return [a for a in self._agents.values() if a.status == status]
    
    def get_available_agents(self) -> list[Agent]:
        """Get all available agents.
        
        Returns:
            List of available agents.
        """
        return [a for a in self._agents.values() if a.is_available]
    
    def assign_task(self, agent_id: str, task_id: str) -> None:
        """Assign a task to an agent.
        
        Args:
            agent_id: Agent ID.
            task_id: Task ID.
            
        Raises:
            AgentNotFoundError: If agent doesn't exist.
            AgentBusyError: If agent is busy.
        """
        agent = self.get_agent(agent_id)
        
        if not agent.is_available:
            raise AgentBusyError(agent_id, agent.current_task_id)
        
        agent.start_task(task_id)
        logger.info(f"Task {task_id} assigned to agent {agent_id}")
    
    def complete_task(self, agent_id: str, success: bool = True) -> None:
        """Mark agent's current task as complete.
        
        Args:
            agent_id: Agent ID.
            success: Whether task was successful.
        """
        agent = self.get_agent(agent_id)
        agent.complete_task(success)
        logger.info(
            f"Agent {agent_id} completed task (success={success})"
        )
    
    def update_agent_status(self, agent_id: str, status: str) -> None:
        """Update agent status.
        
        Args:
            agent_id: Agent ID.
            status: New status.
        """
        agent = self.get_agent(agent_id)
        old_status = agent.status
        agent.status = status
        logger.info(f"Agent {agent_id} status: {old_status} -> {status}")
    
    def set_agent_model(self, agent_id: str, model_id: str) -> None:
        """Set the model for an agent.
        
        Args:
            agent_id: Agent ID.
            model_id: Model ID.
        """
        agent = self.get_agent(agent_id)
        agent.model_id = model_id
        logger.info(f"Agent {agent_id} model set to {model_id}")
    
    def set_agent_system_prompt(
        self,
        agent_id: str,
        system_prompt: str,
    ) -> None:
        """Set the system prompt for an agent.
        
        Args:
            agent_id: Agent ID.
            system_prompt: System prompt.
        """
        agent = self.get_agent(agent_id)
        agent.system_prompt = system_prompt
        logger.info(f"Agent {agent_id} system prompt updated")
    
    def get_agent_count(self) -> int:
        """Get total agent count.
        
        Returns:
            Number of agents.
        """
        return len(self._agents)
    
    def get_running_agent_count(self) -> int:
        """Get count of running agents.
        
        Returns:
            Number of running agents.
        """
        return len([a for a in self._agents.values() if a.status == "running"])
    
    def get_agent_statistics(self) -> dict:
        """Get agent statistics.
        
        Returns:
            Dictionary of statistics.
        """
        agents = self._agents.values()
        return {
            "total": len(agents),
            "running": len([a for a in agents if a.status == "running"]),
            "idle": len([a for a in agents if a.status == "idle"]),
            "total_tasks_completed": sum(a.tasks_completed for a in agents),
            "total_tasks_failed": sum(a.tasks_failed for a in agents),
        }
