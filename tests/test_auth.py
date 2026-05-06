def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Sign In" in response.data


def test_login_invalid(client):
    response = client.post(
        "/login",
        data={
            "email": "notauser@example.com",
            "password": "wrongpassword",
        },
        follow_redirects=True,
    )
    assert b"Invalid email or password" in response.data


def test_login_success(client, admin_user):
    response = client.post(
        "/login",
        data={
            "email": "testadmin@example.com",
            "password": "testpass123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
