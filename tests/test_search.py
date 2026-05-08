def _authenticated_client(app, admin_user):
    client = app.test_client()
    client.post(
        "/login",
        data={"email": "testadmin@example.com", "password": "testpass123"},
        follow_redirects=False,
    )
    return client


def test_search_endpoint(app, admin_user):
    client = _authenticated_client(app, admin_user)
    response = client.get("/api/search?q=test")
    assert response.status_code == 200
    data = response.get_json()
    assert "docs" in data
    assert "progress" in data
    assert "scripts" in data
    client.get("/logout")


def test_search_no_query(app, admin_user):
    client = _authenticated_client(app, admin_user)
    response = client.get("/api/search")
    assert response.status_code == 400
    client.get("/logout")


def test_search_page(app, admin_user):
    client = _authenticated_client(app, admin_user)
    response = client.get("/search?q=workforce")
    assert response.status_code == 200
