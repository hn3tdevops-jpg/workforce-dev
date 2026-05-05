from workforce_devhub.extensions import db
from workforce_devhub.models import Document, ProgressEntry


def test_search_no_query(auth_client):
    resp = auth_client.get('/search/')
    assert resp.status_code == 200
    assert b'Search' in resp.data


def test_search_with_query(auth_client, app):
    with app.app_context():
        doc = Document.query.filter_by(title='Searchable Doc').first()
        if not doc:
            doc = Document(title='Searchable Doc', content='unique searchable content xyz', status='draft')
            db.session.add(doc)
            db.session.commit()

    resp = auth_client.get('/search/?q=Searchable+Doc')
    assert resp.status_code == 200
    assert b'Searchable Doc' in resp.data


def test_search_no_results(auth_client):
    resp = auth_client.get('/search/?q=xyznosuchthing99999')
    assert resp.status_code == 200
    assert b'No results' in resp.data


def test_api_search(client, app):
    with app.app_context():
        if not Document.query.filter_by(title='API Search Doc').first():
            doc = Document(title='API Search Doc', summary='api test', status='draft')
            db.session.add(doc)
            db.session.commit()

    resp = client.get('/api/search?q=API+Search+Doc')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'results' in data
