from devhub.models import Document, Project


def test_docs_index(client):
    response = client.get("/docs/")
    assert response.status_code == 200


def test_docs_create(client, app, admin_user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_user.id)
        sess["_fresh"] = True

    with app.app_context():
        project = Project.query.first()
        project_id = project.id if project else 0

    response = client.post(
        "/docs/new",
        data={
            "title": "Test Document",
            "summary": "A test summary",
            "content": "Test content",
            "doc_type": "markdown",
            "status": "draft",
            "project_id": project_id,
            "tags": "test",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_docs_view(client, app):
    with app.app_context():
        doc = Document.query.first()
        if doc:
            response = client.get(f"/docs/{doc.id}")
            assert response.status_code == 200
