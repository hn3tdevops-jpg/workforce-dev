def test_search_endpoint(authenticated_client):
    response = authenticated_client.get("/api/search?q=test")
    assert response.status_code == 200
    data = response.get_json()
    assert "docs" in data
    assert "progress" in data
    assert "scripts" in data


def test_search_no_query(authenticated_client):
    response = authenticated_client.get("/api/search")
    assert response.status_code == 400


def test_search_page(authenticated_client):
    response = authenticated_client.get("/search?q=workforce")
    assert response.status_code == 200
