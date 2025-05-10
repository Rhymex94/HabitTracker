import pytest
from app import create_app
from app.models import db, Habit, User
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
            target_value=30,  # 30 minutes
            frequency=HabitFrequency.WEEKLY,
            user_id=test_user.id,
        ),
    ]
    db.session.add_all(habits)
    db.session.commit()
    return habits
