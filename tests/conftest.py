import pytest
from app import create_app
from app.models import db, Habit, User, ProgressEntry
from app.enums import HabitType, HabitFrequency  # Adjust imports if needed

from datetime import date


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture
def app():
    app = create_app(TestConfig())

    with app.app_context():
        db.create_all()

        user = User(username="test_user")
        db.session.add(user)
        db.session.commit()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def test_user(app):
    user = User(username="testuser")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def test_habits(app, test_user):
    habits = [
        Habit(
            name="Drink Water",
            type=HabitType.BINARY,
            target_value=1,
            frequency=HabitFrequency.DAILY,
            user_id=test_user.id,
        ),
        Habit(
            name="Exercise",
            type=HabitType.QUANTITATIVE,
            target_value=30,
            frequency=HabitFrequency.WEEKLY,
            user_id=test_user.id,
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