"""Input validation functions for API endpoints."""

import re
from datetime import datetime, timezone
from typing import Tuple, Optional


def validate_habit_data(data: dict, is_update: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Validate habit data for create or update operations.

    Args:
        data: Dictionary containing habit data
        is_update: True if validating for PATCH, False for POST

    Returns:
        Tuple of (is_valid, error_message). error_message is None if valid.
    """
    # Validate name (required for create, optional for update)
    if "name" in data or not is_update:
        name = data.get("name")
        if name is None or not isinstance(name, str) or len(name) == 0:
            return False, "Habit name is required"
        if len(name) > 120:
            return False, "Habit name must not exceed 120 characters"

    # Validate unit if provided
    if "unit" in data and data["unit"] is not None:
        unit = data["unit"]
        if not isinstance(unit, str):
            return False, "Unit must be a string"
        if len(unit) > 20:
            return False, "Unit must not exceed 20 characters"

    # Validate target_value
    if "target_value" in data or "target" in data:
        target = data.get("target_value") or data.get("target")
        if not isinstance(target, (int, float)):
            return False, "Target value must be a number"
        if target < 0:
            return False, "Target value cannot be negative"
        if target > 1000000:
            return False, "Target value is too large (max 1,000,000)"

    return True, None


def validate_progress_data(data: dict) -> Tuple[bool, Optional[str]]:
    """
    Validate progress entry data.

    Args:
        data: Dictionary containing progress data

    Returns:
        Tuple of (is_valid, error_message). error_message is None if valid.
    """
    value = data.get("value")

    # Validate progress value
    if not isinstance(value, (int, float)):
        return False, "Progress value must be a number"
    if value < 0:
        return False, "Progress value cannot be negative"
    if value > 1000000:
        return False, "Progress value is too large (max 1,000,000)"

    return True, None


def validate_date_string(date_str: Optional[str]) -> Tuple[bool, Optional[str], Optional[object]]:
    """
    Validate and parse a date string.

    Args:
        date_str: Date string in YYYY-MM-DD format (can be None)

    Returns:
        Tuple of (is_valid, error_message, parsed_date).
        parsed_date is None if date_str is None (will use current date).
        error_message is None if valid.
    """
    if not date_str:
        return True, None, None

    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD.", None

    # Validate that the date is not in the future
    if parsed_date > datetime.now(timezone.utc).date():
        return False, "Progress entry date cannot be in the future", None

    return True, None, parsed_date


def validate_username(username: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate username format and constraints.

    Args:
        username: The username to validate

    Returns:
        Tuple of (is_valid, error_message). error_message is None if valid.
    """
    if not username:
        return False, "Username and password are required"

    if len(username) < 3:
        return False, "Username must be at least 3 characters long"

    if len(username) > 64:
        return False, "Username must not exceed 64 characters"

    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return False, "Username can only contain letters, numbers, hyphens, and underscores"

    return True, None


def validate_password(password: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength requirements.

    Args:
        password: The password to validate

    Returns:
        Tuple of (is_valid, error_message). error_message is None if valid.
    """
    if not password:
        return False, "Username and password are required"

    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"

    return True, None


def validate_auth_credentials(username: Optional[str], password: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate authentication credentials (username and password).

    Args:
        username: The username to validate
        password: The password to validate

    Returns:
        Tuple of (is_valid, error_message). error_message is None if valid.
    """
    # Validate username
    is_valid, error_message = validate_username(username)
    if not is_valid:
        return False, error_message

    # Validate password
    is_valid, error_message = validate_password(password)
    if not is_valid:
        return False, error_message

    return True, None
