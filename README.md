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
FLASK_APP=wsgi.py flask db upgrade
FLASK_APP=wsgi.py flask seed
FLASK_APP=wsgi.py flask run
```

Open http://localhost:5000. Create an admin user with `FLASK_APP=wsgi.py flask create-admin`.

## UI Overview

The DevHub UI is built with **Bootstrap 5**, **Bootstrap Icons**, and minimal vanilla JavaScript.
There is no npm/Vite/Node build step — all assets are either served from Flask's `static/` folder or
loaded from CDN. This makes the app fully compatible with PythonAnywhere.

### Login screen (`/login`)

A standalone centered login card with:
- Workforce Developer Hub branding and subtitle
- Email, password, and Remember Me fields
- Submit button with loading/disabled state during submission
- Friendly flash message styling for invalid credentials
- "Authorized users only" security note

### App shell (authenticated pages)

- **Topbar** — Dark branded navbar with active-link highlighting for all sections,
  user email dropdown with admin badge, Sign Out link
- **Flash messages** — Categorised Bootstrap alerts with icons and auto-dismiss (5 s)
- **Footer** — Links to `/health` and `/api/status`

### Dashboard (`/`)

- **Stats row** — Six clickable summary cards showing live counts for
  Projects, Docs, Progress entries, Scripts, Packages, and Tracked Files
- **Active projects** — Cards for every active project
- **Recent activity** — Progress entries, docs, packages, files
- **Quick actions** — Log Progress, New Doc, Upload Package (authenticated users)

### Resource pages

Docs, Progress, Scripts, Packages, and Projects pages all feature:
- Filter / search forms
- Status badges (`draft`, `canonical`, `stale`, `archived`, `quarantined`, `approved`, etc.)
- Risk-level badges (safe / moderate / dangerous)
- Empty-state messages with action links

## How to Run Locally

```bash
source .venv/bin/activate
FLASK_APP=wsgi.py flask run
```

## Running Tests

```bash
pytest tests/ -v
```

### Testing UI Changes

The `tests/test_ui.py` suite covers:
- Login page renders with branding, subtitle, security note
- Login accepts valid credentials and rejects invalid ones
- Dashboard renders for anonymous and authenticated users
- Dashboard shows stats cards and quick-action buttons
- Primary nav links are present
- Package approve/install admin-only controls are unaffected

Run the full suite before and after UI changes:

```bash
pytest tests/ -v
```

Lint Python with:

```bash
ruff check devhub/
```

## Tech Stack

- **Flask 3** with app factory pattern
- **SQLAlchemy 2** + **Flask-Migrate** (Alembic) for migrations
- **Flask-Login** + **Flask-WTF** (CSRF protection)
- **Bootstrap 5** (CDN) + Bootstrap Icons (CDN)
- **Vanilla JavaScript** — no npm/Vite/React required
- **Pytest** + **pytest-flask** for testing
- **Ruff** for linting
- **PythonAnywhere**-compatible (no build step)

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
