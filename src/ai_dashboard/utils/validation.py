"""Validation utilities."""

from __future__ import annotations

import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email address format.

    Args:
        email: Email address to validate.

    Returns:
        True if email is valid.
    """
    if not email:
        return False

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password(password: str, min_length: int = 8) -> tuple[bool, list[str]]:
    """Validate password strength.

    Args:
        password: Password to validate.
        min_length: Minimum password length.

    Returns:
        Tuple of (is_valid, list of error messages).
    """
    errors = []

    if not password:
        errors.append("Password is required")
        return False, errors

    if len(password) < min_length:
        errors.append(f"Password must be at least {min_length} characters")

    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")

    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")

    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")

    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character")

    return len(errors) == 0, errors


def validate_url(url: str, require_https: bool = False) -> bool:
    """Validate URL format.

    Args:
        url: URL to validate.
        require_https: Whether to require HTTPS scheme.

    Returns:
        True if URL is valid.
    """
    if not url:
        return False

    pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    if not re.match(pattern, url, re.IGNORECASE):
        return False

    if require_https and not url.lower().startswith("https://"):
        return False

    return True


def validate_model_id(model_id: str) -> bool:
    """Validate model ID format.

    Args:
        model_id: Model ID to validate.

    Returns:
        True if model ID is valid.
    """
    if not model_id:
        return False

    # Model IDs should be lowercase alphanumeric with hyphens
    pattern = r"^[a-z0-9][a-z0-9\-]*[a-z0-9]$|^[a-z0-9]$"
    return bool(re.match(pattern, model_id))


def validate_agent_id(agent_id: str) -> bool:
    """Validate agent ID format.

    Args:
        agent_id: Agent ID to validate.

    Returns:
        True if agent ID is valid.
    """
    if not agent_id:
        return False

    # Agent IDs should start with "agent-" followed by alphanumeric
    pattern = r"^agent-[a-z0-9\-]+$"
    return bool(re.match(pattern, agent_id))
