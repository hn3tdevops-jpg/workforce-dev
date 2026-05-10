import io
import json
import os
import tempfile
import zipfile

from devhub.package_validator import validate_package


def _login(client, user_id):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _clear_session(client):
    with client.session_transaction() as sess:
        sess.clear()


def make_valid_package(tmpdir, manifest_overrides=None):
    manifest = {
        "package_key": "test-pkg",
        "name": "Test Package",
        "version": "1.0.0",
        "description": "A test package",
        "target_project": "workforce-devhub",
        "intended_paths": ["src/test.py"],
        "install_steps": ["copy files"],
        "rollback_notes": "delete copied files",
        "risk_level": "safe",
        "requires_manual_review": True,
    }
    if manifest_overrides:
        manifest.update(manifest_overrides)

    zip_path = os.path.join(tmpdir, "test_package.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("devhub-package.json", json.dumps(manifest))
        zf.writestr("src/test.py", "print('hello')")
    return zip_path


def test_valid_package():
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = make_valid_package(tmpdir)
        result = validate_package(zip_path)
        assert result["valid"] is True
        assert result["manifest"]["name"] == "Test Package"


def test_missing_manifest():
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "no_manifest.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("src/test.py", "print('hello')")
        result = validate_package(zip_path)
        assert result["valid"] is False
        assert "Missing devhub-package.json" in result["error"]


def test_path_traversal_in_zip():
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "traversal.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr(
                "devhub-package.json",
                json.dumps(
                    {
                        "package_key": "evil",
                        "name": "Evil Package",
                        "version": "1.0.0",
                        "description": "Evil",
                        "target_project": "test",
                        "intended_paths": [],
                        "install_steps": [],
                        "rollback_notes": "",
                        "risk_level": "safe",
                        "requires_manual_review": True,
                    }
                ),
            )
            zf.writestr("../../../etc/passwd", "evil content")
        result = validate_package(zip_path)
        assert result["valid"] is False
        assert "traversal" in result["error"].lower()


def test_path_traversal_in_manifest():
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = make_valid_package(tmpdir, {"intended_paths": ["../../../etc/passwd"]})
        result = validate_package(zip_path)
        assert result["valid"] is False


def test_missing_manifest_fields():
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "incomplete.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("devhub-package.json", json.dumps({"name": "Incomplete"}))
        result = validate_package(zip_path)
        assert result["valid"] is False
        assert "Missing manifest fields" in result["error"]


def test_invalid_risk_level():
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = make_valid_package(tmpdir, {"risk_level": "nuclear"})
        result = validate_package(zip_path)
        assert result["valid"] is False
        assert "risk_level" in result["error"]


def make_zip_bytes(manifest_overrides=None):
    """Return a valid package zip as bytes."""
    manifest = {
        "package_key": "test-pkg",
        "name": "Test Package",
        "version": "1.0.0",
        "description": "A test package",
        "target_project": "workforce-devhub",
        "intended_paths": ["src/test.py"],
        "install_steps": ["copy files"],
        "rollback_notes": "delete copied files",
        "risk_level": "safe",
        "requires_manual_review": True,
    }
    if manifest_overrides:
        manifest.update(manifest_overrides)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("devhub-package.json", json.dumps(manifest))
        zf.writestr("src/test.py", "print('hello')")
    return buf.getvalue()


def test_upload_duplicate_filename_no_overwrite(client, app, admin_user):
    """Two uploads with the same original filename must produce distinct quarantine paths."""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_user.id)
        sess["_fresh"] = True

    zip_data = make_zip_bytes()

    resp1 = client.post(
        "/packages/upload",
        data={"file": (io.BytesIO(zip_data), "mypackage.zip")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    resp2 = client.post(
        "/packages/upload",
        data={"file": (io.BytesIO(zip_data), "mypackage.zip")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert resp1.status_code == 200
    assert resp2.status_code == 200

    with app.app_context():
        from devhub.models import Package

        pkgs = Package.query.filter_by(filename="mypackage.zip").all()
        assert len(pkgs) == 2, "Both uploads must be recorded"
        paths = [p.quarantine_path for p in pkgs]
        assert len(set(paths)) == len(paths), (
            "Duplicate quarantine paths — files would overwrite each other!"
        )


def test_packages_index_requires_login():
    from devhub.app import create_app
    from devhub.config import TestingConfig
    from devhub.extensions import db

    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
    client = app.test_client()
    _clear_session(client)

    response = client.get("/packages/")

    with app.app_context():
        db.session.remove()
        db.drop_all()

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_packages_view_requires_login():
    from devhub.app import create_app
    from devhub.config import TestingConfig
    from devhub.extensions import db
    from devhub.models import Package

    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        pkg = Package(
            filename="private.zip",
            quarantine_path="quarantine/private.zip",
            manifest_valid=True,
            manifest_data="{}",
            status="quarantined",
        )
        db.session.add(pkg)
        db.session.commit()
        pkg_id = pkg.id

    client = app.test_client()
    _clear_session(client)
    response = client.get(f"/packages/{pkg_id}")

    with app.app_context():
        db.session.remove()
        db.drop_all()

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_package_approve_non_admin_denied_for_existing_and_missing_ids():
    from devhub.app import create_app
    from devhub.config import TestingConfig
    from devhub.extensions import db
    from devhub.models import Package, User

    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        user = User(email="nonadmin@example.com", is_admin=False)
        user.set_password("testpass123")
        pkg = Package(
            filename="approve-me.zip",
            quarantine_path="quarantine/approve-me.zip",
            manifest_valid=True,
            manifest_data="{}",
            status="quarantined",
        )
        db.session.add_all([user, pkg])
        db.session.commit()
        user_id = user.id
        existing_pkg_id = pkg.id
        missing_pkg_id = pkg.id + 99999

    client = app.test_client()
    _clear_session(client)
    _login(client, user_id)

    existing_response = client.post(
        f"/packages/{existing_pkg_id}/approve", follow_redirects=False
    )
    missing_response = client.post(
        f"/packages/{missing_pkg_id}/approve", follow_redirects=False
    )

    with client.session_transaction() as sess:
        flashed_messages = [message for _, message in sess.get("_flashes", [])]

    with app.app_context():
        pkg = Package.query.get(existing_pkg_id)
        db.session.remove()
        db.drop_all()

    assert existing_response.status_code == 302
    assert missing_response.status_code == 302
    assert existing_response.headers["Location"].endswith("/packages/")
    assert missing_response.headers["Location"].endswith("/packages/")
    assert flashed_messages.count("Admin access required.") == 2
    assert pkg.status == "quarantined"
