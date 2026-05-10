def test_login_page(client):
    with client.session_transaction() as sess:
        sess.clear()
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Workforce Developer Hub" in response.data
    assert b"Authorized users only" in response.data


def test_login_invalid(client):
    with client.session_transaction() as sess:
        sess.clear()
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
    assert b"central platform for project management" in response.data
