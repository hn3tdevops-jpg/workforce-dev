# Workforce Developer Hub

A Flask-based internal developer hub for managing projects, documentation, progress tracking, scripts, packages, and file tracking across the workforce engineering team.

## Features

- **Project Dashboards** – Health cards, status, recent progress and docs for 6 projects
- **Documents Library** – Browse, search, upload, and manage docs with status lifecycle (draft → canonical → stale → archived)
- **Progress Tracking** – Create entries with evidence links, commands run, test results, and notes; generate reports
- **Script Library** – Catalog scripts with risk levels, dry-run and run commands, and run logs
- **Package Upload** – Secure .zip upload with manifest validation, quarantine, and admin approval
- **File Tracker** – Scan workspace roots and track files with checksums
- **Full-text Search** – Across docs, progress, scripts, packages, and files
- **Admin Panel** – User management, project management, feature flags, audit log
- **JSON API** – `/api/health`, `/api/status`, `/api/projects`, `/api/search`

## Quick Start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask --app wsgi:app init-db
flask --app wsgi:app seed
flask --app wsgi:app run
```

Default admin: `admin` / `admin123`

## Documentation

- [Local Development](LOCAL_DEVELOPMENT.md)
- [PythonAnywhere Deployment](PYTHONANYWHERE_DEPLOYMENT.md)
- [Security Model](SECURITY_MODEL.md)

## Stack

- Python 3.11+ / Flask / SQLAlchemy / Flask-Migrate
- Flask-Login / Flask-WTF / Werkzeug
- SQLite (dev) / Jinja2 + Bootstrap 5 + HTMX
- Pytest / Ruff
