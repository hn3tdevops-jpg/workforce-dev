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

        user = User(email="apitest@example.com", is_admin=True)
        user.set_password("testpass")
        _db.session.add(user)
        _db.session.commit()
        uid = user.id
    client = isolated_app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
    return client


def test_api_status_public(client):
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "version" in data
    assert data["script_execution_enabled"] is False
    assert data["package_install_enabled"] is False


# --- Anonymous access should be denied (redirect to /login) ---


def test_api_projects_anonymous_denied():
    anon_client = create_app(TestingConfig).test_client()
    response = anon_client.get("/api/projects")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_api_docs_anonymous_denied():
    anon_client = create_app(TestingConfig).test_client()
    response = anon_client.get("/api/docs")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_api_scripts_anonymous_denied():
    anon_client = create_app(TestingConfig).test_client()
    response = anon_client.get("/api/scripts")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_api_recent_progress_anonymous_denied():
    anon_client = create_app(TestingConfig).test_client()
    response = anon_client.get("/api/progress/recent")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


# --- Authenticated access should still succeed ---


def test_api_projects_authenticated():
    authed = _make_isolated_authed_client()
    response = authed.get("/api/projects")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_api_docs_authenticated():
    authed = _make_isolated_authed_client()
    response = authed.get("/api/docs")
    assert response.status_code == 200


def test_api_scripts_authenticated():
    authed = _make_isolated_authed_client()
    response = authed.get("/api/scripts")
    assert response.status_code == 200


def test_api_recent_progress_authenticated():
    authed = _make_isolated_authed_client()
    response = authed.get("/api/progress/recent")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
