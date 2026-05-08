def test_search_endpoint(client):
    response = client.get("/api/search?q=test")
    assert response.status_code == 200
    data = response.get_json()
    assert "docs" in data
    assert "progress" in data
    assert "scripts" in data


def test_search_no_query(client):
    response = client.get("/api/search")
    assert response.status_code == 400


def test_search_page(client, admin_user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_user.id)
        sess["_fresh"] = True
    response = client.get("/search?q=workforce")
    assert response.status_code == 200
