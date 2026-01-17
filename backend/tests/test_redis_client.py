"""Tests for Redis client caching functionality."""

import pytest
from unittest.mock import patch, MagicMock
import redis

from app import redis_client
from app.redis_client import (
    get_redis_client,
    get_cached_streak,
    set_cached_streak,
    invalidate_streak_cache,
    STREAK_CACHE_TTL,
)


@pytest.fixture(autouse=True)
def reset_redis_client():
    """Reset the global Redis client before each test."""
    redis_client._redis_client = None
    yield
    redis_client._redis_client = None


class TestGetRedisClient:
    """Tests for get_redis_client function."""

    def test_returns_none_when_redis_url_not_set(self, monkeypatch):
        """Test that None is returned when REDIS_URL env var is not set."""
        monkeypatch.delenv("REDIS_URL", raising=False)

        result = get_redis_client()

        assert result is None

    def test_returns_none_when_redis_connection_fails(self, monkeypatch):
        """Test graceful handling when Redis connection fails."""
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

        with patch("app.redis_client.redis.from_url") as mock_from_url:
            mock_client = MagicMock()
            mock_client.ping.side_effect = redis.RedisError("Connection refused")
            mock_from_url.return_value = mock_client

            result = get_redis_client()

            assert result is None
            # Verify the global client was reset to None
            assert redis_client._redis_client is None

    def test_returns_client_when_connection_succeeds(self, monkeypatch):
        """Test that client is returned when connection succeeds."""
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

        with patch("app.redis_client.redis.from_url") as mock_from_url:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_from_url.return_value = mock_client

            result = get_redis_client()

            assert result is mock_client
            mock_from_url.assert_called_once_with(
                "redis://localhost:6379/0", decode_responses=True
            )

    def test_reuses_existing_client(self, monkeypatch):
        """Test that existing client is reused on subsequent calls."""
        existing_client = MagicMock()
        redis_client._redis_client = existing_client

        result = get_redis_client()

        assert result is existing_client


class TestGetCachedStreak:
    """Tests for get_cached_streak function."""

    def test_returns_none_when_client_unavailable(self, monkeypatch):
        """Test that None is returned when Redis client is unavailable."""
        monkeypatch.delenv("REDIS_URL", raising=False)

        result = get_cached_streak(123)

        assert result is None

    def test_returns_none_when_key_not_found(self, monkeypatch):
        """Test that None is returned when streak is not cached."""
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

        with patch("app.redis_client.redis.from_url") as mock_from_url:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.get.return_value = None
            mock_from_url.return_value = mock_client

            result = get_cached_streak(123)

            assert result is None
            mock_client.get.assert_called_once_with("streak:123")

    def test_returns_cached_value(self, monkeypatch):
        """Test that cached streak value is returned."""
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

        with patch("app.redis_client.redis.from_url") as mock_from_url:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.get.return_value = "42"
            mock_from_url.return_value = mock_client

            result = get_cached_streak(123)

            assert result == 42

    def test_returns_none_on_redis_error(self, monkeypatch):
        """Test graceful handling of Redis errors during get."""
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

        with patch("app.redis_client.redis.from_url") as mock_from_url:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.get.side_effect = redis.RedisError("Connection lost")
            mock_from_url.return_value = mock_client

            result = get_cached_streak(123)

            assert result is None


class TestSetCachedStreak:
    """Tests for set_cached_streak function."""

    def test_does_nothing_when_client_unavailable(self, monkeypatch):
        """Test that function returns gracefully when Redis unavailable."""
        monkeypatch.delenv("REDIS_URL", raising=False)

        # Should not raise
        set_cached_streak(123, 5)

    def test_caches_streak_with_ttl(self, monkeypatch):
        """Test that streak is cached with correct TTL."""
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

        with patch("app.redis_client.redis.from_url") as mock_from_url:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_from_url.return_value = mock_client

            set_cached_streak(123, 5)

            mock_client.setex.assert_called_once_with(
                "streak:123", STREAK_CACHE_TTL, 5
            )

    def test_handles_redis_error_gracefully(self, monkeypatch):
        """Test graceful handling of Redis errors during set."""
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

        with patch("app.redis_client.redis.from_url") as mock_from_url:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.setex.side_effect = redis.RedisError("Connection lost")
            mock_from_url.return_value = mock_client

            # Should not raise
            set_cached_streak(123, 5)


class TestInvalidateStreakCache:
    """Tests for invalidate_streak_cache function."""

    def test_does_nothing_when_client_unavailable(self, monkeypatch):
        """Test that function returns gracefully when Redis unavailable."""
        monkeypatch.delenv("REDIS_URL", raising=False)

        # Should not raise
        invalidate_streak_cache(123)

    def test_deletes_cached_streak(self, monkeypatch):
        """Test that cached streak is deleted."""
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

        with patch("app.redis_client.redis.from_url") as mock_from_url:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_from_url.return_value = mock_client

            invalidate_streak_cache(123)

            mock_client.delete.assert_called_once_with("streak:123")

    def test_handles_redis_error_gracefully(self, monkeypatch):
        """Test graceful handling of Redis errors during delete."""
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

        with patch("app.redis_client.redis.from_url") as mock_from_url:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.delete.side_effect = redis.RedisError("Connection lost")
            mock_from_url.return_value = mock_client

            # Should not raise
            invalidate_streak_cache(123)
