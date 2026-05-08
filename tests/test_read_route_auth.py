import json
import uuid
from datetime import datetime

import pytest

from devhub.extensions import db
from devhub.models import Document, Package, ProgressEntry, Project, Script, TrackedFile


@pytest.fixture()
def seeded_internal_data(app):
    token = uuid.uuid4().hex
    project_name = f"SENSITIVE_PROJECT_{token}"
    doc_title = f"SENSITIVE_DOC_{token}"
    package_name = f"SENSITIVE_PACKAGE_{token}"
    tracked_path = f"/workspace/private/{token}/secret.txt"

    with app.app_context():
        project = Project(name=project_name, slug=f"project-{token}", status="active")
        db.session.add(project)
        db.session.flush()

        doc = Document(title=doc_title, content="confidential", project_id=project.id)
        script = Script(name=f"SENSITIVE_SCRIPT_{token}", project_id=project.id, risk_level="safe")
        progress = ProgressEntry(title=f"SENSITIVE_PROGRESS_{token}", project_id=project.id)
        package = Package(
            filename=f"pkg-{token}.zip",
            quarantine_path=f"quarantine/{token}/pkg.zip",
            manifest_valid=True,
            manifest_data=json.dumps({"name": package_name, "version": "1.0.0"}),
            status="quarantined",
        )
        tracked = TrackedFile(file_path=tracked_path, project_id=project.id, last_modified=datetime.utcnow())
        db.session.add_all([doc, script, progress, package, tracked])
        db.session.commit()

        return {
            "project_slug": project.slug,
            "project_name": project_name,
            "doc_id": doc.id,
            "doc_title": doc_title,
            "script_id": script.id,
            "progress_id": progress.id,
            "package_id": package.id,
            "package_name": package_name,
            "tracked_path": tracked_path,
        }


@pytest.mark.parametrize(
    "path_builder",
    [
        lambda data: "/search?q=test",
        lambda data: "/files",
        lambda data: "/docs/",
        lambda data: f"/docs/{data['doc_id']}",
        lambda data: "/projects/",
        lambda data: f"/projects/{data['project_slug']}",
        lambda data: "/packages/",
        lambda data: f"/packages/{data['package_id']}",
        lambda data: "/scripts/",
        lambda data: f"/scripts/{data['script_id']}",
        lambda data: "/progress/",
        lambda data: f"/progress/{data['progress_id']}",
        lambda data: "/progress/report",
    ],
)
def test_anonymous_read_routes_redirect_to_login(client, seeded_internal_data, path_builder):
    with client.session_transaction() as sess:
        sess.clear()

    response = client.get(path_builder(seeded_internal_data), follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_anonymous_project_page_does_not_render_sensitive_name(client, seeded_internal_data):
    with client.session_transaction() as sess:
        sess.clear()

    response = client.get(
        f"/projects/{seeded_internal_data['project_slug']}",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Sign in to manage" in response.data
    assert seeded_internal_data["project_name"].encode() not in response.data
    assert seeded_internal_data["doc_title"].encode() not in response.data


def test_anonymous_package_page_does_not_render_manifest(client, seeded_internal_data):
    with client.session_transaction() as sess:
        sess.clear()

    response = client.get(
        f"/packages/{seeded_internal_data['package_id']}",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Sign in to manage" in response.data
    assert seeded_internal_data["package_name"].encode() not in response.data


def test_anonymous_files_page_does_not_render_tracked_paths(client, seeded_internal_data):
    with client.session_transaction() as sess:
        sess.clear()

    response = client.get("/files", follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign in to manage" in response.data
    assert seeded_internal_data["tracked_path"].encode() not in response.data
