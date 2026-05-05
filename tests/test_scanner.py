import os
import pytest
from devhub.scanner import FileScanner

def test_compute_hash_existing_file(tmp_path):
    f = tmp_path / 'test.txt'
    f.write_text('hello world')
    scanner = FileScanner()
    h = scanner.compute_hash(str(f))
    assert h is not None
    assert len(h) == 64

def test_compute_hash_missing_file():
    scanner = FileScanner()
    h = scanner.compute_hash('/nonexistent/path/file.txt')
    assert h is None

def test_scan_directory(tmp_path):
    (tmp_path / 'a.txt').write_text('aaa')
    (tmp_path / 'b.txt').write_text('bbb')
    sub = tmp_path / 'sub'
    sub.mkdir()
    (sub / 'c.txt').write_text('ccc')
    scanner = FileScanner()
    records = scanner.scan_directory(str(tmp_path))
    filenames = [r['filename'] for r in records]
    assert 'a.txt' in filenames
    assert 'b.txt' in filenames
    assert 'c.txt' in filenames

def test_scan_directory_skips_hidden(tmp_path):
    (tmp_path / '.hidden').write_text('hidden')
    (tmp_path / 'visible.txt').write_text('visible')
    scanner = FileScanner()
    records = scanner.scan_directory(str(tmp_path))
    filenames = [r['filename'] for r in records]
    assert '.hidden' not in filenames
    assert 'visible.txt' in filenames

def test_update_database(app, db, tmp_path):
    with app.app_context():
        f = tmp_path / 'scan.txt'
        f.write_text('data')
        scanner = FileScanner()
        records = scanner.scan_directory(str(tmp_path))
        scanner.update_database(records)
        from devhub.models import FileRecord
        fr = FileRecord.query.filter_by(filename='scan.txt').first()
        assert fr is not None
        assert fr.scan_status == 'ok'

def test_update_database_updates_existing(app, db, tmp_path):
    with app.app_context():
        f = tmp_path / 'upd.txt'
        f.write_text('v1')
        scanner = FileScanner()
        records = scanner.scan_directory(str(tmp_path))
        scanner.update_database(records)
        f.write_text('v2')
        records2 = scanner.scan_directory(str(tmp_path))
        scanner.update_database(records2)
        from devhub.models import FileRecord
        fr = FileRecord.query.filter_by(filename='upd.txt').first()
        assert fr.size_bytes == 2
