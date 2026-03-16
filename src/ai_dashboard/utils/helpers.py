"""Helper utilities."""

from __future__ import annotations

import secrets
import uuid
from datetime import datetime
from typing import Any


def generate_id(prefix: str = "") -> str:
    """Generate a unique identifier.

    Args:
        prefix: Optional prefix for the ID.

    Returns:
        Unique identifier string.
    """
    unique_id = uuid.uuid4().hex[:8]
    if prefix:
        return f"{prefix}-{unique_id}"
    return unique_id


def generate_task_id() -> str:
    """Generate a unique task ID.

    Returns:
        Task ID string.
    """
    return f"task-{uuid.uuid4().hex[:8]}"


def generate_session_id() -> str:
    """Generate a secure session ID.

    Returns:
        Session ID string.
    """
    return secrets.token_urlsafe(32)


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate a string to a maximum length.

    Args:
        text: String to truncate.
        max_length: Maximum length.
        suffix: Suffix to add when truncated.

    Returns:
        Truncated string.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def safe_get(d: dict, *keys: str, default: Any = None) -> Any:
    """Safely get nested dictionary value.

    Args:
        d: Dictionary to get value from.
        *keys: Keys to traverse.
        default: Default value if key not found.

    Returns:
        Value if found, default otherwise.
    """
    current = d
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def merge_dicts(base: dict, override: dict) -> dict:
    """Merge two dictionaries recursively.

    Args:
        base: Base dictionary.
        override: Dictionary to merge into base.

    Returns:
        Merged dictionary.
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def get_timestamp() -> str:
    """Get current timestamp as ISO string.

    Returns:
        ISO formatted timestamp.
    """
    return datetime.now().isoformat()


def parse_bool(value: str) -> bool:
    """Parse a string to boolean.

    Args:
        value: String to parse.

    Returns:
        Boolean value.
    """
    return value.lower() in ("true", "1", "yes", "on", "enabled")


def ensure_list(value: Any) -> list:
    """Ensure value is a list.

    Args:
        value: Value to ensure is a list.

    Returns:
        List value.
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]
