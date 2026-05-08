import pytest


def _authenticate(client, admin_user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_user.id)
        sess["_fresh"] = True


def test_api_status(client):
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "version" in data
    assert data["script_execution_enabled"] is False
    assert data["package_install_enabled"] is False


def test_api_search(client, admin_user):
    _authenticate(client, admin_user)
    response = client.get("/api/search?q=test")
    assert response.status_code == 200
    data = response.get_json()
    assert "docs" in data
    assert "progress" in data
    assert "scripts" in data


def test_api_projects(client, admin_user):
    _authenticate(client, admin_user)
    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_api_docs(client, admin_user):
    _authenticate(client, admin_user)
    response = client.get("/api/docs")
    assert response.status_code == 200


def test_api_scripts(client, admin_user):
    _authenticate(client, admin_user)
    response = client.get("/api/scripts")
    assert response.status_code == 200


def test_api_recent_progress(client, admin_user):
    _authenticate(client, admin_user)
    response = client.get("/api/progress/recent")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


@pytest.mark.parametrize(
    "path",
    ["/api/search?q=", "/api/progress/recent", "/api/projects", "/api/docs", "/api/scripts"],
)
def test_api_protected_endpoints_redirect_anonymous(client, path):
    with client.session_transaction() as sess:
        sess.clear()
    response = client.get(path, follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
