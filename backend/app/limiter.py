"""Rate limiting configuration for the application."""

import os

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def _get_storage_uri() -> str:
    """Get storage URI for rate limiter. Uses Redis if available, else memory."""
    redis_url = os.environ.get("REDIS_URL")
    return redis_url if redis_url else "memory://"


limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=_get_storage_uri(),
    default_limits=["200 per day", "50 per hour"],
)
