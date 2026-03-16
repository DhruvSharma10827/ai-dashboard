"""Configuration management for AI Dashboard.

This module provides centralized configuration management with:
- JSON-based configuration storage
- Environment variable support
- Type-safe configuration access
- Configuration validation

Example:
    >>> config = get_config()
    >>> config.ssh_port
    2222
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from ai_dashboard.core.exceptions import ConfigurationError

# Configuration paths
CONFIG_DIR = Path.home() / ".ai-dashboard"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class SecurityConfig:
    """Security-related configuration settings.

    Attributes:
        session_timeout: Session timeout in minutes.
        max_login_attempts: Maximum failed login attempts before lockout.
        password_min_length: Minimum password length requirement.
        two_factor_enabled: Whether two-factor authentication is enabled.
    """

    session_timeout: int = 30
    max_login_attempts: int = 5
    password_min_length: int = 8
    two_factor_enabled: bool = False


@dataclass
class SSHConfig:
    """SSH server configuration settings.

    Attributes:
        enabled: Whether SSH server is enabled.
        port: SSH server port.
        password_auth: Whether password authentication is enabled.
        key_auth: Whether key-based authentication is enabled.
    """

    enabled: bool = True
    port: int = 2222
    password_auth: bool = True
    key_auth: bool = True


@dataclass
class AIProviderConfig:
    """AI provider configuration settings.

    Attributes:
        default_provider: Default AI provider to use.
        default_model: Default model to use.
        request_timeout: Request timeout in seconds.
        max_retries: Maximum retry attempts for API calls.
    """

    default_provider: str = "ollama"
    default_model: str = "llama3.2"
    request_timeout: int = 60
    max_retries: int = 3


@dataclass
class UIConfig:
    """User interface configuration settings.

    Attributes:
        theme: UI theme name.
        animations_enabled: Whether animations are enabled.
        mouse_support: Whether mouse support is enabled.
    """

    theme: str = "default"
    animations_enabled: bool = True
    mouse_support: bool = True


@dataclass
class Config:
    """Main application configuration.

    This class manages all configuration settings for the AI Dashboard
    application, including security, SSH, AI providers, and UI settings.

    Attributes:
        admin_password_hash: Hashed admin password.
        encryption_key: Key for encrypting sensitive data.
        api_keys: Dictionary of API keys for various providers.
        security: Security configuration settings.
        ssh: SSH server configuration settings.
        ai: AI provider configuration settings.
        ui: User interface configuration settings.

    Example:
        >>> config = Config()
        >>> config.ssh.port = 2222
        >>> config.save()
    """

    admin_password_hash: str = ""
    encryption_key: str = ""
    api_keys: dict[str, str] = field(default_factory=dict)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    ssh: SSHConfig = field(default_factory=SSHConfig)
    ai: AIProviderConfig = field(default_factory=AIProviderConfig)
    ui: UIConfig = field(default_factory=UIConfig)

    def save(self) -> None:
        """Save configuration to disk.

        Raises:
            ConfigurationError: If configuration cannot be saved.
        """
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            # Convert to dict with nested dataclasses
            data = {
                "admin_password_hash": self.admin_password_hash,
                "encryption_key": self.encryption_key,
                "api_keys": self.api_keys,
                "security": asdict(self.security),
                "ssh": asdict(self.ssh),
                "ai": asdict(self.ai),
                "ui": asdict(self.ui),
            }

            # Write atomically
            temp_file = CONFIG_FILE.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            temp_file.replace(CONFIG_FILE)

        except OSError as e:
            raise ConfigurationError(f"Failed to save configuration: {e}") from e

    @classmethod
    def load(cls) -> Config:
        """Load configuration from disk.

        Returns:
            Config: Loaded configuration instance.

        Raises:
            ConfigurationError: If configuration is invalid.
        """
        if not CONFIG_FILE.exists():
            return cls()

        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                data = json.load(f)

            # Handle nested dataclasses
            security_data = data.pop("security", {})
            ssh_data = data.pop("ssh", {})
            ai_data = data.pop("ai", {})
            ui_data = data.pop("ui", {})

            config = cls(**data)
            config.security = SecurityConfig(**security_data)
            config.ssh = SSHConfig(**ssh_data)
            config.ai = AIProviderConfig(**ai_data)
            config.ui = UIConfig(**ui_data)

            return config

        except (json.JSONDecodeError, TypeError) as e:
            raise ConfigurationError(f"Invalid configuration file: {e}") from e

    def validate(self) -> list[str]:
        """Validate configuration settings.

        Returns:
            List of validation error messages. Empty if valid.
        """
        errors = []

        if self.security.session_timeout < 1:
            errors.append("session_timeout must be at least 1 minute")

        if self.security.password_min_length < 6:
            errors.append("password_min_length must be at least 6 characters")

        if self.ssh.port < 1 or self.ssh.port > 65535:
            errors.append(f"Invalid SSH port: {self.ssh.port}")

        if self.ai.request_timeout < 1:
            errors.append("request_timeout must be at least 1 second")

        return errors

    def get_api_key(self, provider: str) -> str | None:
        """Get API key for a provider.

        Args:
            provider: Provider name (e.g., 'openai', 'anthropic').

        Returns:
            API key if set, None otherwise.
        """
        return self.api_keys.get(provider) or os.getenv(f"{provider.upper()}_API_KEY")

    def set_api_key(self, provider: str, api_key: str) -> None:
        """Set API key for a provider.

        Args:
            provider: Provider name.
            api_key: API key value.
        """
        self.api_keys[provider] = api_key


# Global configuration instance
_config: Config | None = None


def get_config() -> Config:
    """Get the global configuration instance.

    Returns:
        Config: Global configuration instance.
    """
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def save_config(config: Config | None = None) -> None:
    """Save configuration to disk.

    Args:
        config: Configuration to save. Uses global config if None.
    """
    if config is None:
        config = get_config()
    config.save()


def reset_config() -> Config:
    """Reset configuration to defaults.

    Returns:
        Config: New default configuration instance.
    """
    global _config
    _config = Config()
    return _config
