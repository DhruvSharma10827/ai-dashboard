"""Screens module for AI Dashboard."""

from ai_dashboard.screens.login import LoginScreen
from ai_dashboard.screens.dashboard import DashboardScreen
from ai_dashboard.screens.models import ModelsScreen
from ai_dashboard.screens.agents import AgentsScreen
from ai_dashboard.screens.chat import ChatScreen
from ai_dashboard.screens.tasks import TasksScreen
from ai_dashboard.screens.settings import SettingsScreen

__all__ = [
    "LoginScreen",
    "DashboardScreen",
    "ModelsScreen",
    "AgentsScreen",
    "ChatScreen",
    "TasksScreen",
    "SettingsScreen",
]
