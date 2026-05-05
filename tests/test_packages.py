import json
import os
import tempfile
import zipfile

from devhub.package_validator import validate_package


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
