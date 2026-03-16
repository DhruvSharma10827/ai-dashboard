"""User data model.

This module defines the User dataclass for representing
application users and their authentication information.

Example:
    >>> user = User(
    ...     id=1,
    ...     username="admin",
    ...     role="admin",
    ... )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class UserRole(Enum):
    """Enumeration of user roles.
    
    Attributes:
        ADMIN: Administrator with full access.
        USER: Regular user with limited access.
        VIEWER: Read-only access.
    """
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def permissions(self) -> list[str]:
        """Get permissions for this role."""
        permissions_map = {
            UserRole.ADMIN: [
                "read", "write", "delete", "manage_users",
                "manage_models", "manage_agents", "manage_settings",
            ],
            UserRole.USER: [
                "read", "write", "manage_models", "manage_agents",
            ],
            UserRole.VIEWER: ["read"],
        }
        return permissions_map.get(self, [])


@dataclass
class User:
    """User account representation.
    
    This class represents a user account with authentication
    and authorization information.
    
    Attributes:
        id: Unique user identifier.
        username: User's login name.
        password_hash: Hashed password.
        salt: Password salt.
        role: User's role.
        email: User's email address.
        created_at: When the account was created.
        last_login: When the user last logged in.
        login_count: Number of successful logins.
        failed_login_attempts: Number of failed login attempts.
        locked_until: Account lockout expiration time.
        preferences: User preferences.
        metadata: Additional metadata.
    
    Example:
        >>> user = User(
        ...     id=1,
        ...     username="admin",
        ...     role="admin",
        ... )
    """
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    salt: str = ""
    role: str = "user"
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    login_count: int = 0
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    preferences: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Initialize default values after creation."""
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == "admin"
    
    @property
    def is_locked(self) -> bool:
        """Check if account is locked."""
        if self.locked_until is None:
            return False
        return datetime.now() < self.locked_until
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission.
        
        Args:
            permission: Permission to check.
            
        Returns:
            True if user has the permission.
        """
        try:
            role = UserRole(self.role)
            return permission in role.permissions
        except ValueError:
            return False
    
    def record_login(self, success: bool) -> None:
        """Record a login attempt.
        
        Args:
            success: Whether the login was successful.
        """
        if success:
            self.last_login = datetime.now()
            self.login_count += 1
            self.failed_login_attempts = 0
        else:
            self.failed_login_attempts += 1
    
    def lock_account(self, minutes: int = 30) -> None:
        """Lock the account for a specified duration.
        
        Args:
            minutes: Lockout duration in minutes.
        """
        from datetime import timedelta
        self.locked_until = datetime.now() + timedelta(minutes=minutes)
    
    def unlock_account(self) -> None:
        """Unlock the account."""
        self.locked_until = None
        self.failed_login_attempts = 0
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (excluding sensitive data)."""
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "login_count": self.login_count,
            "preferences": self.preferences,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> User:
        """Create user from dictionary."""
        for field_name in ["created_at", "last_login", "locked_until"]:
            if data.get(field_name):
                data[field_name] = datetime.fromisoformat(data[field_name])
        return cls(**data)
