import pytest
from devhub.models import User

def login(client, username, password):
    return client.post('/auth/login', data={'username': username, 'password': password},
                       follow_redirects=True)

@pytest.fixture
def registration_enabled(app):
    original = app.config.get('DEVHUB_ALLOW_REGISTRATION', False)
    app.config['DEVHUB_ALLOW_REGISTRATION'] = True
    yield
    app.config['DEVHUB_ALLOW_REGISTRATION'] = original

def test_register_new_user(client, db, registration_enabled):
    resp = client.post('/auth/register', data={
        'username': 'newuser', 'email': 'new@example.com', 'password': 'secret'
    }, follow_redirects=True)
    assert resp.status_code == 200
    user = User.query.filter_by(username='newuser').first()
    assert user is not None

def test_register_first_user_is_admin(client, db, registration_enabled):
    resp = client.post('/auth/register', data={
        'username': 'firstuser', 'email': 'first@example.com', 'password': 'secret'
    }, follow_redirects=True)
    assert resp.status_code == 200
    user = User.query.filter_by(username='firstuser').first()
    assert user.is_admin is True

def test_register_duplicate_username(client, admin_user, registration_enabled):
    resp = client.post('/auth/register', data={
        'username': 'admin', 'email': 'other@example.com', 'password': 'secret'
    }, follow_redirects=True)
    assert b'already taken' in resp.data

def test_register_duplicate_email(client, admin_user, registration_enabled):
    resp = client.post('/auth/register', data={
        'username': 'other', 'email': 'admin@example.com', 'password': 'secret'
    }, follow_redirects=True)
    assert b'already registered' in resp.data

def test_login_valid(client, admin_user):
    resp = login(client, 'admin', 'adminpass')
    assert resp.status_code == 200
    assert b'Dashboard' in resp.data

def test_login_invalid_password(client, admin_user):
    resp = login(client, 'admin', 'wrongpass')
    assert b'Invalid username or password' in resp.data

def test_login_unknown_user(client, db):
    resp = login(client, 'nobody', 'pass')
    assert b'Invalid username or password' in resp.data

def test_logout(client, admin_user):
    login(client, 'admin', 'adminpass')
    resp = client.get('/auth/logout', follow_redirects=True)
    assert b'logged out' in resp.data

def test_register_missing_fields(client, db, registration_enabled):
    resp = client.post('/auth/register', data={
        'username': '', 'email': '', 'password': ''
    }, follow_redirects=True)
    assert b'required' in resp.data

def test_register_disabled_redirects_to_login(client, db):
    resp = client.get('/auth/register', follow_redirects=True)
    assert resp.status_code == 200
    assert b'Registration is currently disabled' in resp.data
    assert b'Login' in resp.data
