"""Pytest configuration and fixtures for AI Dashboard tests."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import Mock

import pytest

from ai_dashboard.core.config import Config
from ai_dashboard.services.agent_service import AgentService
from ai_dashboard.services.auth import AuthService
from ai_dashboard.services.model_service import ModelService
from ai_dashboard.services.storage import StorageService
from ai_dashboard.services.task_service import TaskService

# Configure pytest
# pytest_plugins = ["pytest_benchmark"]  # Optional, uncomment if needed


# ============================================================================
# Command-line options
# ============================================================================


def pytest_addoption(parser):
    """Add custom command-line options."""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests",
    )
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests",
    )


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "slow: mark test as slow")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "security: mark test as security test")
    config.addinivalue_line("markers", "performance: mark test as performance test")


def pytest_collection_modifyitems(config, items):
    """Skip tests based on markers and options."""
    skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
    skip_integration = pytest.mark.skip(reason="need --run-integration option to run")

    for item in items:
        if "slow" in item.keywords and not config.getoption("--run-slow"):
            item.add_marker(skip_slow)
        if "integration" in item.keywords and not config.getoption("--run-integration"):
            item.add_marker(skip_integration)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_config_file(temp_dir):
    """Create a temporary config file."""
    return temp_dir / "config.json"


@pytest.fixture
def temp_db(temp_dir):
    """Create a temporary database file."""
    return temp_dir / "test.db"


# ============================================================================
# Config Fixtures
# ============================================================================


@pytest.fixture
def config():
    """Create a fresh Config instance."""
    return Config()


@pytest.fixture
def config_with_temp_dir(temp_dir, monkeypatch):
    """Create config with temporary directory."""
    monkeypatch.setattr("ai_dashboard.core.config.CONFIG_DIR", temp_dir)
    monkeypatch.setattr("ai_dashboard.core.config.CONFIG_FILE", temp_dir / "config.json")
    return Config()


# ============================================================================
# Service Fixtures
# ============================================================================


@pytest.fixture
def auth_service(config):
    """Create an AuthService instance."""
    return AuthService(config=config)


@pytest.fixture
def auth_service_authenticated(auth_service):
    """Create an authenticated AuthService."""
    auth_service.setup_admin("test_password_123")
    return auth_service


@pytest.fixture
def model_service():
    """Create a ModelService instance."""
    return ModelService()


@pytest.fixture
def agent_service():
    """Create an AgentService instance."""
    return AgentService()


@pytest.fixture
def task_service():
    """Create a TaskService instance."""
    return TaskService()


@pytest.fixture
def storage_service(temp_db):
    """Create a StorageService instance with temp database."""
    return StorageService(db_path=temp_db)


@pytest.fixture
def all_services(config, temp_db):
    """Create all services for integration tests."""
    return {
        "config": config,
        "auth": AuthService(config=config),
        "models": ModelService(),
        "agents": AgentService(),
        "tasks": TaskService(),
        "storage": StorageService(db_path=temp_db),
    }


# ============================================================================
# Model Fixtures
# ============================================================================


@pytest.fixture
def sample_model():
    """Create a sample AIModel."""
    from ai_dashboard.models.ai_model import AIModel

    return AIModel(
        id="test-model-001",
        name="Test Model",
        provider="test",
        model_type="chat",
        status="available",
        context_size=8192,
        supports_vision=False,
        supports_tools=True,
    )


@pytest.fixture
def sample_agent():
    """Create a sample Agent."""
    from ai_dashboard.models.agent import Agent

    return Agent(
        id="test-agent-001",
        name="Test Agent",
        role="code",
        status="idle",
        tasks_completed=0,
        model_id="test-model-001",
    )


@pytest.fixture
def sample_task():
    """Create a sample Task."""
    from ai_dashboard.models.task import Task

    return Task(
        id="test-task-001",
        title="Test Task",
        description="A task for testing",
        status="pending",
        priority="normal",
    )


@pytest.fixture
def sample_models():
    """Create multiple sample models."""
    from ai_dashboard.models.ai_model import AIModel

    return [
        AIModel(
            id=f"model-{i:03d}",
            name=f"Model {i}",
            provider="ollama" if i < 3 else "openai",
            context_size=4096 * (i + 1),
        )
        for i in range(5)
    ]


@pytest.fixture
def sample_agents():
    """Create multiple sample agents."""
    from ai_dashboard.models.agent import Agent

    roles = ["code", "research", "task", "chat"]
    return [
        Agent(
            id=f"agent-{i:03d}",
            name=f"Agent {i}",
            role=roles[i % len(roles)],
            status="idle" if i % 2 == 0 else "running",
        )
        for i in range(4)
    ]


# ============================================================================
# Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_app():
    """Create a mock application instance."""
    app = Mock()
    app.config = Config()
    app.model_service = ModelService()
    app.agent_service = AgentService()
    app.task_service = TaskService()
    return app


@pytest.fixture
def mock_storage():
    """Create a mock storage service."""
    storage = Mock(spec=StorageService)
    storage.save_model = Mock()
    storage.get_model = Mock(return_value=None)
    storage.save_agent = Mock()
    storage.get_agent = Mock(return_value=None)
    storage.save_task = Mock()
    storage.get_task = Mock(return_value=None)
    return storage


# ============================================================================
# Helper Fixtures
# ============================================================================


@pytest.fixture
def assert_no_errors():
    """Helper to assert no errors in result."""

    def _assert(result):
        assert result is not None
        if hasattr(result, "error"):
            assert result.error is None
        if hasattr(result, "errors"):
            assert len(result.errors) == 0

    return _assert


@pytest.fixture
def wait_for_condition():
    """Helper to wait for a condition to be true."""
    import time

    def _wait(condition, timeout=5, interval=0.1):
        start = time.time()
        while time.time() - start < timeout:
            if condition():
                return True
            time.sleep(interval)
        return False

    return _wait


# ============================================================================
# Cleanup Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def cleanup_config():
    """Cleanup config after each test."""
    yield

    # Reset global config
    from ai_dashboard.core import config as config_module

    config_module._config = None


@pytest.fixture(autouse=True)
def cleanup_services():
    """Cleanup services after each test."""
    yield

    # Reset service instances if needed
    pass
