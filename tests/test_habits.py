def test_create_habit(client):
    # Send a valid habit creation request
    response = client.post("/habits", json={
        "name": "Test Habit",
        "type": 1,  # BINARY
        "target_value": 1,
        "frequency": 1,  # DAILY
        "user_id": 1
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Test Habit"
    assert data["type"] == 1
    assert data["target_value"] == 1
    assert data["frequency"] == 1
    assert data["user_id"] == 1