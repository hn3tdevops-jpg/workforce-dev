def test_login_page_loads(client):
    resp = client.get('/auth/login')
    assert resp.status_code == 200
    assert b'Log In' in resp.data


def test_login_invalid(client, init_db):
    resp = client.post('/auth/login', data={'username': 'wrong', 'password': 'wrong'})
    assert resp.status_code == 200
    assert b'Invalid' in resp.data


def test_login_success(client, init_db):
    resp = client.post(
        '/auth/login',
        data={'username': 'testadmin', 'password': 'testpass123'},
        follow_redirects=True,
    )
    assert resp.status_code == 200


def test_logout(auth_client):
    resp = auth_client.get('/auth/logout', follow_redirects=True)
    assert resp.status_code == 200
    assert b'logged out' in resp.data


def test_protected_redirects_to_login(client):
    resp = client.get('/', follow_redirects=False)
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']
