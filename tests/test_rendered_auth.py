import uuid

import pytest

from devhub.app import create_app
from devhub.config import TestingConfig
from devhub.models import Document, Package, ProgressEntry, Project, Script


@pytest.mark.parametrize(
    "path",
    [
        "/docs/",
        "/docs/1",
        "/projects/",
        "/projects/example-project",
        "/progress/",
        "/progress/1",
        "/progress/report",
        "/scripts/",
        "/scripts/1",
        "/packages/",
        "/packages/1",
    ],
)
def test_rendered_read_only_routes_anonymous_redirect_to_login(path):
    anon_client = create_app(TestingConfig).test_client()
    response = anon_client.get(path)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_health_and_api_status_remain_public(client):
    health = client.get("/health")
    assert health.status_code == 200

    status = client.get("/api/status")
    assert status.status_code == 200


def test_rendered_read_only_index_routes_authenticated_ok(client, admin_user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_user.id)
        sess["_fresh"] = True

    for path in ("/docs/", "/projects/", "/progress/", "/progress/report", "/scripts/", "/packages/"):
        response = client.get(path)
        assert response.status_code == 200


def test_rendered_read_only_detail_routes_authenticated_ok(app, client, db, admin_user):
    unique = uuid.uuid4().hex
    with app.app_context():
        project = Project(name=f"Auth Project {unique}", slug=f"auth-project-{unique}")
        db.session.add(project)
        db.session.flush()

        doc = Document(title=f"Auth Doc {unique}", project_id=project.id)
        progress = ProgressEntry(title=f"Auth Progress {unique}", project_id=project.id)
        script = Script(name=f"Auth Script {unique}", project_id=project.id, risk_level="safe")
        package = Package(
            filename=f"auth-{unique}.zip",
            quarantine_path=f"quarantine/{unique}/auth-{unique}.zip",
            manifest_valid=True,
            status="quarantined",
            risk_level="safe",
            requires_manual_review=True,
        )
        db.session.add_all([doc, progress, script, package])
        db.session.commit()

        doc_id = doc.id
        entry_id = progress.id
        script_id = script.id
        package_id = package.id
        project_slug = project.slug

    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_user.id)
        sess["_fresh"] = True

    for path in (
        f"/docs/{doc_id}",
        f"/projects/{project_slug}",
        f"/progress/{entry_id}",
        f"/scripts/{script_id}",
        f"/packages/{package_id}",
    ):
        response = client.get(path)
        assert response.status_code == 200
