import pytest


def test_api_status(app):
    client = app.test_client()
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "version" in data
    assert data["script_execution_enabled"] is False
    assert data["package_install_enabled"] is False


def test_api_search(authenticated_client):
    response = authenticated_client.get("/api/search?q=test")
    assert response.status_code == 200
    data = response.get_json()
    assert "docs" in data
    assert "progress" in data
    assert "scripts" in data


def test_api_projects(authenticated_client):
    response = authenticated_client.get("/api/projects")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_api_docs(authenticated_client):
    response = authenticated_client.get("/api/docs")
    assert response.status_code == 200


def test_api_scripts(authenticated_client):
    response = authenticated_client.get("/api/scripts")
    assert response.status_code == 200


def test_api_recent_progress(authenticated_client):
    response = authenticated_client.get("/api/progress/recent")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


@pytest.mark.parametrize("path", ["/api/status", "/health"])
def test_api_public_endpoints_allow_anonymous(app, path):
    client = app.test_client(use_cookies=False)
    response = client.get(path, follow_redirects=False)
    assert response.status_code == 200


@pytest.mark.parametrize(
    "path",
    ["/api/search?q=", "/api/search?q=test", "/api/progress/recent", "/api/projects", "/api/docs", "/api/scripts"],
)
def test_api_protected_endpoints_redirect_anonymous(app, path):
    client = app.test_client(use_cookies=False)
    response = client.get(path, follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
