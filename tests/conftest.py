import pytest
from app import create_app
from app.models import db, User


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