import os
import tempfile

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

