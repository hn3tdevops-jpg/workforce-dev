import os
import pytest
from workforce_devhub import create_app
from workforce_devhub.config import TestingConfig
from workforce_devhub.extensions import db as _db
from workforce_devhub.models import User, Project


@pytest.fixture(scope='session')
def app():
    os.makedirs('instance/test_uploads', exist_ok=True)
    os.makedirs('instance/test_quarantine', exist_ok=True)
    application = create_app(TestingConfig)
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope='session')
def init_db(app):
    with app.app_context():
        if not User.query.filter_by(username='testadmin').first():
            u = User(username='testadmin', email='admin@test.com', is_admin=True)
            u.set_password('testpass123')
            _db.session.add(u)
        if not Project.query.filter_by(slug='test-project').first():
            p = Project(name='Test Project', slug='test-project', description='Test')
            _db.session.add(p)
        _db.session.commit()


@pytest.fixture
def auth_client(client, init_db):
    """A test client that is logged in."""
    client.post('/auth/login', data={'username': 'testadmin', 'password': 'testpass123'})
    yield client
    client.get('/auth/logout')
