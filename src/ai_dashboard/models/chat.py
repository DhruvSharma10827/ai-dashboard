"""Chat data models.

This module defines data models for chat functionality,
including messages and sessions.

Example:
    >>> session = ChatSession(id="session-001", name="New Chat")
    >>> message = ChatMessage(
    ...     session_id="session-001",
    ...     role="user",
    ...     content="Hello!",
    ... )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class MessageRole(Enum):
    """Enumeration of chat message roles.
    
    Attributes:
        SYSTEM: System message (instructions).
        USER: User message.
        ASSISTANT: AI assistant message.
        TOOL: Tool/function message.
    """
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def icon(self) -> str:
        """Get the icon for this role."""
        icons = {
            MessageRole.SYSTEM: "⚙️",
            MessageRole.USER: "👤",
            MessageRole.ASSISTANT: "🤖",
            MessageRole.TOOL: "🔧",
        }
        return icons.get(self, "💬")


@dataclass
class ChatMessage:
    """Chat message representation.
    
    This class represents a single message in a chat session.
    
    Attributes:
        id: Unique message identifier.
        session_id: ID of the chat session.
        role: Message role (user, assistant, system).
        content: Message content.
        model_id: ID of the model that generated this message.
        created_at: When the message was created.
        tokens: Number of tokens in the message.
        metadata: Additional metadata.
    """
    id: Optional[int] = None
    session_id: str = ""
    role: str = "user"
    content: str = ""
    model_id: Optional[str] = None
    created_at: Optional[datetime] = None
    tokens: Optional[int] = None
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Initialize default values after creation."""
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def role_icon(self) -> str:
        """Get the icon for this message's role."""
        try:
            role = MessageRole(self.role)
            return role.icon
        except ValueError:
            return "💬"
    
    def to_dict(self) -> dict:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "model_id": self.model_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "tokens": self.tokens,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> ChatMessage:
        """Create message from dictionary."""
        if data.get("created_at"):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


@dataclass
class ChatSession:
    """Chat session representation.
    
    This class represents a chat session with its metadata
    and message history.
    
    Attributes:
        id: Unique session identifier.
        name: Session name/title.
        model_id: ID of the model used in this session.
        created_at: When the session was created.
        updated_at: When the session was last updated.
        message_count: Number of messages in the session.
        total_tokens: Total tokens used in the session.
        metadata: Additional metadata.
    """
    id: str = ""
    name: str = "New Chat"
    model_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    message_count: int = 0
    total_tokens: int = 0
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Initialize default values after creation."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def update(self) -> None:
        """Update the session's updated_at timestamp."""
        self.updated_at = datetime.now()
    
    def add_message(self, tokens: int = 0) -> None:
        """Record a new message in the session.
        
        Args:
            tokens: Number of tokens in the message.
        """
        self.message_count += 1
        self.total_tokens += tokens
        self.update()
    
    def to_dict(self) -> dict:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "model_id": self.model_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "message_count": self.message_count,
            "total_tokens": self.total_tokens,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> ChatSession:
        """Create session from dictionary."""
        for field_name in ["created_at", "updated_at"]:
            if data.get(field_name):
                data[field_name] = datetime.fromisoformat(data[field_name])
        return cls(**data)
