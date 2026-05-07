def test_app_starts(client):
    response = client.get("/")
    assert response.status_code == 200


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


def test_primary_navigation_after_login(client, admin_user):
    with client.session_transaction() as sess:
        sess.clear()
    response = client.post(
        "/login",
        data={
            "email": "testadmin@example.com",
            "password": "testpass123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    for link in (
        b"Dashboard",
        b"Projects",
        b"Docs",
        b"Progress",
        b"Scripts",
        b"Packages",
        b"Admin",
    ):
        assert link in response.data
    client.get("/logout")
