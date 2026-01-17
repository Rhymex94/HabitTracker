"""Tests for security event logging."""

import json
import pytest
from unittest.mock import patch
from app import create_app
from app.security_logger import (
    log_login_success,
    log_login_failure,
    log_signup_success,
    log_signup_failure,
    log_token_validation_failure,
    log_unauthorized_access,
    _get_client_ip,
)


@pytest.fixture
def app_context():
    """Create an app context for testing."""
    app = create_app()
    with app.test_request_context():
        yield app


class TestGetClientIp:
    """Tests for client IP extraction."""

    def test_uses_x_forwarded_for_header(self, app_context):
        """Test that X-Forwarded-For header is used when present."""
        with patch("app.security_logger.request") as mock_request:
            mock_request.headers = {"X-Forwarded-For": "203.0.113.1, 10.0.0.1"}
            mock_request.remote_addr = "10.0.0.1"

            ip = _get_client_ip()
            assert ip == "203.0.113.1"

    def test_uses_x_real_ip_header(self, app_context):
        """Test that X-Real-IP header is used when X-Forwarded-For is absent."""
        with patch("app.security_logger.request") as mock_request:
            mock_request.headers = {"X-Real-IP": "203.0.113.2"}
            mock_request.remote_addr = "10.0.0.1"

            ip = _get_client_ip()
            assert ip == "203.0.113.2"

    def test_falls_back_to_remote_addr(self, app_context):
        """Test fallback to remote_addr when no proxy headers."""
        with patch("app.security_logger.request") as mock_request:
            mock_request.headers = {}
            mock_request.remote_addr = "192.168.1.100"

            ip = _get_client_ip()
            assert ip == "192.168.1.100"


class TestSecurityEventLogging:
    """Tests for security event log output."""

    def test_log_login_success_format(self, app_context, capsys):
        """Test that login success is logged with correct format."""
        with patch("app.security_logger.request") as mock_request:
            mock_request.headers = {}
            mock_request.remote_addr = "192.168.1.1"

            log_login_success("testuser", 123)

            captured = capsys.readouterr()
            log_entry = json.loads(captured.err.strip())

            assert log_entry["event"] == "login_success"
            assert log_entry["username"] == "testuser"
            assert log_entry["user_id"] == 123
            assert log_entry["ip"] == "192.168.1.1"
            assert "timestamp" in log_entry

    def test_log_login_failure_format(self, app_context, capsys):
        """Test that login failure is logged with correct format."""
        with patch("app.security_logger.request") as mock_request:
            mock_request.headers = {}
            mock_request.remote_addr = "192.168.1.1"

            log_login_failure("baduser", "invalid_credentials")

            captured = capsys.readouterr()
            log_entry = json.loads(captured.err.strip())

            assert log_entry["event"] == "login_failure"
            assert log_entry["username"] == "baduser"
            assert log_entry["reason"] == "invalid_credentials"
            assert log_entry["ip"] == "192.168.1.1"

    def test_log_signup_success_format(self, app_context, capsys):
        """Test that signup success is logged with correct format."""
        with patch("app.security_logger.request") as mock_request:
            mock_request.headers = {}
            mock_request.remote_addr = "10.0.0.1"

            log_signup_success("newuser", 456)

            captured = capsys.readouterr()
            log_entry = json.loads(captured.err.strip())

            assert log_entry["event"] == "signup_success"
            assert log_entry["username"] == "newuser"
            assert log_entry["user_id"] == 456

    def test_log_signup_failure_format(self, app_context, capsys):
        """Test that signup failure is logged with correct format."""
        with patch("app.security_logger.request") as mock_request:
            mock_request.headers = {}
            mock_request.remote_addr = "10.0.0.1"

            log_signup_failure("existinguser", "username_exists")

            captured = capsys.readouterr()
            log_entry = json.loads(captured.err.strip())

            assert log_entry["event"] == "signup_failure"
            assert log_entry["username"] == "existinguser"
            assert log_entry["reason"] == "username_exists"

    def test_log_token_validation_failure_format(self, app_context, capsys):
        """Test that token validation failure is logged with correct format."""
        with patch("app.security_logger.request") as mock_request:
            mock_request.headers = {}
            mock_request.remote_addr = "172.16.0.1"
            mock_request.path = "/api/habits"
            mock_request.method = "GET"

            log_token_validation_failure("Token has expired")

            captured = capsys.readouterr()
            log_entry = json.loads(captured.err.strip())

            assert log_entry["event"] == "token_validation_failure"
            assert log_entry["reason"] == "Token has expired"
            assert log_entry["path"] == "/api/habits"
            assert log_entry["method"] == "GET"

    def test_log_unauthorized_access_format(self, app_context, capsys):
        """Test that unauthorized access is logged with correct format."""
        with patch("app.security_logger.request") as mock_request:
            mock_request.headers = {}
            mock_request.remote_addr = "172.16.0.1"

            log_unauthorized_access("/api/stats", "GET", "missing_token")

            captured = capsys.readouterr()
            log_entry = json.loads(captured.err.strip())

            assert log_entry["event"] == "unauthorized_access"
            assert log_entry["path"] == "/api/stats"
            assert log_entry["method"] == "GET"
            assert log_entry["reason"] == "missing_token"


class TestSecurityLoggingIntegration:
    """Integration tests for security logging in auth endpoints."""

    def test_login_failure_logs_event(self, client, capsys):
        """Test that failed login attempts are logged."""
        response = client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": "wrongpass"},
        )

        assert response.status_code == 401

        captured = capsys.readouterr()
        # Find the login_failure log line
        log_lines = [l for l in captured.err.strip().split("\n") if l]
        login_failure_logs = [
            json.loads(l) for l in log_lines
            if "login_failure" in l
        ]

        assert len(login_failure_logs) >= 1
        assert login_failure_logs[-1]["username"] == "nonexistent"

    def test_login_success_logs_event(self, app, client, capsys):
        """Test that successful logins are logged."""
        from app.auth import get_hashed_password
        from app.models import db, User

        # Create a user with bcrypt hashing (matching what the app uses)
        with app.app_context():
            user = User(
                username="securitytestuser",
                password=get_hashed_password("TestPass123"),
            )
            db.session.add(user)
            db.session.commit()

        response = client.post(
            "/api/auth/login",
            json={"username": "securitytestuser", "password": "TestPass123"},
        )

        assert response.status_code == 200

        captured = capsys.readouterr()
        log_lines = [l for l in captured.err.strip().split("\n") if l]
        login_success_logs = [
            json.loads(l) for l in log_lines
            if "login_success" in l
        ]

        assert len(login_success_logs) >= 1
        assert login_success_logs[-1]["username"] == "securitytestuser"

    def test_unauthorized_access_logs_event(self, client, capsys):
        """Test that unauthorized access attempts are logged."""
        response = client.get("/api/habits")

        assert response.status_code == 401

        captured = capsys.readouterr()
        log_lines = [l for l in captured.err.strip().split("\n") if l]
        unauthorized_logs = [
            json.loads(l) for l in log_lines
            if "unauthorized_access" in l or "token" in l.lower()
        ]

        assert len(unauthorized_logs) >= 1
