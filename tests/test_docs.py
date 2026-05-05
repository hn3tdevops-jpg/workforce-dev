from workforce_devhub.extensions import db
from workforce_devhub.models import Document, Project


def test_docs_index(auth_client):
    resp = auth_client.get('/docs/')
    assert resp.status_code == 200
    assert b'Documents' in resp.data


def test_docs_new_get(auth_client):
    resp = auth_client.get('/docs/new')
    assert resp.status_code == 200
    assert b'New Document' in resp.data


def test_docs_create(auth_client, app):
    resp = auth_client.post(
        '/docs/new',
        data={
            'title': 'Test Doc',
            'summary': 'A test document',
            'content': '# Test\nContent here.',
            'doc_type': 'general',
            'status': 'draft',
            'project_id': '0',
            'external_url': '',
            'tags': 'test',
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        doc = Document.query.filter_by(title='Test Doc').first()
        assert doc is not None
        assert doc.content == '# Test\nContent here.'


def test_docs_detail(auth_client, app):
    with app.app_context():
        doc = Document.query.filter_by(title='Test Doc').first()
        if not doc:
            doc = Document(title='Detail Test Doc', status='draft')
            db.session.add(doc)
            db.session.commit()
        doc_id = doc.id
    resp = auth_client.get(f'/docs/{doc_id}')
    assert resp.status_code == 200


def test_docs_edit(auth_client, app):
    with app.app_context():
        doc = Document.query.filter_by(title='Test Doc').first()
        if not doc:
            doc = Document(title='Test Doc', status='draft')
            db.session.add(doc)
            db.session.commit()
        doc_id = doc.id

    resp = auth_client.post(
        f'/docs/{doc_id}/edit',
        data={
            'title': 'Test Doc Updated',
            'summary': 'Updated',
            'content': '# Updated',
            'doc_type': 'guide',
            'status': 'canonical',
            'project_id': '0',
            'external_url': '',
            'tags': '',
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        doc = Document.query.get(doc_id)
        assert doc.status == 'canonical'
