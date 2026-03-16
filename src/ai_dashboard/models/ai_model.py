"""AI Model data model.

This module defines the AIModel dataclass and related enums for
representing AI model configurations and their states.

Example:
    >>> model = AIModel(
    ...     id="gpt-4",
    ...     name="GPT-4 Turbo",
    ...     provider="openai",
    ...     context_size=128000,
    ...     supports_vision=True,
    ... )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ModelStatus(Enum):
    """Enumeration of possible model states.
    
    Attributes:
        AVAILABLE: Model is available for use.
        RUNNING: Model is currently running.
        STOPPED: Model is stopped.
        ERROR: Model has an error.
        LOADING: Model is loading.
    """
    AVAILABLE = "available"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    LOADING = "loading"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def icon(self) -> str:
        """Get the icon for this status."""
        icons = {
            ModelStatus.AVAILABLE: "🟢",
            ModelStatus.RUNNING: "🔵",
            ModelStatus.STOPPED: "⚪",
            ModelStatus.ERROR: "🔴",
            ModelStatus.LOADING: "🟡",
        }
        return icons.get(self, "⚪")


class ModelType(Enum):
    """Enumeration of model types.
    
    Attributes:
        CHAT: Chat/completion model.
        EMBEDDING: Embedding model.
        IMAGE: Image generation model.
        AUDIO: Audio processing model.
        VISION: Vision/image understanding model.
    """
    CHAT = "chat"
    EMBEDDING = "embedding"
    IMAGE = "image"
    AUDIO = "audio"
    VISION = "vision"
    
    def __str__(self) -> str:
        return self.value


class ModelProvider(Enum):
    """Enumeration of AI providers.
    
    Attributes:
        OLLAMA: Ollama local models.
        OPENAI: OpenAI API.
        ANTHROPIC: Anthropic Claude API.
        GOOGLE: Google Gemini API.
        GROQ: Groq API.
        OPENROUTER: OpenRouter API.
        LOCALAI: LocalAI server.
        LLAMACPP: llama.cpp server.
    """
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROQ = "groq"
    OPENROUTER = "openrouter"
    LOCALAI = "localai"
    LLAMACPP = "llamacpp"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def display_name(self) -> str:
        """Get the display name for this provider."""
        names = {
            ModelProvider.OLLAMA: "Ollama",
            ModelProvider.OPENAI: "OpenAI",
            ModelProvider.ANTHROPIC: "Anthropic",
            ModelProvider.GOOGLE: "Google",
            ModelProvider.GROQ: "Groq",
            ModelProvider.OPENROUTER: "OpenRouter",
            ModelProvider.LOCALAI: "LocalAI",
            ModelProvider.LLAMACPP: "Llama.cpp",
        }
        return names.get(self, self.value)


@dataclass
class AIModel:
    """AI Model configuration and metadata.
    
    This class represents an AI model with all its configuration
    options, capabilities, and state information.
    
    Attributes:
        id: Unique identifier for the model.
        name: Human-readable model name.
        provider: Model provider (e.g., 'openai', 'ollama').
        model_type: Type of model (chat, embedding, etc.).
        status: Current status of the model.
        context_size: Maximum context window size in tokens.
        supports_vision: Whether the model supports vision/image input.
        supports_tools: Whether the model supports function calling.
        supports_streaming: Whether the model supports streaming output.
        endpoint: API endpoint URL (for local models).
        api_key_name: Environment variable name for API key.
        max_tokens: Maximum output tokens.
        temperature: Default temperature for generation.
        created_at: When the model was added.
        last_used: When the model was last used.
        total_requests: Total number of requests made.
        metadata: Additional metadata.
    
    Example:
        >>> model = AIModel(
        ...     id="gpt-4-turbo",
        ...     name="GPT-4 Turbo",
        ...     provider="openai",
        ...     context_size=128000,
        ...     supports_vision=True,
        ...     supports_tools=True,
        ... )
    """
    id: str
    name: str
    provider: str
    model_type: str = "chat"
    status: str = "available"
    context_size: int = 4096
    supports_vision: bool = False
    supports_tools: bool = False
    supports_streaming: bool = True
    endpoint: Optional[str] = None
    api_key_name: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    created_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    total_requests: int = 0
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Initialize default values after creation."""
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def context_size_display(self) -> str:
        """Get human-readable context size."""
        if self.context_size >= 1_000_000:
            return f"{self.context_size // 1000}K"
        elif self.context_size >= 1000:
            return f"{self.context_size // 1000}K"
        return str(self.context_size)
    
    @property
    def is_local(self) -> bool:
        """Check if this is a local model."""
        return self.provider in ("ollama", "localai", "llamacpp")
    
    @property
    def capabilities(self) -> list[str]:
        """Get list of model capabilities."""
        caps = []
        if self.supports_vision:
            caps.append("Vision")
        if self.supports_tools:
            caps.append("Tools")
        if self.supports_streaming:
            caps.append("Streaming")
        return caps
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "model_type": self.model_type,
            "status": self.status,
            "context_size": self.context_size,
            "supports_vision": self.supports_vision,
            "supports_tools": self.supports_tools,
            "supports_streaming": self.supports_streaming,
            "endpoint": self.endpoint,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "total_requests": self.total_requests,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> AIModel:
        """Create model from dictionary."""
        # Handle datetime fields
        if data.get("created_at"):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("last_used"):
            data["last_used"] = datetime.fromisoformat(data["last_used"])
        return cls(**data)
    
    def update_usage(self) -> None:
        """Update usage statistics."""
        self.last_used = datetime.now()
        self.total_requests += 1
