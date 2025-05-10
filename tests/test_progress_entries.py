from app import db
from app.models import ProgressEntry

def test_create_progress_entry(client, test_habits):
    habit = test_habits[0]  # Use a habit from the fixture
    payload = {
        "habit_id": habit.id,
        "date": "2024-05-01",
        "value": 1
    }

    response = client.post("/progress", json=payload)
    assert response.status_code == 201
    data = response.get_json()

    assert data["habit_id"] == habit.id
    assert data["date"] == "2024-05-01"
    assert data["value"] == 1

    entry = db.session.query(ProgressEntry).filter_by(habit_id=habit.id, date="2024-05-01").first()
    assert entry is not None
    assert entry.value == 1