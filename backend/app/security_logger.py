"""
Structured security event logging for authentication and authorization events.

Logs are written to stderr in JSON format for easy parsing by log aggregation
services. Each log entry includes:
- timestamp: ISO 8601 format
- event: Type of security event
- ip: Client IP address
- Additional context (username, reason, etc.)
"""

import json
import sys
from datetime import datetime, timezone
from flask import request


def _get_client_ip() -> str:
    """Get the client IP address, considering proxy headers."""
    # Check X-Forwarded-For header (set by reverse proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs; first is the client
        return forwarded_for.split(",")[0].strip()
    # Check X-Real-IP header (alternative proxy header)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    # Fall back to direct connection IP
    return request.remote_addr or "unknown"


def _log_security_event(event: str, **kwargs) -> None:
    """Write a structured security log entry to stderr."""
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "ip": _get_client_ip(),
        **kwargs,
    }
    print(json.dumps(log_entry), file=sys.stderr)


def log_login_success(username: str, user_id: int) -> None:
    """Log a successful login."""
    _log_security_event(
        "login_success",
        username=username,
        user_id=user_id,
    )


def log_login_failure(username: str, reason: str = "invalid_credentials") -> None:
    """Log a failed login attempt."""
    _log_security_event(
        "login_failure",
        username=username,
        reason=reason,
    )


def log_signup_success(username: str, user_id: int) -> None:
    """Log a successful account creation."""
    _log_security_event(
        "signup_success",
        username=username,
        user_id=user_id,
    )


def log_signup_failure(username: str, reason: str) -> None:
    """Log a failed signup attempt."""
    _log_security_event(
        "signup_failure",
        username=username,
        reason=reason,
    )


def log_token_validation_failure(reason: str) -> None:
    """Log a failed token validation attempt."""
    _log_security_event(
        "token_validation_failure",
        reason=reason,
        path=request.path,
        method=request.method,
    )


def log_unauthorized_access(path: str, method: str, reason: str = "missing_token") -> None:
    """Log an unauthorized access attempt to a protected resource."""
    _log_security_event(
        "unauthorized_access",
        path=path,
        method=method,
        reason=reason,
    )
