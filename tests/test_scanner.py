import os
import tempfile

from devhub.app import create_app
from devhub.config import TestingConfig
from devhub.extensions import db
from devhub.models import TrackedFile
from devhub.scanner import _DEFAULT_EXCLUDED_DIRS, _DEFAULT_EXCLUDED_EXTENSIONS, scan_workspace


def test_scan_empty_dir(app):
    with app.app_context():
        with tempfile.TemporaryDirectory() as tmpdir:
            count = scan_workspace([tmpdir])
            assert count == 0


def test_scan_with_files(app):
    with app.app_context():
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "test.txt"), "w") as f:
                f.write("hello")
            with open(os.path.join(tmpdir, "test.py"), "w") as f:
                f.write("print('hello')")
            count = scan_workspace([tmpdir])
            assert count == 2


def test_scan_skips_hidden(app):
    with app.app_context():
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, ".hidden"), "w") as f:
                f.write("hidden")
            with open(os.path.join(tmpdir, "visible.txt"), "w") as f:
                f.write("visible")
            count = scan_workspace([tmpdir])
            assert count == 1


def test_scan_skips_pycache(app):
    with app.app_context():
        with tempfile.TemporaryDirectory() as tmpdir:
            pycache = os.path.join(tmpdir, "__pycache__")
            os.makedirs(pycache)
            with open(os.path.join(pycache, "module.pyc"), "w") as f:
                f.write("compiled")
            with open(os.path.join(tmpdir, "module.py"), "w") as f:
                f.write("print('hi')")
            count = scan_workspace([tmpdir])
            assert count == 1


def test_scan_skips_uploads_and_quarantine(app):
    """uploads/ and quarantine/ directories must be excluded by default."""
    with app.app_context():
        with tempfile.TemporaryDirectory() as tmpdir:
            for subdir in ("uploads", "quarantine"):
                path = os.path.join(tmpdir, subdir)
                os.makedirs(path)
                with open(os.path.join(path, "secret.zip"), "w") as f:
                    f.write("data")
            with open(os.path.join(tmpdir, "readme.txt"), "w") as f:
                f.write("visible")
            count = scan_workspace([tmpdir])
            assert count == 1


def test_scan_skips_build_artifacts(app):
    """dist/ and build/ directories must be excluded by default."""
    with app.app_context():
        with tempfile.TemporaryDirectory() as tmpdir:
            for subdir in ("dist", "build"):
                path = os.path.join(tmpdir, subdir)
                os.makedirs(path)
                with open(os.path.join(path, "output.whl"), "w") as f:
                    f.write("binary")
            with open(os.path.join(tmpdir, "setup.py"), "w") as f:
                f.write("# setup")
            count = scan_workspace([tmpdir])
            assert count == 1


def test_scan_skips_db_and_log_files(app):
    """*.db, *.sqlite, and *.log files must be excluded by default."""
    with app.app_context():
        with tempfile.TemporaryDirectory() as tmpdir:
            for fname in ("app.db", "data.sqlite", "server.log"):
                with open(os.path.join(tmpdir, fname), "w") as f:
                    f.write("sensitive")
            with open(os.path.join(tmpdir, "readme.txt"), "w") as f:
                f.write("visible")
            count = scan_workspace([tmpdir])
            assert count == 1


def test_scan_skips_pytest_and_ruff_cache(app):
    """.pytest_cache/ and .ruff_cache/ must be excluded by default."""
    with app.app_context():
        with tempfile.TemporaryDirectory() as tmpdir:
            for subdir in (".pytest_cache", ".ruff_cache"):
                path = os.path.join(tmpdir, subdir)
                os.makedirs(path)
                with open(os.path.join(path, "cache_file"), "w") as f:
                    f.write("cache")
            with open(os.path.join(tmpdir, "source.py"), "w") as f:
                f.write("# code")
            count = scan_workspace([tmpdir])
            # .pytest_cache and .ruff_cache start with '.' so their contents
            # are excluded by the hidden-directory check
            assert count == 1


def test_scan_custom_excluded_dirs(app):
    """Custom excluded_dirs are merged with defaults."""
    with app.app_context():
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = os.path.join(tmpdir, "my_artifacts")
            os.makedirs(custom_dir)
            with open(os.path.join(custom_dir, "artifact.bin"), "w") as f:
                f.write("data")
            with open(os.path.join(tmpdir, "source.py"), "w") as f:
                f.write("# code")
            count = scan_workspace([tmpdir], excluded_dirs={"my_artifacts"})
            assert count == 1


def test_scan_custom_excluded_extensions(app):
    """Custom excluded_extensions are merged with defaults."""
    with app.app_context():
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "archive.whl"), "w") as f:
                f.write("binary")
            with open(os.path.join(tmpdir, "source.py"), "w") as f:
                f.write("# code")
            count = scan_workspace([tmpdir], excluded_extensions={"whl"})
            assert count == 1


def test_default_excluded_dirs_contains_expected(app):
    """Verify the built-in excluded dir set has the expected entries."""
    expected = {"uploads", "quarantine", "dist", "build", ".pytest_cache", ".ruff_cache"}
    assert expected.issubset(_DEFAULT_EXCLUDED_DIRS)


def test_default_excluded_extensions_contains_expected(app):
    """Verify the built-in excluded extensions set has the expected entries."""
    expected = {"db", "sqlite", "log"}
    assert expected.issubset(_DEFAULT_EXCLUDED_EXTENSIONS)


def test_cli_scan_honors_config_exclusions(app, runner):
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "skipme"))
        with open(os.path.join(tmpdir, "skipme", "inside.txt"), "w") as f:
            f.write("skip dir")
        with open(os.path.join(tmpdir, "ignore.customext"), "w") as f:
            f.write("skip ext")
        with open(os.path.join(tmpdir, "keep.py"), "w") as f:
            f.write("print('ok')")

        app.config["SCANNER_EXCLUDED_DIRS"] = {"skipme"}
        app.config["SCANNER_EXCLUDED_EXTENSIONS"] = {"customext"}
        result = runner.invoke(args=["scan", "--root", tmpdir])

        assert result.exit_code == 0
        assert "Scan complete. 1 files indexed." in result.output
        with app.app_context():
            scanned = TrackedFile.query.filter(TrackedFile.file_path.startswith(tmpdir)).all()
            assert len(scanned) == 1
            assert scanned[0].file_path.endswith("keep.py")


def test_cli_scan_honors_env_exclusions(monkeypatch):
    monkeypatch.setenv("DEVHUB_SCANNER_EXCLUDED_DIRS", "envskip")
    monkeypatch.setenv("DEVHUB_SCANNER_EXCLUDED_EXTENSIONS", ".envext")

    class EnvScannerTestingConfig(TestingConfig):
        SCANNER_EXCLUDED_DIRS = set(
            filter(
                None,
                (d.strip() for d in os.environ["DEVHUB_SCANNER_EXCLUDED_DIRS"].split(",")),
            )
        )
        SCANNER_EXCLUDED_EXTENSIONS = set(
            filter(
                None,
                (
                    e.strip().lstrip(".")
                    for e in os.environ["DEVHUB_SCANNER_EXCLUDED_EXTENSIONS"].split(",")
                ),
            )
        )

    env_app = create_app(EnvScannerTestingConfig)
    with env_app.app_context():
        db.create_all()
    runner = env_app.test_cli_runner()

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "envskip"))
            with open(os.path.join(tmpdir, "envskip", "inside.txt"), "w") as f:
                f.write("skip dir from env")
            with open(os.path.join(tmpdir, "ignore.envext"), "w") as f:
                f.write("skip ext from env")
            with open(os.path.join(tmpdir, "keep.txt"), "w") as f:
                f.write("keep")

            result = runner.invoke(args=["scan", "--root", tmpdir])

            assert result.exit_code == 0
            assert "Scan complete. 1 files indexed." in result.output
            with env_app.app_context():
                scanned = TrackedFile.query.filter(TrackedFile.file_path.startswith(tmpdir)).all()
                assert len(scanned) == 1
                assert scanned[0].file_path.endswith("keep.txt")
    finally:
        with env_app.app_context():
            db.session.remove()
            db.drop_all()
