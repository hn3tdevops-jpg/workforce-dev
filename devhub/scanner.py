import datetime
import hashlib
import os

from devhub.extensions import db
from devhub.models import TrackedFile


def hash_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, IOError):
        return None


def scan_workspace(roots):
    """Scan workspace roots and index files. Returns count of files indexed."""
    count = 0
    for root in roots:
        root = os.path.abspath(root)
        if not os.path.exists(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [
                d
                for d in dirnames
                if not d.startswith(".")
                and d not in ("__pycache__", "node_modules", ".git", "venv", ".venv")
            ]
            for filename in filenames:
                if filename.startswith("."):
                    continue
                filepath = os.path.join(dirpath, filename)
                try:
                    stat = os.stat(filepath)
                    last_modified = datetime.datetime.fromtimestamp(stat.st_mtime)
                    size = stat.st_size
                    sha256 = hash_file(filepath)
                    ext = os.path.splitext(filename)[1].lstrip(".").lower() or "unknown"

                    existing = TrackedFile.query.filter_by(file_path=filepath).first()
                    if existing:
                        existing.last_modified = last_modified
                        existing.size_bytes = size
                        existing.sha256_hash = sha256
                        existing.last_scanned = datetime.datetime.utcnow()
                        existing.status = "present"
                        existing.file_type = ext
                    else:
                        tf = TrackedFile(
                            file_path=filepath,
                            file_type=ext,
                            last_modified=last_modified,
                            sha256_hash=sha256,
                            size_bytes=size,
                            status="present",
                            last_scanned=datetime.datetime.utcnow(),
                        )
                        db.session.add(tf)
                    count += 1
                except (OSError, IOError):
                    pass
    db.session.commit()
    return count
