"""Tests for configuration module."""

import pytest
import sys
from unittest.mock import patch


class TestGetSecretKey:
    """Tests for get_secret_key function."""

    def test_returns_secret_key_when_set(self, monkeypatch):
        """Test that SECRET_KEY from env var is returned directly."""
        monkeypatch.setenv("SECRET_KEY", "my-production-secret")

        # Import fresh to get the function
        from app.config import get_secret_key

        # Clear any cached module state and test
        with patch.dict("os.environ", {"SECRET_KEY": "my-production-secret"}, clear=False):
            result = get_secret_key()
            assert result == "my-production-secret"

    def test_returns_default_in_flask_development_mode(self, monkeypatch, capsys):
        """Test that default key is used when FLASK_ENV=development."""
        monkeypatch.delenv("SECRET_KEY", raising=False)
        monkeypatch.setenv("FLASK_ENV", "development")
        monkeypatch.delenv("ENVIRONMENT", raising=False)

        from app.config import get_secret_key

        result = get_secret_key()

        assert result == "dev-secret-key-123"
        captured = capsys.readouterr()
        assert "WARNING" in captured.err
        assert "default SECRET_KEY" in captured.err

    def test_returns_default_in_environment_development_mode(self, monkeypatch, capsys):
        """Test that default key is used when ENVIRONMENT=development."""
        monkeypatch.delenv("SECRET_KEY", raising=False)
        monkeypatch.delenv("FLASK_ENV", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "development")

        from app.config import get_secret_key

        result = get_secret_key()

        assert result == "dev-secret-key-123"
        captured = capsys.readouterr()
        assert "WARNING" in captured.err

    def test_exits_in_production_mode_without_secret_key(self, monkeypatch, capsys):
        """Test that sys.exit(1) is called when no SECRET_KEY in production mode."""
        monkeypatch.delenv("SECRET_KEY", raising=False)
        monkeypatch.delenv("FLASK_ENV", raising=False)
        monkeypatch.delenv("ENVIRONMENT", raising=False)

        from app.config import get_secret_key

        with pytest.raises(SystemExit) as exc_info:
            get_secret_key()

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "ERROR: SECRET_KEY environment variable is required" in captured.err
        assert "FLASK_ENV=development" in captured.err
        assert "token_hex" in captured.err

    def test_exits_when_environment_is_production(self, monkeypatch, capsys):
        """Test that sys.exit(1) is called when ENVIRONMENT=production without SECRET_KEY."""
        monkeypatch.delenv("SECRET_KEY", raising=False)
        monkeypatch.delenv("FLASK_ENV", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "production")

        from app.config import get_secret_key

        with pytest.raises(SystemExit) as exc_info:
            get_secret_key()

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "ERROR" in captured.err

