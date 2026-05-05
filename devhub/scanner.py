import datetime
import hashlib
import os

from devhub.extensions import db
from devhub.models import TrackedFile

# Default excluded directories (merged with any app-config overrides at call time).
_DEFAULT_EXCLUDED_DIRS = frozenset(
    {
        ".git",
        "__pycache__",
        "node_modules",
        "venv",
        ".venv",
        "uploads",
        "quarantine",
        "dist",
        "build",
        ".pytest_cache",
        ".ruff_cache",
        "instance",
    }
)

# Default excluded file extensions (without leading dot).
_DEFAULT_EXCLUDED_EXTENSIONS = frozenset({"db", "sqlite", "log", "env"})


def hash_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, IOError):
        return None


def scan_workspace(roots, excluded_dirs=None, excluded_extensions=None):
    """Scan workspace roots and index files. Returns count of files indexed.

    Args:
        roots: Iterable of directory paths to scan.
        excluded_dirs: Optional set of directory names to skip.  Merges with
            the built-in defaults.  Pass an empty set to use *only* built-ins.
        excluded_extensions: Optional set of file extensions (without leading
            dot) to skip.  Merges with the built-in defaults.
    """
    skip_dirs = _DEFAULT_EXCLUDED_DIRS.union(excluded_dirs or set())
    skip_exts = _DEFAULT_EXCLUDED_EXTENSIONS.union(excluded_extensions or set())

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
                and d not in skip_dirs
            ]
            for filename in filenames:
                if filename.startswith("."):
                    continue
                ext = os.path.splitext(filename)[1].lstrip(".").lower() or "unknown"
                if ext in skip_exts:
                    continue
                filepath = os.path.join(dirpath, filename)
                try:
                    stat = os.stat(filepath)
                    last_modified = datetime.datetime.fromtimestamp(stat.st_mtime)
                    size = stat.st_size
                    sha256 = hash_file(filepath)

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
