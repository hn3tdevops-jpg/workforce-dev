from devhub.app import create_app
from devhub.config import TestingConfig
from devhub.extensions import db as _db


def _make_isolated_authed_client():
    """Return an authenticated test client with its own isolated in-memory DB.

    Using a dedicated app instance prevents Flask-Login's per-app-context
    ``g._login_user`` cache from leaking into the shared session-scoped client.
    """
    isolated_app = create_app(TestingConfig)
    with isolated_app.app_context():
        _db.create_all()
        from devhub.models import User

        user = User(email="searchtest@example.com", is_admin=True)
        user.set_password("testpass")
        _db.session.add(user)
        _db.session.commit()
        uid = user.id
    client = isolated_app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
    return client


def test_search_endpoint_anonymous_denied():
    anon_client = create_app(TestingConfig).test_client()
    response = anon_client.get("/api/search?q=test")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_search_endpoint_authenticated():
    authed = _make_isolated_authed_client()
    response = authed.get("/api/search?q=test")
    assert response.status_code == 200
    data = response.get_json()
    assert "docs" in data
    assert "progress" in data
    assert "scripts" in data


def test_search_no_query_anonymous_denied():
    anon_client = create_app(TestingConfig).test_client()
    response = anon_client.get("/api/search")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_search_no_query_authenticated():
    authed = _make_isolated_authed_client()
    response = authed.get("/api/search")
    assert response.status_code == 400


def test_search_page():
    anon_client = create_app(TestingConfig).test_client()
    response = anon_client.get("/search")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_search_page_with_query_requires_login():
    anon_client = create_app(TestingConfig).test_client()
    response = anon_client.get("/search?q=test")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_files_page_requires_login():
    anon_client = create_app(TestingConfig).test_client()
    response = anon_client.get("/files")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_search_page_allows_authenticated_user(client, admin_user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_user.id)
        sess["_fresh"] = True
    response = client.get("/search?q=workforce")
    assert response.status_code == 200


def test_files_page_allows_authenticated_user(client, admin_user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_user.id)
        sess["_fresh"] = True
    response = client.get("/files")
    assert response.status_code == 200
