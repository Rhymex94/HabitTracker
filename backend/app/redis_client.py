"""Redis client for caching streak calculations."""

import os
from typing import Optional

import redis

STREAK_CACHE_TTL = 300  # 5 minutes

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    """Get or create a Redis client. Returns None if Redis is unavailable."""
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    redis_url = os.environ.get("REDIS_URL")
    if not redis_url:
        return None

    try:
        _redis_client = redis.from_url(redis_url, decode_responses=True)
        _redis_client.ping()
        return _redis_client
    except redis.RedisError:
        _redis_client = None
        return None


def get_cached_streak(habit_id: int) -> Optional[int]:
    """Get cached streak for a habit. Returns None if not cached or Redis unavailable."""
    client = get_redis_client()
    if client is None:
        return None

    try:
        value = client.get(f"streak:{habit_id}")
        return int(value) if value is not None else None
    except redis.RedisError:
        return None


def set_cached_streak(habit_id: int, streak: int) -> None:
    """Cache a streak value for a habit."""
    client = get_redis_client()
    if client is None:
        return

    try:
        client.setex(f"streak:{habit_id}", STREAK_CACHE_TTL, streak)
    except redis.RedisError:
        pass


def invalidate_streak_cache(habit_id: int) -> None:
    """Invalidate cached streak for a habit."""
    client = get_redis_client()
    if client is None:
        return

    try:
        client.delete(f"streak:{habit_id}")
    except redis.RedisError:
        pass
