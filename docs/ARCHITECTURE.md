# Architecture

## Overview

Workforce Dev Hub is a Flask web application built with the **app factory pattern**. It uses SQLAlchemy for persistence, Flask-Migrate/Alembic for schema migrations, Flask-Login for authentication, Flask-WTF for CSRF-protected forms, and Jinja2/Bootstrap 5 for the UI.

## Directory Structure

```
devhub/               Python package (all source code)
  __init__.py         Empty package init
  __main__.py         Entry point for python -m devhub
  app.py              App factory: create_app()
  auth.py             Login/logout blueprint
  cli.py              Flask CLI commands
  config.py           Config and TestingConfig classes
  extensions.py       Extension singletons (db, migrate, login_manager, csrf)
  models.py           SQLAlchemy models
  package_validator.py  Zip package validation
  scanner.py          Workspace file scanner
  script_runner.py    Script execution (stub, disabled by default)
  search.py           Full-text search across models
  seed.py             Seed data loader
  routes/             Flask blueprints
    admin.py          /admin/* — admin-only settings, users, audit
    api.py            /api/* — JSON API endpoints
    docs.py           /docs/* — document CRUD
    main.py           / — dashboard, search, files, health
    packages.py       /packages/* — package upload, validation, approval
    progress.py       /progress/* — progress entry CRUD and report
    projects.py       /projects/* — project CRUD
    scripts.py        /scripts/* — script library CRUD
  templates/          Jinja2 templates (organized by blueprint)
  static/             CSS and JS assets
migrations/           Alembic migrations (committed to git)
tests/                Pytest test suite
docs/                 Project documentation
sample_packages/      Example package zip files
wsgi.py               WSGI entry point
```

## App Factory

`create_app(config_class=Config)` in `devhub/app.py`:

1. Creates the Flask app instance
2. Loads configuration from `config_class`
3. Initializes all extensions (`db`, `migrate`, `login_manager`, `csrf`)
4. Registers all blueprints
5. Sets up `@login_manager.user_loader`

This pattern allows multiple app instances with different configurations (e.g., TestingConfig for tests).

## Blueprint Structure

| Blueprint | Prefix | Purpose |
|-----------|--------|---------|
| `main` | `/` | Dashboard, search page, file index, health check |
| `auth` | `/auth` | Login, logout |
| `projects` | `/projects` | Project CRUD |
| `docs` | `/docs` | Document CRUD |
| `progress` | `/progress` | Progress entry CRUD and report |
| `scripts` | `/scripts` | Script library CRUD |
| `packages` | `/packages` | Package upload, validation, approval, install |
| `admin` | `/admin` | Admin settings, user management, audit log |
| `api` | `/api` | JSON API for all resource types |

## Data Model

### Core Models

```
User              — Auth users with admin flag
Project           — Top-level groupings for all work
Document          — Markdown/text documents per project
ProgressEntry     — Time-stamped progress notes per project
Script            — Script catalog entries
ScriptRunLog      — Immutable log of script executions
Package           — Uploaded zip packages with quarantine workflow
TrackedFile       — Workspace files indexed by scanner
AuditLog          — Admin action audit trail
Tag               — Many-to-many labels for Projects/Documents/Scripts
```

### Relationships

```
Project 1──* Document
Project 1──* ProgressEntry
Project *──* Tag   (project_tags association table)
Script *──* Tag    (script_tags association table)
Document *──* Tag  (document_tags association table)
Script 1──* ScriptRunLog
User 1──* ScriptRunLog  (ran_by_user_id)
User 1──* Package       (uploaded_by_user_id)
User 1──* AuditLog      (user_id)
```

## Configuration Hierarchy

```
Config (base)
  SQLALCHEMY_DATABASE_URI = sqlite:///devhub.db
  WTF_CSRF_ENABLED = True
  DEVHUB_ENABLE_SCRIPT_EXECUTION = False
  DEVHUB_ENABLE_PACKAGE_INSTALL = False
  ...

TestingConfig(Config)
  SQLALCHEMY_DATABASE_URI = sqlite:///:memory:
  TESTING = True
  WTF_CSRF_ENABLED = False
  SERVER_NAME = localhost
```

All config values can be overridden with environment variables (see `.env.example`).

## Request Flow

```
Browser → Flask (wsgi.py) → create_app → Blueprint route
  → login_required (if needed)
  → admin_required (if admin-only)
  → business logic (models, search, scanner, validator)
  → Jinja2 template render (or JSON response for /api/*)
  → Bootstrap 5 UI in browser
```

## Extension Singletons

All extensions are instantiated in `devhub/extensions.py` without an app instance, then initialized in `create_app()` using `init_app(app)`. This avoids circular imports.

```python
# extensions.py
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
```

## Test Architecture

Tests use:
- `pytest-flask` with a session-scoped app fixture using `TestingConfig`
- In-memory SQLite (`sqlite:///:memory:`) — clean, fast, no disk state
- CSRF disabled in tests — form POSTs work without tokens
- Admin user fixture creates `testadmin@example.com` / `testpass123`
- Authentication in tests uses `client.session_transaction()` to set `_user_id` directly
