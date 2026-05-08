import pytest


def _authenticated_client(app, admin_user):
    client = app.test_client()
    client.post(
        "/login",
        data={"email": "testadmin@example.com", "password": "testpass123"},
        follow_redirects=False,
    )
    return client


def test_api_status(app):
    client = app.test_client()
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "version" in data
    assert data["script_execution_enabled"] is False
    assert data["package_install_enabled"] is False


def test_api_search(app, admin_user):
    client = _authenticated_client(app, admin_user)
    response = client.get("/api/search?q=test")
    assert response.status_code == 200
    data = response.get_json()
    assert "docs" in data
    assert "progress" in data
    assert "scripts" in data
    client.get("/logout")


def test_api_projects(app, admin_user):
    client = _authenticated_client(app, admin_user)
    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    client.get("/logout")


def test_api_docs(app, admin_user):
    client = _authenticated_client(app, admin_user)
    response = client.get("/api/docs")
    assert response.status_code == 200
    client.get("/logout")


def test_api_scripts(app, admin_user):
    client = _authenticated_client(app, admin_user)
    response = client.get("/api/scripts")
    assert response.status_code == 200
    client.get("/logout")


def test_api_recent_progress(app, admin_user):
    client = _authenticated_client(app, admin_user)
    response = client.get("/api/progress/recent")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    client.get("/logout")


@pytest.mark.parametrize(
    "path",
    ["/api/search?q=", "/api/progress/recent", "/api/projects", "/api/docs", "/api/scripts"],
)
def test_api_protected_endpoints_redirect_anonymous(app, path):
    client = app.test_client(use_cookies=False)
    response = client.get(path, follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
