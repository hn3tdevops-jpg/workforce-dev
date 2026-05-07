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

## UI Overview

- Bootstrap 5 + Jinja app shell with responsive topbar, sidebar/offcanvas navigation, and reusable page-header components.
- Standalone branded `/login` experience with keyboard-friendly controls, CSRF-safe Flask-WTF form handling, and submit loading states.
- Interactive dashboard cards for docs, packages, progress, scripts, tracked files, and project health.
- Lightweight vanilla JS enhancements (form loading states, copy-to-clipboard, safe confirm dialogs, search clear button) with no npm/Vite/React build pipeline.
- PythonAnywhere-friendly server-rendered architecture remains unchanged.

## Quick Start

```bash
git clone https://github.com/hn3tdevops-jpg/workforce-dev.git
cd workforce-dev
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
FLASK_APP=wsgi.py flask db upgrade
FLASK_APP=wsgi.py flask seed
FLASK_APP=wsgi.py flask run
```

Open http://localhost:5000. Create an admin user with `FLASK_APP=wsgi.py flask create-admin`.

## Running Tests

```bash
pytest tests/ -v
```

```bash
ruff check devhub/
```

For UI-focused verification:

1. Log in at `/login` (admin + non-admin accounts).
2. Validate responsive navigation (desktop sidebar + mobile offcanvas).
3. Confirm package approve/install controls remain admin-gated and feature-flag controlled.
4. Run the full test and lint commands above before merge.

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
