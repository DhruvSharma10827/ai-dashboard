"""Unit tests for AI Dashboard services."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile

from ai_dashboard.core.config import Config
from ai_dashboard.core.exceptions import (
    AuthenticationError,
    AgentNotFoundError,
    ModelNotFoundError,
    TaskNotFoundError,
    AgentBusyError,
)
from ai_dashboard.services.auth import AuthService
from ai_dashboard.services.model_service import ModelService
from ai_dashboard.services.agent_service import AgentService
from ai_dashboard.services.task_service import TaskService
from ai_dashboard.models.ai_model import AIModel
from ai_dashboard.models.agent import Agent
from ai_dashboard.models.task import Task


class TestAuthService:
    """Tests for AuthService."""
    
    @pytest.fixture
    def auth_service(self):
        """Create auth service with fresh config."""
        config = Config()
        config.admin_password_hash = ""
        return AuthService(config=config)
    
    def test_is_first_run(self, auth_service):
        """Test is_first_run returns True when no password set."""
        assert auth_service.is_first_run() is True
    
    def test_setup_admin(self, auth_service):
        """Test setup_admin sets password correctly."""
        auth_service.setup_admin("secure_password123")
        
        assert auth_service.config.admin_password_hash != ""
        assert auth_service.is_first_run() is False
    
    def test_setup_admin_password_too_short(self, auth_service):
        """Test setup_admin rejects short passwords."""
        with pytest.raises(AuthenticationError, match="at least"):
            auth_service.setup_admin("short")
    
    def test_setup_admin_empty_password(self, auth_service):
        """Test setup_admin rejects empty passwords."""
        with pytest.raises(AuthenticationError, match="cannot be empty"):
            auth_service.setup_admin("")
    
    def test_setup_admin_password_mismatch(self, auth_service):
        """Test setup_admin rejects mismatched passwords."""
        with pytest.raises(AuthenticationError, match="do not match"):
            auth_service.setup_admin("password123", confirm="password456")
    
    def test_authenticate_success(self, auth_service):
        """Test successful authentication."""
        auth_service.setup_admin("test_password")
        
        result = auth_service.authenticate("test_password")
        
        assert result is True
    
    def test_authenticate_wrong_password(self, auth_service):
        """Test authentication with wrong password."""
        auth_service.setup_admin("correct_password")
        
        with pytest.raises(AuthenticationError, match="Invalid password"):
            auth_service.authenticate("wrong_password")
    
    def test_authenticate_lockout_after_max_attempts(self, auth_service):
        """Test account lockout after max failed attempts."""
        auth_service.setup_admin("password")
        auth_service.max_attempts = 3
        
        # Fail multiple times
        for _ in range(3):
            try:
                auth_service.authenticate("wrong")
            except AuthenticationError:
                pass
        
        # Account should be locked
        assert auth_service._is_locked("admin")
    
    def test_change_password(self, auth_service):
        """Test password change."""
        auth_service.setup_admin("old_password")
        
        auth_service.change_password("old_password", "new_password123")
        
        # Old password should fail
        with pytest.raises(AuthenticationError):
            auth_service.authenticate("old_password")
        
        # New password should work
        assert auth_service.authenticate("new_password123") is True
    
    def test_generate_session_token(self, auth_service):
        """Test session token generation."""
        token = auth_service.generate_session_token()
        
        assert isinstance(token, str)
        assert len(token) >= 32
    
    def test_validate_session_token(self, auth_service):
        """Test session token validation."""
        valid_token = auth_service.generate_session_token()
        
        assert auth_service.validate_session_token(valid_token) is True
        assert auth_service.validate_session_token("") is False
        assert auth_service.validate_session_token("invalid") is False


class TestModelService:
    """Tests for ModelService."""
    
    @pytest.fixture
    def model_service(self):
        """Create model service."""
        return ModelService()
    
    def test_get_all_models(self, model_service):
        """Test get_all_models returns default models."""
        models = model_service.get_all_models()
        
        assert len(models) > 0
        assert all(isinstance(m, AIModel) for m in models)
    
    def test_get_model(self, model_service):
        """Test get_model returns specific model."""
        model = model_service.get_model("ollama-llama3.2")
        
        assert model is not None
        assert model.name == "Llama 3.2"
    
    def test_get_model_not_found(self, model_service):
        """Test get_model raises error for unknown model."""
        with pytest.raises(ModelNotFoundError):
            model_service.get_model("nonexistent-model")
    
    def test_register_model(self, model_service):
        """Test registering a new model."""
        model = AIModel(
            id="test-model",
            name="Test Model",
            provider="test",
        )
        
        model_service.register_model(model)
        
        retrieved = model_service.get_model("test-model")
        assert retrieved.name == "Test Model"
    
    def test_unregister_model(self, model_service):
        """Test unregistering a model."""
        model = AIModel(id="to-remove", name="Remove Me", provider="test")
        model_service.register_model(model)
        
        model_service.unregister_model("to-remove")
        
        with pytest.raises(ModelNotFoundError):
            model_service.get_model("to-remove")
    
    def test_get_models_by_provider(self, model_service):
        """Test filtering models by provider."""
        models = model_service.get_models_by_provider("ollama")
        
        assert all(m.provider == "ollama" for m in models)
    
    def test_get_models_by_status(self, model_service):
        """Test filtering models by status."""
        models = model_service.get_models_by_status("running")
        
        assert all(m.status == "running" for m in models)
    
    def test_update_model_status(self, model_service):
        """Test updating model status."""
        model_service.update_model_status("ollama-llama3.2", "stopped")
        
        model = model_service.get_model("ollama-llama3.2")
        assert model.status == "stopped"
    
    def test_record_model_usage(self, model_service):
        """Test recording model usage."""
        model = model_service.get_model("ollama-llama3.2")
        initial_requests = model.total_requests
        
        model_service.record_model_usage("ollama-llama3.2")
        
        assert model.total_requests == initial_requests + 1


class TestAgentService:
    """Tests for AgentService."""
    
    @pytest.fixture
    def agent_service(self):
        """Create agent service."""
        return AgentService()
    
    def test_get_all_agents(self, agent_service):
        """Test get_all_agents returns default agents."""
        agents = agent_service.get_all_agents()
        
        assert len(agents) > 0
        assert all(isinstance(a, Agent) for a in agents)
    
    def test_get_agent(self, agent_service):
        """Test get_agent returns specific agent."""
        agent = agent_service.get_agent("agent-code")
        
        assert agent is not None
        assert agent.name == "Code Agent"
    
    def test_get_agent_not_found(self, agent_service):
        """Test get_agent raises error for unknown agent."""
        with pytest.raises(AgentNotFoundError):
            agent_service.get_agent("nonexistent-agent")
    
    def test_create_agent(self, agent_service):
        """Test creating a new agent."""
        agent = Agent(
            id="test-agent",
            name="Test Agent",
            role="testing",
        )
        
        agent_service.create_agent(agent)
        
        retrieved = agent_service.get_agent("test-agent")
        assert retrieved.name == "Test Agent"
    
    def test_delete_agent(self, agent_service):
        """Test deleting an agent."""
        agent = Agent(id="to-delete", name="Delete Me", role="test")
        agent_service.create_agent(agent)
        
        agent_service.delete_agent("to-delete")
        
        with pytest.raises(AgentNotFoundError):
            agent_service.get_agent("to-delete")
    
    def test_get_available_agents(self, agent_service):
        """Test getting available agents."""
        available = agent_service.get_available_agents()
        
        assert all(a.is_available for a in available)
    
    def test_assign_task(self, agent_service):
        """Test assigning a task to an agent."""
        # Find an idle agent
        idle_agents = agent_service.get_agents_by_status("idle")
        if idle_agents:
            agent = idle_agents[0]
            agent_service.assign_task(agent.id, "task-001")
            
            updated = agent_service.get_agent(agent.id)
            assert updated.status == "running"
            assert updated.current_task_id == "task-001"
    
    def test_assign_task_to_busy_agent(self, agent_service):
        """Test assigning task to busy agent raises error."""
        # Make an agent busy
        agent_service.update_agent_status("agent-code", "running")
        agent_service.get_agent("agent-code").current_task_id = "existing-task"
        
        with pytest.raises(AgentBusyError):
            agent_service.assign_task("agent-code", "new-task")
    
    def test_complete_task(self, agent_service):
        """Test completing a task."""
        agent = agent_service.get_agent("agent-code")
        agent.status = "running"
        agent.current_task_id = "task-001"
        initial_completed = agent.tasks_completed
        
        agent_service.complete_task("agent-code", success=True)
        
        assert agent.status == "idle"
        assert agent.current_task_id is None
        assert agent.tasks_completed == initial_completed + 1
    
    def test_get_agent_statistics(self, agent_service):
        """Test getting agent statistics."""
        stats = agent_service.get_agent_statistics()
        
        assert "total" in stats
        assert "running" in stats
        assert "idle" in stats
        assert "total_tasks_completed" in stats


class TestTaskService:
    """Tests for TaskService."""
    
    @pytest.fixture
    def task_service(self):
        """Create task service."""
        return TaskService()
    
    def test_create_task(self, task_service):
        """Test creating a task."""
        task = task_service.create_task(
            title="Test Task",
            description="Task description",
        )
        
        assert task.id is not None
        assert task.title == "Test Task"
        assert task.status == "pending"
    
    def test_get_task(self, task_service):
        """Test getting a task."""
        created = task_service.create_task(title="Test")
        
        task = task_service.get_task(created.id)
        
        assert task.title == "Test"
    
    def test_get_task_not_found(self, task_service):
        """Test getting nonexistent task."""
        with pytest.raises(TaskNotFoundError):
            task_service.get_task("nonexistent-task")
    
    def test_get_all_tasks(self, task_service):
        """Test getting all tasks."""
        task_service.create_task(title="Task 1")
        task_service.create_task(title="Task 2")
        
        tasks = task_service.get_all_tasks()
        
        assert len(tasks) >= 2
    
    def test_get_tasks_by_status(self, task_service):
        """Test filtering tasks by status."""
        task_service.create_task(title="Pending Task")
        
        pending = task_service.get_tasks_by_status("pending")
        
        assert all(t.status == "pending" for t in pending)
    
    def test_start_task(self, task_service):
        """Test starting a task."""
        task = task_service.create_task(title="Test")
        
        task_service.start_task(task.id, agent_id="agent-1")
        
        updated = task_service.get_task(task.id)
        assert updated.status == "running"
        assert updated.agent_id == "agent-1"
    
    def test_complete_task(self, task_service):
        """Test completing a task."""
        task = task_service.create_task(title="Test")
        task_service.start_task(task.id)
        
        task_service.complete_task(task.id, result="Success!")
        
        updated = task_service.get_task(task.id)
        assert updated.status == "completed"
        assert updated.result == "Success!"
        assert updated.progress == 100
    
    def test_fail_task(self, task_service):
        """Test failing a task."""
        task = task_service.create_task(title="Test")
        task_service.start_task(task.id)
        
        task_service.fail_task(task.id, error="Something went wrong")
        
        updated = task_service.get_task(task.id)
        assert updated.status == "failed"
        assert updated.error == "Something went wrong"
    
    def test_cancel_task(self, task_service):
        """Test cancelling a task."""
        task = task_service.create_task(title="Test")
        task_service.start_task(task.id)
        
        task_service.cancel_task(task.id)
        
        updated = task_service.get_task(task.id)
        assert updated.status == "cancelled"
    
    def test_update_task_progress(self, task_service):
        """Test updating task progress."""
        task = task_service.create_task(title="Test")
        task_service.start_task(task.id)
        
        task_service.update_task_progress(task.id, 50, message="Halfway")
        
        updated = task_service.get_task(task.id)
        assert updated.progress == 50
    
    def test_retry_task(self, task_service):
        """Test retrying a failed task."""
        task = task_service.create_task(title="Test")
        task_service.start_task(task.id)
        task_service.fail_task(task.id, error="Failed")
        
        task_service.retry_task(task.id)
        
        updated = task_service.get_task(task.id)
        assert updated.status == "pending"
        assert updated.retry_count == 1
    
    def test_clear_completed_tasks(self, task_service):
        """Test clearing completed tasks."""
        task1 = task_service.create_task(title="Completed")
        task2 = task_service.create_task(title="Running")
        task_service.start_task(task1.id)
        task_service.complete_task(task1.id)
        task_service.start_task(task2.id)
        
        cleared = task_service.clear_completed_tasks()
        
        assert cleared >= 1
        with pytest.raises(TaskNotFoundError):
            task_service.get_task(task1.id)
    
    def test_get_task_statistics(self, task_service):
        """Test getting task statistics."""
        stats = task_service.get_task_statistics()
        
        assert "total" in stats
        assert "pending" in stats
        assert "running" in stats
        assert "completed" in stats
        assert "failed" in stats
