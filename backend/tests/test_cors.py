import pytest
from app import validate_cors_origin, get_cors_origins


class TestValidateCorsOrigin:
    """Tests for the validate_cors_origin function."""

    @pytest.mark.parametrize(
        "origin",
        [
            "http://localhost:3000",
            "https://example.com",
            "https://app.example.com",
            "http://192.168.1.1:8080",
            "https://example.com/",
            "http://localhost",
            "https://sub.domain.example.com",
        ],
        ids=[
            "localhost_with_port",
            "https_domain",
            "https_subdomain",
            "ip_with_port",
            "trailing_slash",
            "localhost_no_port",
            "nested_subdomain",
        ],
    )
    def test_valid_origins(self, origin):
        """Test that valid CORS origins are accepted."""
        assert validate_cors_origin(origin) is True

    @pytest.mark.parametrize(
        "origin",
        [
            "localhost:3000",
            "example.com",
            "htps://example.com",
            "ftp://example.com",
            "",
            "https://example.com/path",
            "https://example.com/api/v1",
            "   ",
            None,
        ],
        ids=[
            "missing_protocol",
            "no_protocol",
            "typo_in_protocol",
            "wrong_protocol_ftp",
            "empty_string",
            "has_path",
            "has_deep_path",
            "whitespace_only",
            "none_value",
        ],
    )
    def test_invalid_origins(self, origin):
        """Test that invalid CORS origins are rejected."""
        assert validate_cors_origin(origin) is False


class TestGetCorsOrigins:
    """Tests for the get_cors_origins function."""

    def test_single_valid_origin(self, monkeypatch):
        """Test with a single valid origin."""
        monkeypatch.setenv("FRONTEND_ORIGIN", "https://example.com")
        origins = get_cors_origins()
        assert origins == ["https://example.com"]

    def test_multiple_valid_origins(self, monkeypatch):
        """Test with multiple comma-separated valid origins."""
        monkeypatch.setenv(
            "FRONTEND_ORIGIN",
            "https://app.example.com,https://staging.example.com"
        )
        origins = get_cors_origins()
        assert origins == ["https://app.example.com", "https://staging.example.com"]

    def test_multiple_origins_with_whitespace(self, monkeypatch):
        """Test that whitespace around origins is trimmed."""
        monkeypatch.setenv(
            "FRONTEND_ORIGIN",
            "  https://app.example.com  ,  https://staging.example.com  "
        )
        origins = get_cors_origins()
        assert origins == ["https://app.example.com", "https://staging.example.com"]

    def test_default_origin_when_not_set(self, monkeypatch):
        """Test that default origin is used when env var is not set."""
        monkeypatch.delenv("FRONTEND_ORIGIN", raising=False)
        origins = get_cors_origins()
        assert origins == ["http://localhost:3000"]

    def test_invalid_origin_exits(self, monkeypatch):
        """Test that invalid origin causes system exit."""
        monkeypatch.setenv("FRONTEND_ORIGIN", "invalid-url")
        with pytest.raises(SystemExit) as exc_info:
            get_cors_origins()
        assert exc_info.value.code == 1

    def test_empty_origin_exits(self, monkeypatch):
        """Test that empty origin causes system exit."""
        monkeypatch.setenv("FRONTEND_ORIGIN", "")
        with pytest.raises(SystemExit) as exc_info:
            get_cors_origins()
        assert exc_info.value.code == 1

    def test_mixed_valid_invalid_origins_exits(self, monkeypatch):
        """Test that mix of valid and invalid origins causes system exit."""
        monkeypatch.setenv(
            "FRONTEND_ORIGIN",
            "https://valid.example.com,invalid-url"
        )
        with pytest.raises(SystemExit) as exc_info:
            get_cors_origins()
        assert exc_info.value.code == 1
