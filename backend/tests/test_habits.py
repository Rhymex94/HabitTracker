from app.models import ProgressEntry

import datetime
import pytest


def test_create_habit(client, test_user, test_auth_headers):
    # Send a valid habit creation request
    response = client.post(
        "/api/habits",
        headers=test_auth_headers,
        json={
            "name": "Test Habit",
            "type": "above",
            "target": 1,
            "frequency": "daily",
            "user_id": test_user.id,
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == "Test Habit"
    assert data["data"]["type"] == "above"
    assert data["data"]["target"] == 1
    assert data["data"]["frequency"] == "daily"


def test_create_habit_with_zero_target_value(client, test_user, test_auth_headers):
    # Send a valid habit creation request
    request_data = {
        "name": "Test Habit",
        "type": "above",
        "target": 0,
        "frequency": "daily",
        "user_id": test_user.id,
    }
    response = client.post("/api/habits", headers=test_auth_headers, json=request_data)

    assert response.status_code == 400

    request_data["type"] = "below"
    response = client.post("/api/habits", headers=test_auth_headers, json=request_data)

    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == "Test Habit"
    assert data["data"]["type"] == "below"
    assert data["data"]["target"] == 0
    assert data["data"]["frequency"] == "daily"


def test_get_all_habits(client, test_habits, test_auth_headers):
    response = client.get("/api/habits", headers=test_auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 2  # We created 2 habits
    names = [habit["name"] for habit in data["data"]]
    assert "Drink Water" in names
    assert "Exercise" in names
    assert "Read" not in names


def test_get_habits_no_habits(client, test_auth_headers):
    response = client.get("/api/habits", headers=test_auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"] == []


def test_delete_habit(client, test_habits, test_auth_headers):
    habit_to_delete = test_habits[0]

    # Delete the habit
    response = client.delete(
        f"/api/habits/{habit_to_delete.id}", headers=test_auth_headers
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["message"] == "Habit deleted successfully."

    # Try to fetch it again to confirm deletion
    fetch_response = client.get("/api/habits", headers=test_auth_headers)
    fetch_data = fetch_response.get_json()

    habit_ids = [habit["id"] for habit in fetch_data["data"]]
    assert habit_to_delete.id not in habit_ids


def test_delete_habit_cascades_progress_entries(
    client, app, test_habits, test_auth_headers
):
    habit_to_delete = test_habits[0]

    # Create a ProgressEntry linked to the habit
    with app.app_context():
        progress_entry = ProgressEntry(
            date=datetime.date(day=1, month=1, year=2024), value=1, habit_id=habit_to_delete.id
        )
        from app import db

        db.session.add(progress_entry)
        db.session.commit()

        # Confirm that the ProgressEntry exists
        assert ProgressEntry.query.filter_by(habit_id=habit_to_delete.id).count() == 1

    # Delete the Habit
    response = client.delete(
        f"/api/habits/{habit_to_delete.id}", headers=test_auth_headers
    )
    assert response.status_code == 200

    # Confirm that the ProgressEntry is gone
    with app.app_context():
        entries_remaining = ProgressEntry.query.filter_by(
            habit_id=habit_to_delete.id
        ).count()
        assert entries_remaining == 0


def test_create_and_retrieve_habit_with_unit(client, test_user, test_auth_headers):
    # Create a habit with a unit
    response = client.post(
        "/api/habits",
        headers=test_auth_headers,
        json={
            "name": "Run",
            "type": "above",
            "target": 5,
            "frequency": "daily",
            "unit": "km",
            "user_id": test_user.id,
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == "Run"
    assert data["data"]["type"] == "above"
    assert data["data"]["target"] == 5
    assert data["data"]["frequency"] == "daily"
    assert data["data"]["unit"] == "km"

    habit_id = data["data"]["id"]

    # Retrieve the habit and verify unit is present
    response = client.get("/api/habits", headers=test_auth_headers)
    assert response.status_code == 200
    habits = response.get_json()["data"]

    created_habit = next((h for h in habits if h["id"] == habit_id), None)
    assert created_habit is not None
    assert created_habit["unit"] == "km"

    # Update the habit with a different unit
    response = client.patch(
        f"/api/habits/{habit_id}",
        headers=test_auth_headers,
        json={"unit": "miles"},
    )
    assert response.status_code == 200

    # Verify the update worked
    response = client.get("/api/habits", headers=test_auth_headers)
    habits = response.get_json()["data"]
    updated_habit = next((h for h in habits if h["id"] == habit_id), None)
    assert updated_habit["unit"] == "miles"


def test_create_habit_without_unit(client, test_user, test_auth_headers):
    # Create a habit without a unit (should be None/null)
    response = client.post(
        "/api/habits",
        headers=test_auth_headers,
        json={
            "name": "Meditate",
            "type": "above",
            "target": 1,
            "frequency": "daily",
            "user_id": test_user.id,
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == "Meditate"
    assert data["data"]["unit"] is None


@pytest.mark.parametrize(
    "progress_value,expected_completed",
    [
        (3, False),  # Below target (3 < 5)
        (5, True),   # Equal to target (5 = 5)
        (7, True),   # Above target (7 > 5)
    ],
    ids=["not_completed", "completed", "exceeded"],
)
def test_habit_completion_above_type(
    client, test_user, test_auth_headers, progress_value, expected_completed
):
    """Test ABOVE type habit completion with different progress values"""
    # Create an ABOVE habit with target 5
    response = client.post(
        "/api/habits",
        headers=test_auth_headers,
        json={
            "name": "Run",
            "type": "above",
            "target": 5,
            "frequency": "daily",
            "user_id": test_user.id,
        },
    )
    habit_id = response.get_json()["data"]["id"]

    # Add progress
    client.post(
        "/api/progress",
        headers=test_auth_headers,
        json={
            "habit_id": habit_id,
            "value": progress_value,
            "date": datetime.date.today().isoformat(),
        },
    )

    # Fetch habits and check completion status
    response = client.get("/api/habits", headers=test_auth_headers)
    habits = response.get_json()["data"]
    habit = next((h for h in habits if h["id"] == habit_id), None)

    assert habit is not None
    assert habit["is_completed"] is expected_completed


@pytest.mark.parametrize(
    "progress_value,expected_completed",
    [
        (3, False),   # Above target (3 > 2)
        (2, True),    # Equal to target (2 = 2)
        (None, True), # No progress (0 < 2)
    ],
    ids=["not_completed", "completed", "zero_progress"],
)
def test_habit_completion_below_type(
    client, test_user, test_auth_headers, progress_value, expected_completed
):
    """Test BELOW type habit completion with different progress values"""
    # Create a BELOW habit with target 2
    response = client.post(
        "/api/habits",
        headers=test_auth_headers,
        json={
            "name": "Limit Coffee",
            "type": "below",
            "target": 2,
            "frequency": "daily",
            "user_id": test_user.id,
        },
    )
    habit_id = response.get_json()["data"]["id"]

    # Add progress if value is provided
    if progress_value is not None:
        client.post(
            "/api/progress",
            headers=test_auth_headers,
            json={
                "habit_id": habit_id,
                "value": progress_value,
                "date": datetime.date.today().isoformat(),
            },
        )

    # Fetch habits and check completion status
    response = client.get("/api/habits", headers=test_auth_headers)
    habits = response.get_json()["data"]
    habit = next((h for h in habits if h["id"] == habit_id), None)

    assert habit is not None
    assert habit["is_completed"] is expected_completed


def test_habit_completion_binary_habit(client, test_user, test_auth_headers):
    """Test binary habit (target=1) completion"""
    # Create a binary habit (target=1)
    response = client.post(
        "/api/habits",
        headers=test_auth_headers,
        json={
            "name": "Meditate",
            "type": "above",
            "target": 1,
            "frequency": "daily",
            "user_id": test_user.id,
        },
    )
    habit_id = response.get_json()["data"]["id"]

    # No progress - should not be completed
    response = client.get("/api/habits", headers=test_auth_headers)
    habits = response.get_json()["data"]
    habit = next((h for h in habits if h["id"] == habit_id), None)
    assert habit["is_completed"] is False

    # Add progress of 1
    client.post(
        "/api/progress",
        headers=test_auth_headers,
        json={
            "habit_id": habit_id,
            "value": 1,
            "date": datetime.date.today().isoformat(),
        },
    )

    # Should now be completed
    response = client.get("/api/habits", headers=test_auth_headers)
    habits = response.get_json()["data"]
    habit = next((h for h in habits if h["id"] == habit_id), None)
    assert habit["is_completed"] is True


def test_habit_completion_target_zero(client, test_user, test_auth_headers):
    """Test BELOW habit with target 0 (e.g., 'No smoking')"""
    # Create a BELOW habit with target 0
    response = client.post(
        "/api/habits",
        headers=test_auth_headers,
        json={
            "name": "No Smoking",
            "type": "below",
            "target": 0,
            "frequency": "daily",
            "user_id": test_user.id,
        },
    )
    habit_id = response.get_json()["data"]["id"]

    # No progress - should be completed
    response = client.get("/api/habits", headers=test_auth_headers)
    habits = response.get_json()["data"]
    habit = next((h for h in habits if h["id"] == habit_id), None)
    assert habit["is_completed"] is True

    # Add any progress - should not be completed
    client.post(
        "/api/progress",
        headers=test_auth_headers,
        json={
            "habit_id": habit_id,
            "value": 1,
            "date": datetime.date.today().isoformat(),
        },
    )

    response = client.get("/api/habits", headers=test_auth_headers)
    habits = response.get_json()["data"]
    habit = next((h for h in habits if h["id"] == habit_id), None)
    assert habit["is_completed"] is False


def test_update_habit_prevents_attribute_injection(
    client, app, test_user, test_auth_headers
):
    """Test that protected fields like user_id and id cannot be modified via PATCH"""
    from app.models import User
    from app import db
    from app.auth import get_hashed_password

    # Create a second user to attempt user_id hijacking
    with app.app_context():
        hashed_password = get_hashed_password("password123")
        other_user = User(username="otheruser", password=hashed_password)
        db.session.add(other_user)
        db.session.commit()
        other_user_id = other_user.id

    # Create a habit for test_user
    response = client.post(
        "/api/habits",
        headers=test_auth_headers,
        json={
            "name": "Original Habit",
            "type": "above",
            "target": 5,
            "frequency": "daily",
            "user_id": test_user.id,
        },
    )
    assert response.status_code == 201
    habit_data = response.get_json()
    habit_id = habit_data["data"]["id"]
    original_user_id = test_user.id

    # Attempt to modify protected fields via PATCH
    response = client.patch(
        f"/api/habits/{habit_id}",
        headers=test_auth_headers,
        json={
            "name": "Updated Habit",
            "user_id": other_user_id,  # Try to change owner (should be ignored)
            "id": 99999,  # Try to change ID (should be ignored)
        },
    )
    assert response.status_code == 200

    # Verify that only allowed fields were updated
    with app.app_context():
        from app.models import Habit

        updated_habit = db.session.get(Habit, habit_id)
        assert updated_habit is not None
        assert updated_habit.name == "Updated Habit"  # Allowed field was updated
        assert updated_habit.user_id == original_user_id  # Protected field unchanged
        assert updated_habit.id == habit_id  # Protected field unchanged

    # Verify habit still belongs to original user by fetching habits
    response = client.get("/api/habits", headers=test_auth_headers)
    habits = response.get_json()["data"]
    habit = next((h for h in habits if h["id"] == habit_id), None)
    assert habit is not None
    assert habit["name"] == "Updated Habit"


@pytest.mark.parametrize(
    "field,value,expected_error",
    [
        ("name", "a" * 121, "must not exceed 120 characters"),
        ("name", "", "name is required"),
        ("unit", "a" * 21, "must not exceed 20 characters"),
        ("target", -1, "cannot be negative"),
        ("target", 1000001, "too large"),
        ("target", "not a number", "must be a number"),
    ],
    ids=["name_too_long", "name_empty", "unit_too_long", "target_negative", "target_too_large", "target_not_number"],
)
def test_create_habit_input_validation(client, test_user, test_auth_headers, field, value, expected_error):
    """Test input validation for habit creation"""
    data = {
        "name": "Test Habit",
        "type": "above",
        "target": 1,
        "frequency": "daily",
        "user_id": test_user.id,
    }
    data[field] = value

    response = client.post("/api/habits", headers=test_auth_headers, json=data)
    assert response.status_code == 400
    resp_data = response.get_json()
    assert resp_data["success"] is False
    assert expected_error in resp_data["message"].lower()


@pytest.mark.parametrize(
    "field,value,expected_error",
    [
        ("name", "a" * 121, "must not exceed 120 characters"),
        ("name", "", "name is required"),
        ("unit", "a" * 21, "must not exceed 20 characters"),
        ("target", -1, "cannot be negative"),
        ("target", 1000001, "too large"),
    ],
    ids=["name_too_long", "name_empty", "unit_too_long", "target_negative", "target_too_large"],
)
def test_update_habit_input_validation(client, test_user, test_auth_headers, field, value, expected_error):
    """Test input validation for habit updates"""
    # Create a habit first
    response = client.post(
        "/api/habits",
        headers=test_auth_headers,
        json={
            "name": "Test Habit",
            "type": "above",
            "target": 5,
            "frequency": "daily",
            "user_id": test_user.id,
        },
    )
    habit_id = response.get_json()["data"]["id"]

    # Try to update with invalid value
    update_data = {field: value}
    response = client.patch(
        f"/api/habits/{habit_id}",
        headers=test_auth_headers,
        json=update_data,
    )
    assert response.status_code == 400
    resp_data = response.get_json()
    assert resp_data["success"] is False
    assert expected_error in resp_data["message"].lower()
