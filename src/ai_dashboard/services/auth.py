"""Authentication service for AI Dashboard.

This module provides authentication and authorization functionality,
including password hashing, verification, and session management.

Example:
    >>> auth = AuthService()
    >>> auth.setup_admin("secure_password")
    >>> auth.authenticate("secure_password")
    True
"""

from __future__ import annotations

import secrets
from datetime import datetime
from datetime import timedelta

import argon2

from ai_dashboard.core.config import Config
from ai_dashboard.core.config import get_config
from ai_dashboard.core.config import save_config
from ai_dashboard.core.exceptions import AuthenticationError
from ai_dashboard.core.exceptions import SecurityError
from ai_dashboard.core.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    """Authentication service for user management.

    This service handles:
    - Password hashing and verification
    - Admin authentication
    - Session management
    - Account lockout

    Attributes:
        config: Application configuration.
        hasher: Argon2 password hasher.
        max_attempts: Maximum failed login attempts before lockout.
        lockout_minutes: Account lockout duration in minutes.

    Example:
        >>> auth = AuthService()
        >>> if auth.is_first_run():
        ...     auth.setup_admin("new_password")
    """

    def __init__(
        self,
        config: Config | None = None,
        max_attempts: int = 5,
        lockout_minutes: int = 30,
    ) -> None:
        """Initialize authentication service.

        Args:
            config: Application configuration.
            max_attempts: Maximum failed login attempts.
            lockout_minutes: Lockout duration in minutes.
        """
        self.config = config or get_config()
        self.hasher = argon2.PasswordHasher(
            time_cost=3,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            salt_len=16,
        )
        self.max_attempts = max_attempts
        self.lockout_minutes = lockout_minutes
        self._failed_attempts: dict[str, int] = {}
        self._lockouts: dict[str, datetime] = {}

    def is_first_run(self) -> bool:
        """Check if this is the first run (no admin password set).

        Returns:
            True if no admin password has been set.
        """
        return not bool(self.config.admin_password_hash)

    def setup_admin(self, password: str, confirm: str | None = None) -> None:
        """Set up the admin password for the first time.

        Args:
            password: Admin password to set.
            confirm: Password confirmation.

        Raises:
            AuthenticationError: If passwords don't match or are invalid.
        """
        # Validate password
        if not password:
            raise AuthenticationError("Password cannot be empty")

        if len(password) < self.config.security.password_min_length:
            raise AuthenticationError(
                f"Password must be at least {self.config.security.password_min_length} characters"
            )

        if confirm is not None and password != confirm:
            raise AuthenticationError("Passwords do not match")

        # Check if already set up
        if self.config.admin_password_hash:
            raise AuthenticationError("Admin password already set")

        # Hash and store password
        self.config.admin_password_hash = self.hasher.hash(password)
        self.config.encryption_key = secrets.token_hex(32)
        save_config(self.config)

        logger.info("Admin account set up successfully")

    def change_password(
        self,
        current_password: str,
        new_password: str,
        confirm: str | None = None,
    ) -> None:
        """Change the admin password.

        Args:
            current_password: Current password for verification.
            new_password: New password to set.
            confirm: New password confirmation.

        Raises:
            AuthenticationError: If verification fails or new password is invalid.
        """
        # Verify current password
        if not self.authenticate(current_password, check_lockout=False):
            raise AuthenticationError("Current password is incorrect")

        # Validate new password
        if not new_password:
            raise AuthenticationError("New password cannot be empty")

        if len(new_password) < self.config.security.password_min_length:
            raise AuthenticationError(
                f"Password must be at least {self.config.security.password_min_length} characters"
            )

        if confirm is not None and new_password != confirm:
            raise AuthenticationError("Passwords do not match")

        # Update password
        self.config.admin_password_hash = self.hasher.hash(new_password)
        save_config(self.config)

        logger.info("Admin password changed successfully")

    def authenticate(
        self,
        password: str,
        check_lockout: bool = True,
    ) -> bool:
        """Authenticate with the admin password.

        Args:
            password: Password to verify.
            check_lockout: Whether to check for account lockout.

        Returns:
            True if authentication successful.

        Raises:
            AuthenticationError: If authentication fails.
            SecurityError: If account is locked.
        """
        admin_key = "admin"

        # Check lockout
        if check_lockout and self._is_locked(admin_key):
            raise SecurityError(
                "Account is locked due to too many failed attempts. Please try again later."
            )

        # Check if password is set
        if not self.config.admin_password_hash:
            raise AuthenticationError("Admin password not set")

        # Verify password
        try:
            self.hasher.verify(self.config.admin_password_hash, password)
            self._clear_failed_attempts(admin_key)
            logger.info("Admin authenticated successfully")
            return True
        except argon2.exceptions.VerifyMismatchError:
            self._record_failed_attempt(admin_key)
            raise AuthenticationError("Invalid password")
        except argon2.exceptions.VerificationError as e:
            logger.error(f"Password verification error: {e}")
            raise AuthenticationError("Authentication failed")

    def _record_failed_attempt(self, key: str) -> None:
        """Record a failed authentication attempt.

        Args:
            key: Key to track attempts for.
        """
        self._failed_attempts[key] = self._failed_attempts.get(key, 0) + 1

        if self._failed_attempts[key] >= self.max_attempts:
            self._lock_account(key)
            logger.warning(f"Account locked due to {self.max_attempts} failed attempts")

    def _clear_failed_attempts(self, key: str) -> None:
        """Clear failed attempts for a key.

        Args:
            key: Key to clear attempts for.
        """
        self._failed_attempts.pop(key, None)
        self._lockouts.pop(key, None)

    def _lock_account(self, key: str) -> None:
        """Lock an account.

        Args:
            key: Key to lock.
        """
        self._lockouts[key] = datetime.now() + timedelta(minutes=self.lockout_minutes)

    def _is_locked(self, key: str) -> bool:
        """Check if an account is locked.

        Args:
            key: Key to check.

        Returns:
            True if account is locked.
        """
        if key not in self._lockouts:
            return False

        if datetime.now() > self._lockouts[key]:
            self._lockouts.pop(key)
            self._failed_attempts.pop(key, None)
            return False

        return True

    def get_lockout_remaining(self, key: str = "admin") -> int | None:
        """Get remaining lockout time in minutes.

        Args:
            key: Key to check.

        Returns:
            Remaining minutes, or None if not locked.
        """
        if key not in self._lockouts:
            return None

        remaining = self._lockouts[key] - datetime.now()
        if remaining.total_seconds() <= 0:
            return None

        return int(remaining.total_seconds() / 60)

    def generate_session_token(self) -> str:
        """Generate a secure session token.

        Returns:
            Secure random token.
        """
        return secrets.token_urlsafe(32)

    def validate_session_token(self, token: str) -> bool:
        """Validate a session token.

        Args:
            token: Token to validate.

        Returns:
            True if token is valid format.
        """
        if not token or len(token) < 32:
            return False
        try:
            # Just check if it's valid base64
            import base64

            base64.urlsafe_b64decode(token + "==")
            return True
        except Exception:
            return False
