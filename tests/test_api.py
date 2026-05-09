from devhub.app import create_app
from devhub.config import TestingConfig
from devhub.extensions import db as _db

from tests.helpers import make_isolated_authed_client


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
    authed = make_isolated_authed_client()
    response = authed.get("/api/projects")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_api_docs_authenticated():
    authed = make_isolated_authed_client()
    response = authed.get("/api/docs")
    assert response.status_code == 200


def test_api_scripts_authenticated():
    authed = make_isolated_authed_client()
    response = authed.get("/api/scripts")
    assert response.status_code == 200


def test_api_recent_progress_authenticated():
    authed = make_isolated_authed_client()
    response = authed.get("/api/progress/recent")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
