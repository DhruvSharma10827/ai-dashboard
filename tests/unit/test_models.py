"""Unit tests for AI Dashboard models."""

import pytest
from datetime import datetime

from ai_dashboard.models.ai_model import AIModel, ModelStatus, ModelType, ModelProvider
from ai_dashboard.models.agent import Agent, AgentStatus, AgentRole
from ai_dashboard.models.task import Task, TaskStatus, TaskPriority
from ai_dashboard.models.chat import ChatMessage, ChatSession
from ai_dashboard.models.user import User, UserRole


class TestAIModel:
    """Tests for AIModel dataclass."""
    
    def test_create_model_with_defaults(self):
        """Test creating a model with default values."""
        model = AIModel(
            id="test-model",
            name="Test Model",
            provider="openai",
        )
        
        assert model.id == "test-model"
        assert model.name == "Test Model"
        assert model.provider == "openai"
        assert model.model_type == "chat"
        assert model.status == "available"
        assert model.context_size == 4096
        assert model.supports_vision is False
        assert model.supports_tools is False
    
    def test_create_model_with_custom_values(self):
        """Test creating a model with custom values."""
        model = AIModel(
            id="gpt-4-vision",
            name="GPT-4 Vision",
            provider="openai",
            model_type="chat",
            status="running",
            context_size=128000,
            supports_vision=True,
            supports_tools=True,
            temperature=0.5,
            max_tokens=8192,
        )
        
        assert model.id == "gpt-4-vision"
        assert model.status == "running"
        assert model.context_size == 128000
        assert model.supports_vision is True
        assert model.supports_tools is True
        assert model.temperature == 0.5
        assert model.max_tokens == 8192
    
    def test_model_is_local(self):
        """Test is_local property."""
        local_model = AIModel(id="llama", name="Llama", provider="ollama")
        cloud_model = AIModel(id="gpt-4", name="GPT-4", provider="openai")
        
        assert local_model.is_local is True
        assert cloud_model.is_local is False
    
    def test_model_context_size_display(self):
        """Test context_size_display property."""
        model_4k = AIModel(id="m1", name="M1", provider="test", context_size=4096)
        model_128k = AIModel(id="m2", name="M2", provider="test", context_size=128000)
        model_200k = AIModel(id="m3", name="M3", provider="test", context_size=200000)
        
        assert model_4k.context_size_display == "4K"
        assert model_128k.context_size_display == "128K"
        assert model_200k.context_size_display == "200K"
    
    def test_model_capabilities(self):
        """Test capabilities property."""
        model = AIModel(
            id="test",
            name="Test",
            provider="test",
            supports_vision=True,
            supports_tools=True,
            supports_streaming=True,
        )
        
        assert "Vision" in model.capabilities
        assert "Tools" in model.capabilities
        assert "Streaming" in model.capabilities
    
    def test_model_to_dict(self):
        """Test to_dict serialization."""
        model = AIModel(id="test", name="Test", provider="openai")
        data = model.to_dict()
        
        assert isinstance(data, dict)
        assert data["id"] == "test"
        assert data["name"] == "Test"
        assert "created_at" in data
    
    def test_model_from_dict(self):
        """Test from_dict deserialization."""
        data = {
            "id": "test",
            "name": "Test Model",
            "provider": "anthropic",
            "context_size": 100000,
        }
        model = AIModel.from_dict(data)
        
        assert model.id == "test"
        assert model.name == "Test Model"
        assert model.provider == "anthropic"
        assert model.context_size == 100000
    
    def test_model_update_usage(self):
        """Test update_usage method."""
        model = AIModel(id="test", name="Test", provider="test")
        initial_requests = model.total_requests
        
        model.update_usage()
        
        assert model.total_requests == initial_requests + 1
        assert model.last_used is not None


class TestAgent:
    """Tests for Agent dataclass."""
    
    def test_create_agent_with_defaults(self):
        """Test creating an agent with default values."""
        agent = Agent(
            id="test-agent",
            name="Test Agent",
            role="code",
        )
        
        assert agent.id == "test-agent"
        assert agent.name == "Test Agent"
        assert agent.role == "code"
        assert agent.status == "idle"
        assert agent.tasks_completed == 0
    
    def test_agent_is_available(self):
        """Test is_available property."""
        idle_agent = Agent(id="a1", name="A1", role="code", status="idle")
        running_agent = Agent(
            id="a2", name="A2", role="code",
            status="running",
            current_task_id="task-1",
        )
        
        assert idle_agent.is_available is True
        assert running_agent.is_available is False
    
    def test_agent_success_rate(self):
        """Test success_rate property."""
        agent = Agent(
            id="test",
            name="Test",
            role="code",
            tasks_completed=8,
            tasks_failed=2,
        )
        
        assert agent.success_rate == 0.8
    
    def test_agent_start_task(self):
        """Test start_task method."""
        agent = Agent(id="test", name="Test", role="code")
        
        agent.start_task("task-001")
        
        assert agent.status == "running"
        assert agent.current_task_id == "task-001"
        assert agent.last_active is not None
    
    def test_agent_complete_task(self):
        """Test complete_task method."""
        agent = Agent(id="test", name="Test", role="code")
        agent.start_task("task-001")
        
        agent.complete_task(success=True)
        
        assert agent.status == "idle"
        assert agent.current_task_id is None
        assert agent.tasks_completed == 1


class TestTask:
    """Tests for Task dataclass."""
    
    def test_create_task_with_defaults(self):
        """Test creating a task with default values."""
        task = Task(id="task-1", title="Test Task")
        
        assert task.id == "task-1"
        assert task.title == "Test Task"
        assert task.status == "pending"
        assert task.priority == "normal"
        assert task.progress == 0
    
    def test_task_duration_seconds(self):
        """Test duration_seconds property."""
        task = Task(id="t1", title="T1")
        
        # No duration if not started
        assert task.duration_seconds is None
        
        # Duration after start
        task.start()
        assert task.duration_seconds is not None
        assert task.duration_seconds >= 0
    
    def test_task_is_complete(self):
        """Test is_complete property."""
        pending = Task(id="t1", title="T1", status="pending")
        completed = Task(id="t2", title="T2", status="completed")
        failed = Task(id="t3", title="T3", status="failed")
        
        assert pending.is_complete is False
        assert completed.is_complete is True
        assert failed.is_complete is True
    
    def test_task_can_retry(self):
        """Test can_retry property."""
        task = Task(id="t1", title="T1", status="failed", max_retries=3, retry_count=1)
        
        assert task.can_retry is True
        
        task.retry_count = 3
        assert task.can_retry is False
    
    def test_task_start(self):
        """Test start method."""
        task = Task(id="t1", title="T1")
        
        task.start(agent_id="agent-1")
        
        assert task.status == "running"
        assert task.agent_id == "agent-1"
        assert task.started_at is not None
    
    def test_task_complete(self):
        """Test complete method."""
        task = Task(id="t1", title="T1")
        task.start()
        
        task.complete(result="Success!")
        
        assert task.status == "completed"
        assert task.result == "Success!"
        assert task.progress == 100
        assert task.completed_at is not None
    
    def test_task_fail(self):
        """Test fail method."""
        task = Task(id="t1", title="T1")
        task.start()
        
        task.fail(error="Something went wrong")
        
        assert task.status == "failed"
        assert task.error == "Something went wrong"
    
    def test_task_update_progress(self):
        """Test update_progress method."""
        task = Task(id="t1", title="T1")
        
        task.update_progress(50, message="Halfway there!")
        
        assert task.progress == 50
        assert task.metadata.get("progress_message") == "Halfway there!"


class TestChatModels:
    """Tests for Chat models."""
    
    def test_chat_message_creation(self):
        """Test ChatMessage creation."""
        msg = ChatMessage(
            session_id="session-1",
            role="user",
            content="Hello!",
        )
        
        assert msg.session_id == "session-1"
        assert msg.role == "user"
        assert msg.content == "Hello!"
        assert msg.created_at is not None
    
    def test_chat_session_creation(self):
        """Test ChatSession creation."""
        session = ChatSession(id="session-1", name="New Chat")
        
        assert session.id == "session-1"
        assert session.name == "New Chat"
        assert session.message_count == 0
        assert session.created_at is not None
    
    def test_chat_session_add_message(self):
        """Test ChatSession add_message method."""
        session = ChatSession(id="s1")
        
        session.add_message(tokens=100)
        
        assert session.message_count == 1
        assert session.total_tokens == 100


class TestUser:
    """Tests for User model."""
    
    def test_create_user(self):
        """Test User creation."""
        user = User(
            id=1,
            username="admin",
            role="admin",
        )
        
        assert user.id == 1
        assert user.username == "admin"
        assert user.is_admin is True
    
    def test_user_has_permission(self):
        """Test has_permission method."""
        admin = User(id=1, username="admin", role="admin")
        viewer = User(id=2, username="viewer", role="viewer")
        
        assert admin.has_permission("manage_users") is True
        assert viewer.has_permission("manage_users") is False
        assert viewer.has_permission("read") is True
    
    def test_user_record_login(self):
        """Test record_login method."""
        user = User(id=1, username="test")
        
        user.record_login(success=True)
        
        assert user.login_count == 1
        assert user.last_login is not None
        assert user.failed_login_attempts == 0
    
    def test_user_lock_account(self):
        """Test lock_account method."""
        user = User(id=1, username="test")
        
        user.lock_account(minutes=30)
        
        assert user.is_locked is True
    
    def test_user_unlock_account(self):
        """Test unlock_account method."""
        user = User(id=1, username="test")
        user.lock_account()
        
        user.unlock_account()
        
        assert user.is_locked is False
        assert user.failed_login_attempts == 0
