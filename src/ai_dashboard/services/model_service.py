"""Model service for AI Dashboard.

This module provides model management functionality,
including registration, status tracking, and configuration.

Example:
    >>> service = ModelService()
    >>> service.register_model(AIModel(id="gpt-4", name="GPT-4", provider="openai"))
    >>> model = service.get_model("gpt-4")
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from ai_dashboard.core.exceptions import ModelError, ModelNotFoundError
from ai_dashboard.core.logging import get_logger
from ai_dashboard.models.ai_model import AIModel

logger = get_logger(__name__)


class ModelService:
    """Service for managing AI models.
    
    This service handles:
    - Model registration and removal
    - Model status tracking
    - Model configuration
    - Usage statistics
    
    Attributes:
        models: Dictionary of registered models.
    """
    
    def __init__(self) -> None:
        """Initialize model service with default models."""
        self._models: dict[str, AIModel] = {}
        self._initialize_default_models()
    
    def _initialize_default_models(self) -> None:
        """Initialize default AI models."""
        default_models = [
            AIModel(
                id="ollama-llama3.2",
                name="Llama 3.2",
                provider="ollama",
                model_type="chat",
                status="running",
                context_size=128000,
                supports_vision=False,
                supports_tools=True,
                supports_streaming=True,
            ),
            AIModel(
                id="ollama-mistral",
                name="Mistral",
                provider="ollama",
                model_type="chat",
                status="running",
                context_size=32000,
                supports_vision=False,
                supports_tools=True,
            ),
            AIModel(
                id="ollama-codellama",
                name="CodeLlama",
                provider="ollama",
                model_type="chat",
                status="available",
                context_size=16384,
                supports_vision=False,
                supports_tools=False,
            ),
            AIModel(
                id="openai-gpt4",
                name="GPT-4 Turbo",
                provider="openai",
                model_type="chat",
                status="available",
                context_size=128000,
                supports_vision=True,
                supports_tools=True,
            ),
            AIModel(
                id="claude-opus",
                name="Claude 3 Opus",
                provider="anthropic",
                model_type="chat",
                status="available",
                context_size=200000,
                supports_vision=True,
                supports_tools=True,
            ),
        ]
        
        for model in default_models:
            self._models[model.id] = model
    
    def register_model(self, model: AIModel) -> None:
        """Register a new model.
        
        Args:
            model: Model to register.
            
        Raises:
            ModelError: If model ID already exists.
        """
        if model.id in self._models:
            raise ModelError(
                f"Model already registered: {model.id}",
                model_id=model.id,
            )
        
        self._models[model.id] = model
        logger.info(f"Registered model: {model.name} ({model.provider})")
    
    def unregister_model(self, model_id: str) -> None:
        """Unregister a model.
        
        Args:
            model_id: ID of model to unregister.
            
        Raises:
            ModelNotFoundError: If model doesn't exist.
        """
        if model_id not in self._models:
            raise ModelNotFoundError(model_id)
        
        del self._models[model_id]
        logger.info(f"Unregistered model: {model_id}")
    
    def get_model(self, model_id: str) -> AIModel:
        """Get a model by ID.
        
        Args:
            model_id: Model ID.
            
        Returns:
            Model instance.
            
        Raises:
            ModelNotFoundError: If model doesn't exist.
        """
        if model_id not in self._models:
            raise ModelNotFoundError(model_id)
        return self._models[model_id]
    
    def get_all_models(self) -> list[AIModel]:
        """Get all registered models.
        
        Returns:
            List of all models.
        """
        return list(self._models.values())
    
    def get_models_by_provider(self, provider: str) -> list[AIModel]:
        """Get models by provider.
        
        Args:
            provider: Provider name.
            
        Returns:
            List of models from the provider.
        """
        return [m for m in self._models.values() if m.provider == provider]
    
    def get_models_by_status(self, status: str) -> list[AIModel]:
        """Get models by status.
        
        Args:
            status: Status to filter by.
            
        Returns:
            List of models with the status.
        """
        return [m for m in self._models.values() if m.status == status]
    
    def update_model_status(self, model_id: str, status: str) -> None:
        """Update model status.
        
        Args:
            model_id: Model ID.
            status: New status.
            
        Raises:
            ModelNotFoundError: If model doesn't exist.
        """
        model = self.get_model(model_id)
        old_status = model.status
        model.status = status
        logger.info(f"Model {model_id} status: {old_status} -> {status}")
    
    def record_model_usage(self, model_id: str) -> None:
        """Record model usage.
        
        Args:
            model_id: Model ID.
        """
        model = self.get_model(model_id)
        model.update_usage()
    
    def get_model_count(self) -> int:
        """Get total model count.
        
        Returns:
            Number of registered models.
        """
        return len(self._models)
    
    def get_running_model_count(self) -> int:
        """Get count of running models.
        
        Returns:
            Number of running models.
        """
        return len([m for m in self._models.values() if m.status == "running"])
    
    def set_model_endpoint(self, model_id: str, endpoint: str) -> None:
        """Set model endpoint (for local models).
        
        Args:
            model_id: Model ID.
            endpoint: Endpoint URL.
        """
        model = self.get_model(model_id)
        model.endpoint = endpoint
        logger.info(f"Model {model_id} endpoint set: {endpoint}")
    
    def update_model_config(
        self,
        model_id: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> None:
        """Update model configuration.
        
        Args:
            model_id: Model ID.
            temperature: New temperature.
            max_tokens: New max tokens.
        """
        model = self.get_model(model_id)
        if temperature is not None:
            model.temperature = temperature
        if max_tokens is not None:
            model.max_tokens = max_tokens
        logger.info(f"Model {model_id} configuration updated")
