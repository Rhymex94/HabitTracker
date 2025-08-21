import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash

from app import create_app
from app.auth import create_access_token
from app.models import db, Habit, User, ProgressEntry
from app.enums import HabitType, HabitFrequency  # Adjust imports if needed


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture
def app():
    app = create_app(TestConfig())

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def test_user(app):
    user = User(
        username="testuser",
        password=generate_password_hash("Testpass123!").encode("utf-8"),
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def test_auth_headers(app, test_user):
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_habits(app, test_user):

    another_user = User(
        username="anotheruser",
        password=generate_password_hash("Testpass123!").encode("utf-8"),
    )
    db.session.add(another_user)
    db.session.commit()

    habits = [
        Habit(
            name="Drink Water",
            type=HabitType.ABOVE,
            target_value=1,
            frequency=HabitFrequency.DAILY,
            user_id=test_user.id,
        ),
        Habit(
            name="Exercise",
            type=HabitType.ABOVE,
            target_value=30,
            frequency=HabitFrequency.WEEKLY,
            user_id=test_user.id,
        ),
        Habit(
            name="Read",
            type=HabitType.ABOVE,
            target_value=15,
            frequency=HabitFrequency.DAILY,
            user_id=another_user.id,
        ),
    ]
    db.session.add_all(habits)
    db.session.commit()
    return habits


@pytest.fixture
def progress_entries(app, test_habits):
    habit = test_habits[0]

    entries = [
        ProgressEntry(habit_id=habit.id, date=date(2024, 5, 1), value=1),
        ProgressEntry(habit_id=habit.id, date=date(2024, 5, 2), value=2),
        ProgressEntry(habit_id=habit.id, date=date(2024, 5, 3), value=3),
    ]
    db.session
    db.session.add_all(entries)
    db.session.commit()
    return entries


@pytest.fixture
def mock_habits(monkeypatch, request, test_user):
    habits_data = request.param["habits"]
    path = request.param["path"]

    habits = [Habit(user_id=test_user.id, **data) for data in habits_data]

    query_mock = MagicMock()
    query_mock.filter_by.return_value = query_mock
    query_mock.order_by.return_value = query_mock
    query_mock.all.return_value = habits
    query_mock.__iter__.return_value = iter(habits)

    monkeypatch.setattr(path, query_mock)
    return habits


@pytest.fixture
def mock_progress_entries(monkeypatch, request):
    entries = request.param["entries"]
    path = request.param["path"]

    called = MagicMock()
    called.filter.return_value = called
    called.order_by.return_value = called
    called.all.return_value = entries
    called.__iter__.return_value = iter(entries)

    query_callable = MagicMock()
    query_callable.return_value = called

    monkeypatch.setattr(path, query_callable)
    return entries
