import os

_PLACEHOLDER_KEY = "dev-secret-change-me"


class Config:
    SECRET_KEY = os.environ.get("DEVHUB_SECRET_KEY", _PLACEHOLDER_KEY)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEVHUB_DATABASE_URL", "sqlite:///devhub.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_DIR = os.environ.get("DEVHUB_UPLOAD_DIR", "uploads")
    QUARANTINE_DIR = os.environ.get("DEVHUB_QUARANTINE_DIR", "quarantine")
    ENABLE_SCRIPT_EXECUTION = os.environ.get("DEVHUB_ENABLE_SCRIPT_EXECUTION", "false").lower() == "true"
    ENABLE_PACKAGE_INSTALL = os.environ.get("DEVHUB_ENABLE_PACKAGE_INSTALL", "false").lower() == "true"
    WORKSPACE_ROOTS = [r.strip() for r in os.environ.get("DEVHUB_WORKSPACE_ROOTS", "").split(",") if r.strip()]
    ADMIN_EMAIL = os.environ.get("DEVHUB_ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD = os.environ.get("DEVHUB_ADMIN_PASSWORD", "")
    WTF_CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB upload limit
    VERSION = "1.0.0"
    # Directories and file extensions excluded from workspace scanning.
    # Override via subclass or DEVHUB_SCANNER_EXCLUDED_DIRS / DEVHUB_SCANNER_EXCLUDED_EXTENSIONS.
    SCANNER_EXCLUDED_DIRS = set(
        filter(
            None,
            (
                d.strip()
                for d in os.environ.get(
                    "DEVHUB_SCANNER_EXCLUDED_DIRS",
                    ".git,__pycache__,node_modules,venv,.venv,uploads,quarantine,dist,build,"
                    ".pytest_cache,.ruff_cache,instance,*.egg-info",
                ).split(",")
            ),
        )
    )
    SCANNER_EXCLUDED_EXTENSIONS = set(
        filter(
            None,
            (
                e.strip().lstrip(".")
                for e in os.environ.get(
                    "DEVHUB_SCANNER_EXCLUDED_EXTENSIONS",
                    ".db,.sqlite,.log,.env",
                ).split(",")
            ),
        )
    )


class ProductionConfig(Config):
    """Configuration for production deployments.

    Requires DEVHUB_SECRET_KEY to be set to a non-placeholder value.
    Use this config class (or set DEVHUB_ENV=production) when deploying
    to PythonAnywhere or any public-facing server.
    """

    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    ENABLE_SCRIPT_EXECUTION = False
    ENABLE_PACKAGE_INSTALL = False
