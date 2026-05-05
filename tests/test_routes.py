import pytest
from devhub.models import Project, Doc, Script

def login(client, username, password):
    return client.post('/auth/login', data={'username': username, 'password': password},
                       follow_redirects=True)

# --- API ---

def test_health(client, db):
    resp = client.get('/api/v1/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'ok'

def test_api_projects_empty(client, db):
    resp = client.get('/api/v1/projects')
    assert resp.status_code == 200
    assert resp.get_json() == []

def test_api_docs_empty(client, db):
    resp = client.get('/api/v1/docs')
    assert resp.status_code == 200
    assert resp.get_json() == []

def test_api_search_empty(client, db):
    resp = client.get('/api/v1/search?q=test')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'docs' in data

# --- Auth redirects ---

def test_dashboard_redirect_unauthenticated(client, db):
    resp = client.get('/dashboard')
    assert resp.status_code == 302

def test_root_redirect(client, db):
    resp = client.get('/')
    assert resp.status_code == 302

# --- Docs ---

def test_docs_index_public(client, db):
    resp = client.get('/docs/')
    assert resp.status_code == 200

def test_docs_new_requires_login(client, db):
    resp = client.get('/docs/new')
    assert resp.status_code == 302

def test_docs_create(client, admin_user):
    login(client, 'admin', 'adminpass')
    resp = client.post('/docs/new', data={
        'title': 'Test Doc', 'content': 'Some content', 'category': 'general'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Test Doc' in resp.data

def test_docs_view(client, admin_user):
    login(client, 'admin', 'adminpass')
    client.post('/docs/new', data={
        'title': 'View Me', 'content': 'content', 'category': ''
    }, follow_redirects=True)
    doc = Doc.query.filter_by(title='View Me').first()
    resp = client.get(f'/docs/{doc.slug}')
    assert resp.status_code == 200

def test_docs_404(client, db):
    resp = client.get('/docs/nonexistent-slug')
    assert resp.status_code == 404

# --- Dashboard ---

def test_dashboard_authenticated(client, admin_user):
    login(client, 'admin', 'adminpass')
    resp = client.get('/dashboard')
    assert resp.status_code == 200
    assert b'Dashboard' in resp.data

# --- Admin ---

def test_admin_requires_admin(client, regular_user):
    login(client, 'testuser', 'userpass')
    resp = client.get('/admin/')
    assert resp.status_code == 403

def test_admin_accessible_by_admin(client, admin_user):
    login(client, 'admin', 'adminpass')
    resp = client.get('/admin/')
    assert resp.status_code == 200

def test_admin_users(client, admin_user):
    login(client, 'admin', 'adminpass')
    resp = client.get('/admin/users')
    assert resp.status_code == 200
    assert b'admin' in resp.data

def test_admin_audit(client, admin_user):
    login(client, 'admin', 'adminpass')
    resp = client.get('/admin/audit')
    assert resp.status_code == 200

# --- Scripts ---

def test_scripts_index_requires_login(client, db):
    resp = client.get('/scripts/')
    assert resp.status_code == 302

def test_scripts_new_requires_admin(client, regular_user):
    login(client, 'testuser', 'userpass')
    resp = client.get('/scripts/new')
    assert resp.status_code == 403

def test_scripts_create(client, admin_user):
    login(client, 'admin', 'adminpass')
    resp = client.post('/scripts/new', data={
        'name': 'My Script', 'description': 'Desc', 'content': 'print(1)', 'language': 'python'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'My Script' in resp.data

# --- Reports ---

def test_reports_index_requires_login(client, db):
    resp = client.get('/reports/')
    assert resp.status_code == 302

def test_reports_new_requires_login(client, db):
    resp = client.get('/reports/new')
    assert resp.status_code == 302

# --- Packages ---

def test_packages_index_requires_login(client, db):
    resp = client.get('/packages/')
    assert resp.status_code == 302
