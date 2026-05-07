import os
import tempfile

from devhub.scanner import scan_workspace


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
