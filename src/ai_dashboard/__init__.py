"""AI Dashboard - Enterprise AI Orchestration System.

A professional, production-grade TUI for managing AI models, agents, and workflows.
"""

from ai_dashboard.core.config import Config, get_config
from ai_dashboard.core.exceptions import AIDashboardError
from ai_dashboard.models.agent import Agent
from ai_dashboard.models.ai_model import AIModel
from ai_dashboard.models.task import Task

__version__ = "1.0.0"
__author__ = "AI Dashboard Team"
__email__ = "team@ai-dashboard.dev"

__all__ = [
    "Config",
    "get_config",
    "AIDashboardError",
    "Agent",
    "AIModel",
    "Task",
    "__version__",
]
