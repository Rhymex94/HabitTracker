import pytest
import time


@pytest.mark.parametrize(
    "password,expected_error_fragment",
    [
        ("Short1", "at least 8 characters"),
        ("PASSWORD123", "lowercase letter"),
        ("password123", "uppercase letter"),
        ("PasswordOnly", "number"),
    ],
    ids=["too_short", "no_lowercase", "no_uppercase", "no_number"],
)
def test_signup_invalid_password(client, password, expected_error_fragment):
    """Test that invalid passwords are rejected with appropriate error messages"""
    response = client.post(
        "/api/auth/signup",
        json={"username": "testuser", "password": password},
    )
    assert response.status_code == 400
    assert expected_error_fragment in response.get_json()["error"]


def test_signup_valid_password(client):
    """Test that valid passwords are accepted"""
    response = client.post(
        "/api/auth/signup",
        json={"username": "testuser", "password": "ValidPass123"},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "token" in data
    assert "user_id" in data
    assert data["username"] == "testuser"


@pytest.mark.parametrize(
    "username,expected_error_fragment",
    [
        ("ab", "at least 3 characters"),
        ("a" * 65, "must not exceed 64 characters"),
        ("test@user!", "letters, numbers, hyphens, and underscores"),
    ],
    ids=["too_short", "too_long", "invalid_characters"],
)
def test_signup_invalid_username(client, username, expected_error_fragment):
    """Test that invalid usernames are rejected with appropriate error messages"""
    response = client.post(
        "/api/auth/signup",
        json={"username": username, "password": "ValidPass123"},
    )
    assert response.status_code == 400
    assert expected_error_fragment in response.get_json()["error"]


def test_signup_valid_username(client):
    """Test that usernames with valid characters (letters, numbers, hyphens, underscores) are accepted"""
    response = client.post(
        "/api/auth/signup",
        json={"username": "valid_user-123", "password": "ValidPass123"},
    )
    assert response.status_code == 201
    assert response.get_json()["username"] == "valid_user-123"


def test_signup_duplicate_username(client):
    """Test that duplicate usernames are rejected"""
    # Create first user
    client.post(
        "/api/auth/signup",
        json={"username": "testuser", "password": "ValidPass123"},
    )

    # Try to create second user with same username
    response = client.post(
        "/api/auth/signup",
        json={"username": "testuser", "password": "AnotherPass456"},
    )
    assert response.status_code == 400
    assert "already exists" in response.get_json()["error"]


@pytest.mark.parametrize(
    "payload,expected_error_fragment",
    [
        ({"password": "ValidPass123"}, "required"),
        ({"username": "testuser"}, "required"),
    ],
    ids=["missing_username", "missing_password"],
)
def test_signup_missing_fields(client, payload, expected_error_fragment):
    """Test that missing required fields are rejected"""
    response = client.post("/api/auth/signup", json=payload)
    assert response.status_code == 400
    assert expected_error_fragment in response.get_json()["error"]


def test_login_rate_limit(client):
    """Test that login endpoint is rate limited to 5 requests per minute"""
    # Make 5 login attempts (at the limit)
    for _ in range(5):
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password123"},
        )
        # All should return 401 (invalid credentials) or 200 (success if user exists)
        assert response.status_code in [200, 401]

    # The 6th attempt should be rate limited
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    assert response.status_code == 429  # Too Many Requests
    # Flask-Limiter returns plain text error message by default
    assert response.data is not None
