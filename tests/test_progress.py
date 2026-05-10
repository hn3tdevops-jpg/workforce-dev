from devhub.models import ProgressEntry


def test_progress_index(client, admin_user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_user.id)
        sess["_fresh"] = True
    response = client.get("/progress/")
    assert response.status_code == 200


def test_progress_report(client, admin_user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_user.id)
        sess["_fresh"] = True
    response = client.get("/progress/report")
    assert response.status_code == 200


def test_progress_create(client, app, admin_user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_user.id)
        sess["_fresh"] = True

    with app.app_context():
        from devhub.models import Project

        project = Project.query.first()
        project_id = project.id if project else 0

    response = client.post(
        "/progress/new",
        data={
            "title": "Test Progress Entry",
            "description": "A test description",
            "status": "in-progress",
            "project_id": project_id,
            "evidence_links": "https://example.com",
            "file_paths": "",
            "commands_run": "",
            "test_results": "",
            "notes": "",
            "tags": "test",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
