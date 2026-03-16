"""Core module for AI Dashboard."""

from ai_dashboard.core.config import Config
from ai_dashboard.core.config import get_config
from ai_dashboard.core.config import save_config
from ai_dashboard.core.exceptions import AgentError
from ai_dashboard.core.exceptions import AIDashboardError
from ai_dashboard.core.exceptions import AuthenticationError
from ai_dashboard.core.exceptions import ConfigurationError
from ai_dashboard.core.exceptions import ModelError
from ai_dashboard.core.exceptions import TaskError
from ai_dashboard.core.logging import get_logger
from ai_dashboard.core.logging import setup_logging

__all__ = [
    "AIDashboardError",
    "AgentError",
    "AuthenticationError",
    "Config",
    "ConfigurationError",
    "ModelError",
    "TaskError",
    "get_config",
    "get_logger",
    "save_config",
    "setup_logging",
]
