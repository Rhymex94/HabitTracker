from datetime import date, timedelta
import pytest
from app import db
from app.models import ProgressEntry


def test_create_progress_entry(client, test_habits, test_auth_headers):
    habit = test_habits[0]  # Use a habit from the fixture
    payload = {"habit_id": habit.id, "date": "2024-05-01", "value": 1}

    response = client.post("/api/progress", json=payload, headers=test_auth_headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True

    assert data["data"]["habit_id"] == habit.id
    assert data["data"]["date"] == "2024-05-01"
    assert data["data"]["value"] == 1

    entry = (
        db.session.query(ProgressEntry)
        .filter_by(habit_id=habit.id, date="2024-05-01")
        .first()
    )
    assert entry is not None
    assert entry.value == 1


def test_get_progress_entries(client, progress_entries, test_auth_headers):
    habit_id = progress_entries[0].habit_id

    response = client.get(
        f"/api/progress?habit_id={habit_id}&all=true", headers=test_auth_headers
    )
    assert response.status_code == 200

    data = response.get_json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert len(data["data"]) == len(progress_entries)

    returned_ids = {entry["id"] for entry in data["data"]}
    expected_ids = {e.id for e in progress_entries}
    assert returned_ids == expected_ids


def test_get_progress_entries_date_filter(client, progress_entries, test_auth_headers):
    habit_id = progress_entries[0].habit_id

    response = client.get(
        f"/api/progress?habit_id={habit_id}&start_date=2024-05-02&end_date=2024-05-03&all=true",
        headers=test_auth_headers,
    )
    assert response.status_code == 200

    data = response.get_json()
    assert data["success"] is True
    assert len(data["data"]) == 2
    returned_dates = {entry["date"] for entry in data["data"]}
    assert returned_dates == {"2024-05-02", "2024-05-03"}


def test_get_progress_entries_invalid_habit(client, test_auth_headers):
    response = client.get("/api/progress?habit_id=999999", headers=test_auth_headers)
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False


def test_get_progress_entries_empty_result(client, progress_entries, test_auth_headers):
    habit_id = progress_entries[0].habit_id

    response = client.get(
        f"/api/progress?habit_id={habit_id}&start_date=2024-01-01&end_date=2024-01-31",
        headers=test_auth_headers,
    )
    assert response.status_code == 200

    data = response.get_json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 0


def test_delete_existing_progress_entry(client, progress_entries, test_auth_headers):
    entry_to_delete = progress_entries[0]
    habit_id = entry_to_delete.habit_id

    # Perform deletion
    response = client.delete(
        f"/api/progress/{entry_to_delete.id}", headers=test_auth_headers
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert f"{entry_to_delete.id}" in data["message"]

    # Verify it's no longer returned
    response_check = client.get(
        f"/api/progress?habit_id={habit_id}", headers=test_auth_headers
    )
    ids = {entry["id"] for entry in response_check.get_json()["data"]}
    assert entry_to_delete.id not in ids


def test_delete_nonexistent_progress_entry(client, test_auth_headers):
    non_existent_id = 999999

    response = client.delete(
        f"/api/progress/{non_existent_id}", headers=test_auth_headers
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()


def test_create_progress_entry_future_date(client, test_habits, test_auth_headers):
    habit = test_habits[0]
    future_date = (date.today() + timedelta(days=1)).isoformat()
    payload = {"habit_id": habit.id, "date": future_date, "value": 5}

    response = client.post("/api/progress", json=payload, headers=test_auth_headers)
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "future" in data["message"].lower()


def test_delete_progress_entry_without_authentication(client, progress_entries):
    """Test that unauthenticated users cannot delete progress entries"""
    entry_to_delete = progress_entries[0]

    # Attempt to delete without auth headers
    response = client.delete(f"/api/progress/{entry_to_delete.id}")
    assert response.status_code == 401
    # Auth errors may have different format, just check response exists
    assert response.get_json() is not None

    # Verify the entry still exists
    entry = db.session.get(ProgressEntry, entry_to_delete.id)
    assert entry is not None


def test_delete_progress_entry_unauthorized_user(client, progress_entries, test_habits):
    """Test that users cannot delete other users' progress entries"""
    from app.models import User
    from app.auth import create_access_token

    # test_habits fixture creates "anotheruser" - we need it loaded
    assert len(test_habits) > 0  # Ensure habits are loaded

    # Get a progress entry that belongs to test_user
    entry_to_delete = progress_entries[0]

    # Find the "anotheruser" created in test_habits fixture
    another_user = User.query.filter_by(username="anotheruser").first()
    assert another_user is not None

    # Create auth headers for the other user
    other_user_token = create_access_token(another_user.id)
    other_user_headers = {"Authorization": f"Bearer {other_user_token}"}

    # Attempt to delete test_user's progress entry as another_user
    response = client.delete(
        f"/api/progress/{entry_to_delete.id}", headers=other_user_headers
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()

    # Verify the entry still exists
    entry = db.session.get(ProgressEntry, entry_to_delete.id)
    assert entry is not None
    assert entry.id == entry_to_delete.id


@pytest.mark.parametrize(
    "value,expected_error",
    [
        (-1, "cannot be negative"),
        (1000001, "too large"),
        ("not a number", "must be a number"),
    ],
    ids=["negative", "too_large", "not_number"],
)
def test_create_progress_entry_input_validation(client, test_habits, test_auth_headers, value, expected_error):
    """Test input validation for progress entry creation"""
    habit = test_habits[0]
    payload = {"habit_id": habit.id, "date": "2024-05-01", "value": value}

    response = client.post("/api/progress", json=payload, headers=test_auth_headers)
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert expected_error in data["message"].lower()


def test_create_progress_entry_missing_habit_id(client, test_auth_headers):
    """Test that missing habit_id returns 400."""
    payload = {"date": "2024-05-01", "value": 1}

    response = client.post("/api/progress", json=payload, headers=test_auth_headers)
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "missing required fields" in data["message"].lower()


def test_create_progress_entry_missing_value(client, test_habits, test_auth_headers):
    """Test that missing value returns 400."""
    habit = test_habits[0]
    payload = {"habit_id": habit.id, "date": "2024-05-01"}

    response = client.post("/api/progress", json=payload, headers=test_auth_headers)
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "missing required fields" in data["message"].lower()


def test_create_progress_entry_habit_not_found(client, test_auth_headers):
    """Test that non-existent habit returns 404."""
    payload = {"habit_id": 999999, "date": "2024-05-01", "value": 1}

    response = client.post("/api/progress", json=payload, headers=test_auth_headers)
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()


def test_create_progress_entry_default_date(client, test_habits, test_auth_headers):
    """Test that missing date defaults to current date."""
    from datetime import datetime, timezone

    habit = test_habits[0]
    payload = {"habit_id": habit.id, "value": 1}

    response = client.post("/api/progress", json=payload, headers=test_auth_headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True

    # The date should be today's date
    today = datetime.now(timezone.utc).date().isoformat()
    assert data["data"]["date"] == today


def test_get_progress_entries_without_habit_id(client, progress_entries, test_auth_headers):
    """Test fetching all progress entries for a user without habit_id filter."""
    response = client.get("/api/progress?all=true", headers=test_auth_headers)
    assert response.status_code == 200

    data = response.get_json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    # Should return all progress entries for the user
    assert len(data["data"]) == len(progress_entries)


def test_get_progress_entries_invalid_start_date_format(client, test_auth_headers):
    """Test that invalid start_date format returns 400."""
    response = client.get(
        "/api/progress?start_date=invalid-date&all=true", headers=test_auth_headers
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "invalid start_date format" in data["message"].lower()


def test_get_progress_entries_invalid_end_date_format(client, test_auth_headers):
    """Test that invalid end_date format returns 400."""
    response = client.get(
        "/api/progress?end_date=not-a-date&all=true", headers=test_auth_headers
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "invalid end_date format" in data["message"].lower()
