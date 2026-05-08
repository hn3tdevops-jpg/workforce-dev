import pytest

from devhub.app import create_app
from devhub.config import TestingConfig
from devhub.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        yield _db
        _db.session.rollback()


class _UserProxy:
    """Lightweight proxy holding just the user id to avoid detached-instance errors."""

    def __init__(self, user_id: int) -> None:
        self.id = user_id


@pytest.fixture(scope="session")
def admin_user(app):
    with app.app_context():
        from devhub.models import User

        user = User.query.filter_by(email="testadmin@example.com").first()
        if not user:
            user = User(email="testadmin@example.com", is_admin=True)
            user.set_password("testpass123")
            _db.session.add(user)
            _db.session.commit()
        return _UserProxy(user.id)


@pytest.fixture(scope="function")
def authenticated_client(app, admin_user):
    client = app.test_client()
    login_response = client.post(
        "/login",
        data={"email": "testadmin@example.com", "password": "testpass123"},
        follow_redirects=False,
    )
    assert login_response.status_code == 302
    yield client
    client.get("/logout", follow_redirects=False)
