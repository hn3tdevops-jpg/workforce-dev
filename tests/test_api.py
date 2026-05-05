def test_health(client):
    resp = client.get('/api/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'ok'
    assert data['service'] == 'workforce-devhub'


def test_status(client):
    resp = client.get('/api/status')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'projects' in data


def test_projects_list(client):
    resp = client.get('/api/projects')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_project_detail_not_found(client):
    resp = client.get('/api/projects/nonexistent-slug')
    assert resp.status_code == 404


def test_search_empty(client):
    resp = client.get('/api/search')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'results' in data


def test_search_with_query(client, app):
    resp = client.get('/api/search?q=test')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'query' in data
    assert 'results' in data
