import os
import hashlib
from datetime import datetime
from devhub.extensions import db
from devhub.models import FileRecord

class FileScanner:
    DEFAULT_EXCLUDE_DIRS = {
        'venv', 'env', '.venv', '.env', 'node_modules', '__pycache__',
        'dist', 'build', '.git', '.tox', '.mypy_cache', '.pytest_cache',
        'uploads', 'migrations',
    }
    DEFAULT_EXCLUDE_EXTENSIONS = {'.db', '.sqlite', '.sqlite3', '.pyc'}
    DEFAULT_EXCLUDE_FILENAMES = {'.env'}

    def compute_hash(self, filepath):
        h = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    h.update(chunk)
            return h.hexdigest()
        except (OSError, IOError):
            return None

    def scan_directory(self, path, exclude_dirs=None, exclude_extensions=None,
                       exclude_filenames=None):
        if exclude_dirs is None:
            exclude_dirs = self.DEFAULT_EXCLUDE_DIRS
        if exclude_extensions is None:
            exclude_extensions = self.DEFAULT_EXCLUDE_EXTENSIONS
        if exclude_filenames is None:
            exclude_filenames = self.DEFAULT_EXCLUDE_FILENAMES

        records = []
        for root, dirs, files in os.walk(path):
            dirs[:] = [
                d for d in dirs
                if not d.startswith('.') and d not in exclude_dirs
            ]
            for fname in files:
                if fname.startswith('.'):
                    continue
                if fname in exclude_filenames:
                    continue
                _, ext = os.path.splitext(fname)
                if ext in exclude_extensions:
                    continue
                fpath = os.path.join(root, fname)
                try:
                    size = os.path.getsize(fpath)
                    fhash = self.compute_hash(fpath)
                    records.append({
                        'filepath': fpath,
                        'filename': fname,
                        'file_hash': fhash,
                        'size_bytes': size,
                        'last_scanned': datetime.utcnow(),
                        'scan_status': 'ok',
                    })
                except (OSError, IOError):
                    continue
        return records

    def update_database(self, records):
        for rec in records:
            existing = FileRecord.query.filter_by(filepath=rec['filepath']).first()
            if existing:
                existing.file_hash = rec['file_hash']
                existing.size_bytes = rec['size_bytes']
                existing.last_scanned = rec['last_scanned']
                existing.scan_status = rec['scan_status']
            else:
                fr = FileRecord(**rec)
                db.session.add(fr)
        db.session.commit()
