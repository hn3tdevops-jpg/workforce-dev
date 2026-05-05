import pytest
from devhub.app import create_app
from devhub.extensions import db as _db
from devhub.models import User
from devhub.extensions import bcrypt

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        _db.session.remove()
        _db.drop_all()
        _db.create_all()
        yield _db
        _db.session.remove()

@pytest.fixture(scope='function')
def client(app, db):
    return app.test_client()

@pytest.fixture(scope='function')
def admin_user(db):
    hashed = bcrypt.generate_password_hash('adminpass').decode('utf-8')
    user = User(username='admin', email='admin@example.com',
                password_hash=hashed, is_admin=True)
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture(scope='function')
def regular_user(db):
    hashed = bcrypt.generate_password_hash('userpass').decode('utf-8')
    user = User(username='testuser', email='testuser@example.com',
                password_hash=hashed, is_admin=False)
    db.session.add(user)
    db.session.commit()
    return user

def login(client, username, password):
    return client.post('/auth/login', data={'username': username, 'password': password},
                       follow_redirects=True)
