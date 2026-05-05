def test_api_status(client):
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "version" in data
    assert data["script_execution_enabled"] is False
    assert data["package_install_enabled"] is False


def test_api_projects(client):
    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_api_docs(client):
    response = client.get("/api/docs")
    assert response.status_code == 200


def test_api_scripts(client):
    response = client.get("/api/scripts")
    assert response.status_code == 200


def test_api_recent_progress(client):
    response = client.get("/api/progress/recent")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
