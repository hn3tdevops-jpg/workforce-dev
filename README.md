# Workforce Developer Hub

A GitHub-first, PythonAnywhere-ready internal developer hub for the Workforce project. It centralizes docs, progress reports, project dashboards, script catalogs, package validation, file tracking, full-text search, and admin tooling for managing the full Workforce development lifecycle.

## Features

- **Project Dashboard** — Track multiple projects with status and tags
- **Documents** — Per-project markdown/text documents
- **Progress Log** — Time-stamped progress entries with weekly reports
- **Script Library** — Catalog of automation scripts (execution disabled by default)
- **Package Manager** — Upload, validate, and quarantine zip packages
- **File Tracker** — Index and track workspace files with SHA256 hashes
- **Search** — Full-text search across all resources
- **Admin Panel** — User management, settings, audit log
- **JSON API** — REST endpoints for all resource types

## Quick Start

```bash
git clone https://github.com/hn3tdevops-jpg/workforce-dev.git
cd workforce-dev
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
FLASK_APP=wsgi.py flask db init
FLASK_APP=wsgi.py flask db migrate -m "initial"
FLASK_APP=wsgi.py flask db upgrade
FLASK_APP=wsgi.py flask seed
FLASK_APP=wsgi.py flask run
```

Open http://localhost:5000. Create an admin user with `FLASK_APP=wsgi.py flask create-admin`.

## Running Tests

```bash
pytest tests/ -v
```

## Tech Stack

- **Flask 3** with app factory pattern
- **SQLAlchemy 2** + **Flask-Migrate** (Alembic) for migrations
- **Flask-Login** + **Flask-WTF** (CSRF protection)
- **Bootstrap 5** (CDN) + Bootstrap Icons
- **Pytest** + **pytest-flask** for testing
- **Ruff** for linting

## Project Structure

```
devhub/        Application source (models, routes, templates, static)
migrations/    Alembic database migrations
tests/         Pytest test suite
docs/          Project documentation
sample_packages/ Example package zip files
wsgi.py        WSGI entry point
```

## Documentation

- [Local Development](docs/LOCAL_DEVELOPMENT.md)
- [PythonAnywhere Deployment](docs/PYTHONANYWHERE_DEPLOYMENT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Security Model](docs/SECURITY_MODEL.md)
- [Package Manifest Spec](docs/PACKAGE_MANIFEST_SPEC.md)
- [Script Library Spec](docs/SCRIPT_LIBRARY_SPEC.md)

## Security Notes

Script execution and package installation are **disabled by default**. See [SECURITY_MODEL.md](docs/SECURITY_MODEL.md) for details.

## Required Environment Variables

| Variable | Required in Production | Default (dev) | Description |
|---|---|---|---|
| `DEVHUB_SECRET_KEY` | **Yes** | `dev-secret-change-me` | Flask session signing key. **Must** be a long random string in production. |
| `DEVHUB_DATABASE_URL` | Recommended | `sqlite:///devhub.db` | SQLAlchemy database URL. Use an absolute path for PythonAnywhere. |
| `DEVHUB_ADMIN_EMAIL` | Yes | `admin@example.com` | Email for the initial admin account. |
| `DEVHUB_ADMIN_PASSWORD` | Yes | *(empty)* | Password for the initial admin account. Set before running `flask create-admin`. |
| `DEVHUB_UPLOAD_DIR` | No | `uploads` | Directory for file uploads. |
| `DEVHUB_QUARANTINE_DIR` | No | `quarantine` | Directory for quarantined packages. |
| `DEVHUB_ENABLE_SCRIPT_EXECUTION` | No | `false` | Set to `true` to enable script execution (advanced). |
| `DEVHUB_ENABLE_PACKAGE_INSTALL` | No | `false` | Set to `true` to enable package installation (advanced). |
| `DEVHUB_WORKSPACE_ROOTS` | No | *(empty)* | Comma-separated list of workspace root directories to scan. |
| `DEVHUB_SCANNER_EXCLUDED_DIRS` | No | see config.py | Comma-separated dir names to exclude from workspace scan. |
| `DEVHUB_SCANNER_EXCLUDED_EXTENSIONS` | No | `.db,.sqlite,.log,.env` | Comma-separated file extensions to exclude from workspace scan. |
| `DEVHUB_ENV` | No | *(not set)* | Set to `production` to activate production safety checks (e.g. rejects placeholder `DEVHUB_SECRET_KEY`). |

### Production Config

Use `ProductionConfig` (from `devhub.config`) or set `DEVHUB_ENV=production` to activate startup validation. The app will refuse to start if `DEVHUB_SECRET_KEY` is missing or uses the placeholder value.
