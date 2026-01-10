def test_signup_password_too_short(client):
    """Test that passwords shorter than 8 characters are rejected"""
    response = client.post(
        "/api/auth/signup",
        json={"username": "testuser", "password": "Short1"},
    )
    assert response.status_code == 400
    assert "at least 8 characters" in response.get_json()["error"]


def test_signup_password_no_lowercase(client):
    """Test that passwords without lowercase letters are rejected"""
    response = client.post(
        "/api/auth/signup",
        json={"username": "testuser", "password": "PASSWORD123"},
    )
    assert response.status_code == 400
    assert "lowercase letter" in response.get_json()["error"]


def test_signup_password_no_uppercase(client):
    """Test that passwords without uppercase letters are rejected"""
    response = client.post(
        "/api/auth/signup",
        json={"username": "testuser", "password": "password123"},
    )
    assert response.status_code == 400
    assert "uppercase letter" in response.get_json()["error"]


def test_signup_password_no_number(client):
    """Test that passwords without numbers are rejected"""
    response = client.post(
        "/api/auth/signup",
        json={"username": "testuser", "password": "PasswordOnly"},
    )
    assert response.status_code == 400
    assert "number" in response.get_json()["error"]


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


def test_signup_username_too_short(client):
    """Test that usernames shorter than 3 characters are rejected"""
    response = client.post(
        "/api/auth/signup",
        json={"username": "ab", "password": "ValidPass123"},
    )
    assert response.status_code == 400
    assert "at least 3 characters" in response.get_json()["error"]


def test_signup_username_too_long(client):
    """Test that usernames longer than 64 characters are rejected"""
    long_username = "a" * 65
    response = client.post(
        "/api/auth/signup",
        json={"username": long_username, "password": "ValidPass123"},
    )
    assert response.status_code == 400
    assert "must not exceed 64 characters" in response.get_json()["error"]


def test_signup_username_invalid_characters(client):
    """Test that usernames with invalid characters are rejected"""
    response = client.post(
        "/api/auth/signup",
        json={"username": "test@user!", "password": "ValidPass123"},
    )
    assert response.status_code == 400
    assert "letters, numbers, hyphens, and underscores" in response.get_json()["error"]


def test_signup_username_valid_characters(client):
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


def test_signup_missing_username(client):
    """Test that missing username is rejected"""
    response = client.post(
        "/api/auth/signup",
        json={"password": "ValidPass123"},
    )
    assert response.status_code == 400
    assert "required" in response.get_json()["error"]


def test_signup_missing_password(client):
    """Test that missing password is rejected"""
    response = client.post(
        "/api/auth/signup",
        json={"username": "testuser"},
    )
    assert response.status_code == 400
    assert "required" in response.get_json()["error"]
