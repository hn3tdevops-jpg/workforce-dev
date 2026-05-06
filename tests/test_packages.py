import json
import os
import tempfile
import zipfile

from devhub.package_validator import _is_within_root, validate_package


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


# ---------------------------------------------------------------------------
# Hardened path validation tests (Fix 3)
# ---------------------------------------------------------------------------


def test_is_within_root_exact():
    """A path equal to the root is within it."""
    assert _is_within_root("/workspace_api", "/workspace_api") is True


def test_is_within_root_child():
    """A direct child is within the root."""
    assert _is_within_root("/workspace_api/src/foo.py", "/workspace_api") is True


def test_is_within_root_sibling_prefix_escape():
    """Sibling-prefix attack: /workspace_api_evil must not be inside /workspace_api."""
    assert _is_within_root("/workspace_api_evil", "/workspace_api") is False


def test_is_within_root_sibling_prefix_sub():
    """Another sibling-prefix variant with a subdirectory."""
    assert _is_within_root("/workspace_api_evil/src", "/workspace_api") is False


def test_is_within_root_dotdot_normalization():
    """Paths with .. segments are normalised before comparison."""
    # /workspace_api/sub/../../../etc/passwd resolves to /etc/passwd — not inside root
    assert _is_within_root("/workspace_api/sub/../../../etc/passwd", "/workspace_api") is False


def test_is_within_root_redundant_slashes():
    """Redundant slashes are normalised."""
    assert _is_within_root("/workspace_api//src//foo.py", "/workspace_api") is True


def test_workspace_root_sibling_prefix_in_manifest():
    """Absolute intended_path that looks like root but is a sibling must be rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = make_valid_package(
            tmpdir, {"intended_paths": ["/workspace_api_evil/install.py"]}
        )
        result = validate_package(zip_path, workspace_roots=["/workspace_api"])
        assert result["valid"] is False
        assert "escapes workspace roots" in result["error"]


def test_workspace_root_valid_child_path():
    """A path that genuinely lives inside the workspace root must be accepted."""
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = make_valid_package(
            tmpdir, {"intended_paths": ["/workspace_api/src/install.py"]}
        )
        result = validate_package(zip_path, workspace_roots=["/workspace_api"])
        assert result["valid"] is True


def test_workspace_root_dotdot_escape():
    """An absolute intended_path that uses .. to escape the root must be rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = make_valid_package(
            tmpdir, {"intended_paths": ["/workspace_api/../../../etc/passwd"]}
        )
        result = validate_package(zip_path, workspace_roots=["/workspace_api"])
        assert result["valid"] is False


def test_relative_dotdot_in_manifest_no_roots():
    """Relative paths with .. segments are rejected even without workspace roots."""
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = make_valid_package(tmpdir, {"intended_paths": ["../../etc/passwd"]})
        result = validate_package(zip_path)
        assert result["valid"] is False


def test_relative_path_normalisation_no_roots():
    """A clean relative path (no traversal) is accepted when no roots are configured."""
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = make_valid_package(tmpdir, {"intended_paths": ["src/module/file.py"]})
        result = validate_package(zip_path)
        assert result["valid"] is True


# ---------------------------------------------------------------------------
# Quarantine uniqueness tests (Fix 4)
# ---------------------------------------------------------------------------


def test_quarantine_unique_dirs(app, client, admin_user):
    """Two uploads of a file with the same name must be stored in different directories."""
    import io

    from devhub.models import Package

    def _make_zip_bytes():
        buf = io.BytesIO()
        manifest = {
            "package_key": "dup-test",
            "name": "Dup Test",
            "version": "1.0.0",
            "description": "d",
            "target_project": "t",
            "intended_paths": [],
            "install_steps": [],
            "rollback_notes": "",
            "risk_level": "safe",
            "requires_manual_review": False,
        }
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("devhub-package.json", json.dumps(manifest))
        buf.seek(0)
        return buf.read()

    zip_bytes = _make_zip_bytes()

    with app.app_context():
        with client.session_transaction() as sess:
            sess["_user_id"] = str(admin_user.id)
            sess["_fresh"] = True

        r1 = client.post(
            "/packages/upload",
            data={"file": (io.BytesIO(zip_bytes), "mypackage.zip")},
            content_type="multipart/form-data",
            follow_redirects=False,
        )
        assert r1.status_code in (200, 302)

        r2 = client.post(
            "/packages/upload",
            data={"file": (io.BytesIO(zip_bytes), "mypackage.zip")},
            content_type="multipart/form-data",
            follow_redirects=False,
        )
        assert r2.status_code in (200, 302)

        pkgs = Package.query.filter_by(filename="mypackage.zip").all()
        assert len(pkgs) >= 2, "Expected at least 2 package records for same filename"

        paths = [p.quarantine_path for p in pkgs]
        # All quarantine paths must be distinct
        assert len(set(paths)) == len(paths), "Duplicate quarantine paths detected — uploads overwrite each other"
        # Each file must be in its own subdirectory
        dirs = [os.path.dirname(p) for p in paths]
        assert len(set(dirs)) == len(dirs), "Uploads share a quarantine directory"
