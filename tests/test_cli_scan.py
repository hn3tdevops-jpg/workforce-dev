import importlib
import os
import tempfile

from devhub.app import create_app
from devhub.extensions import db


def _write(path, content="data"):
    with open(path, "w") as f:
        f.write(content)


def test_scan_cli_honors_scanner_exclusions_from_app_config(app, runner):
    with tempfile.TemporaryDirectory() as tmpdir:
        excluded_dir = os.path.join(tmpdir, "cli_excluded")
        os.makedirs(excluded_dir)
        _write(os.path.join(excluded_dir, "secret.txt"))
        _write(os.path.join(tmpdir, "ignored.scanignore"))
        _write(os.path.join(tmpdir, "included.txt"))

        app.config["SCANNER_EXCLUDED_DIRS"] = {"cli_excluded"}
        app.config["SCANNER_EXCLUDED_EXTENSIONS"] = {"scanignore"}

        result = runner.invoke(args=["scan", "--root", tmpdir])

    assert result.exit_code == 0
    assert "Scan complete. 1 files indexed." in result.output


def test_scan_cli_honors_scanner_exclusions_from_env(monkeypatch):
    monkeypatch.setenv("DEVHUB_SCANNER_EXCLUDED_DIRS", "env_excluded")
    monkeypatch.setenv("DEVHUB_SCANNER_EXCLUDED_EXTENSIONS", ".envskip")

    import devhub.config as config_module

    importlib.reload(config_module)
    app = create_app(config_module.TestingConfig)
    runner = app.test_cli_runner()

    with app.app_context():
        db.create_all()

    with tempfile.TemporaryDirectory() as tmpdir:
        excluded_dir = os.path.join(tmpdir, "env_excluded")
        os.makedirs(excluded_dir)
        _write(os.path.join(excluded_dir, "secret.txt"))
        _write(os.path.join(tmpdir, "ignored.envskip"))
        _write(os.path.join(tmpdir, "included.txt"))

        result = runner.invoke(args=["scan", "--root", tmpdir])

    with app.app_context():
        db.session.remove()
        db.drop_all()

    assert result.exit_code == 0
    assert "Scan complete. 1 files indexed." in result.output
