"""Tests for auth helper functions and decorators."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
import jwt

from app import create_app
from app.auth import (
    get_hashed_password,
    check_password,
    create_access_token,
    decode_token,
    token_required,
)


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "test-secret-key"
    RATELIMIT_ENABLED = False


class TestConfigNoSecretKey:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = ""  # Empty secret key
    RATELIMIT_ENABLED = False


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_get_hashed_password_returns_bytes(self):
        """Test that hashed password is returned as bytes."""
        result = get_hashed_password("mypassword")
        assert isinstance(result, bytes)

    def test_hashed_password_is_not_plaintext(self):
        """Test that hashed password differs from plaintext."""
        password = "mypassword"
        hashed = get_hashed_password(password)
        assert hashed != password.encode("utf-8")

    def test_check_password_correct(self):
        """Test that correct password returns True."""
        password = "mypassword"
        hashed = get_hashed_password(password)
        assert check_password(password, hashed) is True

    def test_check_password_incorrect(self):
        """Test that incorrect password returns False."""
        hashed = get_hashed_password("mypassword")
        assert check_password("wrongpassword", hashed) is False


class TestCreateAccessToken:
    """Tests for create_access_token function."""

    def test_creates_valid_token(self):
        """Test that a valid JWT token is created."""
        app = create_app(TestConfig)
        with app.app_context():
            token = create_access_token(123)
            assert isinstance(token, str)
            # Verify we can decode it
            payload = jwt.decode(token, "test-secret-key", algorithms=["HS256"])
            assert payload["sub"] == 123

    def test_raises_error_when_secret_key_not_configured(self):
        """Test that ValueError is raised when SECRET_KEY is empty."""
        app = create_app(TestConfigNoSecretKey)
        with app.app_context():
            with pytest.raises(ValueError) as exc_info:
                create_access_token(123)
            assert "SECRET_KEY not configured" in str(exc_info.value)


class TestDecodeToken:
    """Tests for decode_token function."""

    def test_decodes_valid_token(self):
        """Test that a valid token is decoded correctly."""
        app = create_app(TestConfig)
        with app.app_context():
            token = create_access_token(456)
            payload = decode_token(token)
            assert payload["sub"] == 456

    def test_raises_error_when_secret_key_not_configured(self):
        """Test that ValueError is raised when SECRET_KEY is empty."""
        app = create_app(TestConfigNoSecretKey)
        with app.app_context():
            with pytest.raises(ValueError) as exc_info:
                decode_token("some-token")
            assert "SECRET_KEY not configured" in str(exc_info.value)

    def test_raises_error_for_expired_token(self):
        """Test that ValueError is raised for expired token."""
        app = create_app(TestConfig)
        with app.app_context():
            # Create an already-expired token
            payload = {
                "exp": datetime.now(timezone.utc) - timedelta(hours=1),
                "iat": datetime.now(timezone.utc) - timedelta(hours=2),
                "sub": 123,
            }
            expired_token = jwt.encode(payload, "test-secret-key", algorithm="HS256")

            with pytest.raises(ValueError) as exc_info:
                decode_token(expired_token)
            assert "Token has expired" in str(exc_info.value)

    def test_raises_error_for_invalid_token(self):
        """Test that ValueError is raised for invalid token."""
        app = create_app(TestConfig)
        with app.app_context():
            with pytest.raises(ValueError) as exc_info:
                decode_token("not-a-valid-jwt-token")
            assert "Invalid token" in str(exc_info.value)

    def test_raises_error_for_wrong_secret_key(self):
        """Test that ValueError is raised when token signed with different key."""
        app = create_app(TestConfig)
        with app.app_context():
            # Create token with different secret
            payload = {
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
                "iat": datetime.now(timezone.utc),
                "sub": 123,
            }
            wrong_key_token = jwt.encode(payload, "wrong-secret", algorithm="HS256")

            with pytest.raises(ValueError) as exc_info:
                decode_token(wrong_key_token)
            assert "Invalid token" in str(exc_info.value)


class TestTokenRequiredDecorator:
    """Tests for token_required decorator."""

    @pytest.fixture
    def app(self):
        """Create app with test config."""
        app = create_app(TestConfig)
        from app.models import db
        with app.app_context():
            db.create_all()
        yield app
        with app.app_context():
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    def test_returns_401_for_malformed_authorization_header(self, client):
        """Test that 401 is returned for malformed Authorization header."""
        # "Bearer" without the actual token
        response = client.get(
            "/api/habits",
            headers={"Authorization": "Bearer"}
        )
        assert response.status_code == 401
        data = response.get_json()
        assert "Invalid token format" in data.get("error", "")

    def test_returns_401_for_expired_token(self, app, client):
        """Test that 401 is returned for expired token."""
        with app.app_context():
            # Create an expired token
            payload = {
                "exp": datetime.now(timezone.utc) - timedelta(hours=1),
                "iat": datetime.now(timezone.utc) - timedelta(hours=2),
                "sub": 123,
            }
            expired_token = jwt.encode(payload, "test-secret-key", algorithm="HS256")

        response = client.get(
            "/api/habits",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401
        data = response.get_json()
        assert "expired" in data.get("error", "").lower()

    def test_returns_401_for_invalid_token(self, client):
        """Test that 401 is returned for invalid token."""
        response = client.get(
            "/api/habits",
            headers={"Authorization": "Bearer invalid-token-here"}
        )
        assert response.status_code == 401
        data = response.get_json()
        assert "Invalid token" in data.get("error", "")

    def test_returns_401_for_missing_token(self, client):
        """Test that 401 is returned when no token is provided."""
        response = client.get("/api/habits")
        assert response.status_code == 401
        data = response.get_json()
        assert "missing" in data.get("error", "").lower()
