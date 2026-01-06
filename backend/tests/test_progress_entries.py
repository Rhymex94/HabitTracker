from datetime import date, timedelta
from app import db
from app.models import ProgressEntry


def test_create_progress_entry(client, test_habits, test_auth_headers):
    habit = test_habits[0]  # Use a habit from the fixture
    payload = {"habit_id": habit.id, "date": "2024-05-01", "value": 1}

    response = client.post("/api/progress", json=payload, headers=test_auth_headers)
    assert response.status_code == 201
    data = response.get_json()

    assert data["habit_id"] == habit.id
    assert data["date"] == "2024-05-01"
    assert data["value"] == 1

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
    assert isinstance(data, list)
    assert len(data) == len(progress_entries)

    returned_ids = {entry["id"] for entry in data}
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
    assert len(data) == 2
    returned_dates = {entry["date"] for entry in data}
    assert returned_dates == {"2024-05-02", "2024-05-03"}


def test_get_progress_entries_invalid_habit(client, test_auth_headers):
    response = client.get("/api/progress?habit_id=999999", headers=test_auth_headers)
    assert response.status_code == 404


def test_get_progress_entries_empty_result(client, progress_entries, test_auth_headers):
    habit_id = progress_entries[0].habit_id

    response = client.get(
        f"/api/progress?habit_id={habit_id}&start_date=2024-01-01&end_date=2024-01-31",
        headers=test_auth_headers,
    )
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_delete_existing_progress_entry(client, progress_entries, test_auth_headers):
    entry_to_delete = progress_entries[0]
    habit_id = entry_to_delete.habit_id

    # Perform deletion
    response = client.delete(
        f"/api/progress/{entry_to_delete.id}", headers=test_auth_headers
    )
    assert response.status_code == 200
    assert f"{entry_to_delete.id}" in response.get_json()["message"]

    # Verify it's no longer returned
    response_check = client.get(
        f"/api/progress?habit_id={habit_id}", headers=test_auth_headers
    )
    ids = {entry["id"] for entry in response_check.get_json()}
    assert entry_to_delete.id not in ids


def test_delete_nonexistent_progress_entry(client, test_auth_headers):
    non_existent_id = 999999

    response = client.delete(
        f"/api/progress/{non_existent_id}", headers=test_auth_headers
    )
    assert response.status_code == 404
    assert "not found" in response.get_json()["error"].lower()


def test_create_progress_entry_future_date(client, test_habits, test_auth_headers):
    habit = test_habits[0]
    future_date = (date.today() + timedelta(days=1)).isoformat()
    payload = {"habit_id": habit.id, "date": future_date, "value": 5}

    response = client.post("/api/progress", json=payload, headers=test_auth_headers)
    assert response.status_code == 400
    assert "future" in response.get_json()["error"].lower()
