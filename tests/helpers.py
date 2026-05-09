"""Shared test helper utilities."""

from devhub.app import create_app
from devhub.config import TestingConfig
from devhub.extensions import db as _db


def make_isolated_authed_client():
    """Return an authenticated test client with its own isolated in-memory DB.

    Using a dedicated app instance prevents Flask-Login's per-app-context
    ``g._login_user`` cache from leaking into the shared session-scoped client.
    """
    isolated_app = create_app(TestingConfig)
    with isolated_app.app_context():
        _db.create_all()
        from devhub.models import User

        user = User(email="isolated_authed@example.com", is_admin=True)
        user.set_password("testpass")
        _db.session.add(user)
        _db.session.commit()
        uid = user.id
    client = isolated_app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
    return client
