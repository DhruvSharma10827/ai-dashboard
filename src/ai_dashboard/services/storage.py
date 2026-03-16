"""Storage service for AI Dashboard.

This module provides data persistence functionality using SQLite.

Example:
    >>> storage = StorageService()
    >>> storage.save_model(model)
    >>> model = storage.get_model("gpt-4")
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from ai_dashboard.core.config import CONFIG_DIR
from ai_dashboard.core.logging import get_logger
from ai_dashboard.models.agent import Agent
from ai_dashboard.models.ai_model import AIModel
from ai_dashboard.models.chat import ChatMessage
from ai_dashboard.models.chat import ChatSession
from ai_dashboard.models.task import Task
from ai_dashboard.models.user import User

logger = get_logger(__name__)

# Database path
DB_PATH = CONFIG_DIR / "ai_dashboard.db"


class StorageService:
    """Service for data persistence using SQLite.

    This service handles:
    - Database initialization
    - Model persistence
    - Agent persistence
    - Task persistence
    - Chat history persistence
    - User persistence

    Attributes:
        db_path: Path to SQLite database file.
    """

    def __init__(self, db_path: Path | None = None) -> None:
        """Initialize storage service.

        Args:
            db_path: Optional custom database path.
        """
        self.db_path = db_path or DB_PATH
        self._ensure_tables()

    @contextmanager
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection context manager.

        Yields:
            SQLite connection.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _ensure_tables(self) -> None:
        """Create database tables if they don't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Models table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS models (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model_type TEXT DEFAULT 'chat',
                    status TEXT DEFAULT 'available',
                    context_size INTEGER DEFAULT 4096,
                    supports_vision INTEGER DEFAULT 0,
                    supports_tools INTEGER DEFAULT 0,
                    supports_streaming INTEGER DEFAULT 1,
                    endpoint TEXT,
                    max_tokens INTEGER DEFAULT 4096,
                    temperature REAL DEFAULT 0.7,
                    created_at TEXT,
                    last_used TEXT,
                    total_requests INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)

            # Agents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    status TEXT DEFAULT 'idle',
                    model_id TEXT,
                    system_prompt TEXT,
                    tasks_completed INTEGER DEFAULT 0,
                    tasks_failed INTEGER DEFAULT 0,
                    current_task_id TEXT,
                    created_at TEXT,
                    last_active TEXT,
                    max_concurrent_tasks INTEGER DEFAULT 1,
                    priority INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)

            # Tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    priority TEXT DEFAULT 'normal',
                    agent_id TEXT,
                    created_at TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    result TEXT,
                    error TEXT,
                    progress INTEGER DEFAULT 0,
                    parent_task_id TEXT,
                    tags TEXT,
                    metadata TEXT,
                    max_retries INTEGER DEFAULT 3,
                    retry_count INTEGER DEFAULT 0,
                    timeout_seconds INTEGER DEFAULT 300
                )
            """)

            # Chat sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    model_id TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    message_count INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)

            # Chat messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    model_id TEXT,
                    created_at TEXT,
                    tokens INTEGER,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
                )
            """)

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT,
                    role TEXT DEFAULT 'user',
                    email TEXT,
                    created_at TEXT,
                    last_login TEXT,
                    login_count INTEGER DEFAULT 0,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until TEXT,
                    preferences TEXT,
                    metadata TEXT
                )
            """)

            logger.debug("Database tables initialized")

    # Model operations

    def save_model(self, model: AIModel) -> None:
        """Save a model to the database.

        Args:
            model: Model to save.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO models (
                    id, name, provider, model_type, status, context_size,
                    supports_vision, supports_tools, supports_streaming,
                    endpoint, max_tokens, temperature, created_at, last_used,
                    total_requests, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    model.id,
                    model.name,
                    model.provider,
                    model.model_type,
                    model.status,
                    model.context_size,
                    int(model.supports_vision),
                    int(model.supports_tools),
                    int(model.supports_streaming),
                    model.endpoint,
                    model.max_tokens,
                    model.temperature,
                    model.created_at.isoformat() if model.created_at else None,
                    model.last_used.isoformat() if model.last_used else None,
                    model.total_requests,
                    json.dumps(model.metadata) if model.metadata else None,
                ),
            )
        logger.debug(f"Saved model: {model.id}")

    def get_model(self, model_id: str) -> AIModel | None:
        """Get a model from the database.

        Args:
            model_id: Model ID.

        Returns:
            Model instance or None.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM models WHERE id = ?", (model_id,))
            row = cursor.fetchone()

        if row:
            return self._row_to_model(row)
        return None

    def get_all_models(self) -> list[AIModel]:
        """Get all models from the database.

        Returns:
            List of models.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM models")
            rows = cursor.fetchall()

        return [self._row_to_model(row) for row in rows]

    def delete_model(self, model_id: str) -> None:
        """Delete a model from the database.

        Args:
            model_id: Model ID.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM models WHERE id = ?", (model_id,))
        logger.debug(f"Deleted model: {model_id}")

    # Agent operations

    def save_agent(self, agent: Agent) -> None:
        """Save an agent to the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO agents (
                    id, name, role, status, model_id, system_prompt,
                    tasks_completed, tasks_failed, current_task_id,
                    created_at, last_active, max_concurrent_tasks,
                    priority, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    agent.id,
                    agent.name,
                    agent.role,
                    agent.status,
                    agent.model_id,
                    agent.system_prompt,
                    agent.tasks_completed,
                    agent.tasks_failed,
                    agent.current_task_id,
                    agent.created_at.isoformat() if agent.created_at else None,
                    agent.last_active.isoformat() if agent.last_active else None,
                    agent.max_concurrent_tasks,
                    agent.priority,
                    json.dumps(agent.metadata) if agent.metadata else None,
                ),
            )
        logger.debug(f"Saved agent: {agent.id}")

    def get_agent(self, agent_id: str) -> Agent | None:
        """Get an agent from the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
            row = cursor.fetchone()

        if row:
            return self._row_to_agent(row)
        return None

    def get_all_agents(self) -> list[Agent]:
        """Get all agents from the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agents")
            rows = cursor.fetchall()

        return [self._row_to_agent(row) for row in rows]

    # Task operations

    def save_task(self, task: Task) -> None:
        """Save a task to the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO tasks (
                    id, title, description, status, priority, agent_id,
                    created_at, started_at, completed_at, result, error,
                    progress, parent_task_id, tags, metadata,
                    max_retries, retry_count, timeout_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task.id,
                    task.title,
                    task.description,
                    task.status,
                    task.priority,
                    task.agent_id,
                    task.created_at.isoformat() if task.created_at else None,
                    task.started_at.isoformat() if task.started_at else None,
                    task.completed_at.isoformat() if task.completed_at else None,
                    task.result,
                    task.error,
                    task.progress,
                    task.parent_task_id,
                    json.dumps(task.tags) if task.tags else None,
                    json.dumps(task.metadata) if task.metadata else None,
                    task.max_retries,
                    task.retry_count,
                    task.timeout_seconds,
                ),
            )
        logger.debug(f"Saved task: {task.id}")

    def get_task(self, task_id: str) -> Task | None:
        """Get a task from the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()

        if row:
            return self._row_to_task(row)
        return None

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks from the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks")
            rows = cursor.fetchall()

        return [self._row_to_task(row) for row in rows]

    # Chat operations

    def save_chat_session(self, session: ChatSession) -> None:
        """Save a chat session to the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO chat_sessions (
                    id, name, model_id, created_at, updated_at,
                    message_count, total_tokens, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    session.id,
                    session.name,
                    session.model_id,
                    session.created_at.isoformat() if session.created_at else None,
                    session.updated_at.isoformat() if session.updated_at else None,
                    session.message_count,
                    session.total_tokens,
                    json.dumps(session.metadata) if session.metadata else None,
                ),
            )

    def save_chat_message(self, message: ChatMessage) -> int:
        """Save a chat message and return its ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO chat_messages (
                    session_id, role, content, model_id, created_at, tokens, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    message.session_id,
                    message.role,
                    message.content,
                    message.model_id,
                    message.created_at.isoformat() if message.created_at else None,
                    message.tokens,
                    json.dumps(message.metadata) if message.metadata else None,
                ),
            )
            return cursor.lastrowid or 0

    # User operations

    def save_user(self, user: User) -> None:
        """Save a user to the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO users (
                    id, username, password_hash, salt, role, email,
                    created_at, last_login, login_count, failed_login_attempts,
                    locked_until, preferences, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    user.id,
                    user.username,
                    user.password_hash,
                    user.salt,
                    user.role,
                    user.email,
                    user.created_at.isoformat() if user.created_at else None,
                    user.last_login.isoformat() if user.last_login else None,
                    user.login_count,
                    user.failed_login_attempts,
                    user.locked_until.isoformat() if user.locked_until else None,
                    json.dumps(user.preferences) if user.preferences else None,
                    json.dumps(user.metadata) if user.metadata else None,
                ),
            )

    def get_user_by_username(self, username: str) -> User | None:
        """Get a user by username."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()

        if row:
            return self._row_to_user(row)
        return None

    # Helper methods

    def _row_to_model(self, row: sqlite3.Row) -> AIModel:
        """Convert database row to AIModel."""
        return AIModel(
            id=row["id"],
            name=row["name"],
            provider=row["provider"],
            model_type=row["model_type"],
            status=row["status"],
            context_size=row["context_size"],
            supports_vision=bool(row["supports_vision"]),
            supports_tools=bool(row["supports_tools"]),
            supports_streaming=bool(row["supports_streaming"]),
            endpoint=row["endpoint"],
            max_tokens=row["max_tokens"],
            temperature=row["temperature"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            last_used=datetime.fromisoformat(row["last_used"]) if row["last_used"] else None,
            total_requests=row["total_requests"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )

    def _row_to_agent(self, row: sqlite3.Row) -> Agent:
        """Convert database row to Agent."""
        return Agent(
            id=row["id"],
            name=row["name"],
            role=row["role"],
            status=row["status"],
            model_id=row["model_id"],
            system_prompt=row["system_prompt"],
            tasks_completed=row["tasks_completed"],
            tasks_failed=row["tasks_failed"],
            current_task_id=row["current_task_id"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            last_active=datetime.fromisoformat(row["last_active"]) if row["last_active"] else None,
            max_concurrent_tasks=row["max_concurrent_tasks"],
            priority=row["priority"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        """Convert database row to Task."""
        return Task(
            id=row["id"],
            title=row["title"],
            description=row["description"] or "",
            status=row["status"],
            priority=row["priority"],
            agent_id=row["agent_id"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            started_at=datetime.fromisoformat(row["started_at"]) if row["started_at"] else None,
            completed_at=(
                datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
            ),
            result=row["result"],
            error=row["error"],
            progress=row["progress"],
            parent_task_id=row["parent_task_id"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            max_retries=row["max_retries"],
            retry_count=row["retry_count"],
            timeout_seconds=row["timeout_seconds"],
        )

    def _row_to_user(self, row: sqlite3.Row) -> User:
        """Convert database row to User."""
        return User(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
            salt=row["salt"],
            role=row["role"],
            email=row["email"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            last_login=datetime.fromisoformat(row["last_login"]) if row["last_login"] else None,
            login_count=row["login_count"],
            failed_login_attempts=row["failed_login_attempts"],
            locked_until=(
                datetime.fromisoformat(row["locked_until"]) if row["locked_until"] else None
            ),
            preferences=json.loads(row["preferences"]) if row["preferences"] else {},
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )
