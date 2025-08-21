from app.models import ProgressEntry

import datetime


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
    assert data["name"] == "Test Habit"
    assert data["type"] == "above"
    assert data["target"] == 1
    assert data["frequency"] == "daily"


def test_get_all_habits(client, test_habits, test_auth_headers):
    response = client.get("/api/habits", headers=test_auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2  # We created 2 habits
    names = [habit["name"] for habit in data]
    assert "Drink Water" in names
    assert "Exercise" in names
    assert "Read" not in names


def test_get_habits_no_habits(client, test_auth_headers):
    response = client.get("/api/habits", headers=test_auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data == []


def test_delete_habit(client, test_habits, test_auth_headers):
    habit_to_delete = test_habits[0]

    # Delete the habit
    response = client.delete(
        f"/api/habits/{habit_to_delete.id}", headers=test_auth_headers
    )
    assert response.status_code == 200
    assert response.get_json()["message"] == "Habit deleted successfully."

    # Try to fetch it again to confirm deletion
    fetch_response = client.get("/api/habits", headers=test_auth_headers)
    data = fetch_response.get_json()

    habit_ids = [habit["id"] for habit in data]
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
