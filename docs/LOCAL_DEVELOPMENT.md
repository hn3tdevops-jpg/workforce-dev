# Local Development Guide

## Prerequisites

- Python 3.11+
- Git

## Quick Start

```bash
# Clone the repo
git clone https://github.com/hn3tdevops-jpg/workforce-dev.git
cd workforce-dev

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy the example env file and configure
cp .env.example .env
# Edit .env with your preferred values

# Apply existing migrations (do NOT run flask db init on a cloned repo — migrations already exist)
FLASK_APP=wsgi.py flask db upgrade

# Create an admin user
FLASK_APP=wsgi.py flask create-admin

# Optionally load seed data
FLASK_APP=wsgi.py flask seed

# Run the development server
FLASK_APP=wsgi.py flask run
```

The app will be available at http://localhost:5000.

## Running Tests

```bash
pytest tests/ -v
```

## Linting

```bash
ruff check devhub/ tests/
ruff format devhub/ tests/
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DEVHUB_SECRET_KEY` | `dev-secret-change-me` | Flask secret key |
| `DEVHUB_DATABASE_URL` | `sqlite:///devhub.db` | SQLAlchemy database URL |
| `DEVHUB_UPLOAD_DIR` | `uploads` | Upload directory |
| `DEVHUB_QUARANTINE_DIR` | `quarantine` | Package quarantine directory |
| `DEVHUB_ENABLE_SCRIPT_EXECUTION` | `false` | Enable script execution |
| `DEVHUB_ENABLE_PACKAGE_INSTALL` | `false` | Enable package installation |
| `DEVHUB_WORKSPACE_ROOTS` | `` | Comma-separated workspace roots to scan |
| `DEVHUB_ADMIN_EMAIL` | `admin@example.com` | Default admin email |

## Flask CLI Commands

```bash
flask init-db           # Initialize database tables
flask seed              # Load seed data
flask create-admin      # Create an admin user (interactive)
flask scan --root /path # Scan a workspace root and index files
flask validate-package path/to/pkg.zip  # Validate a package zip
flask db migrate -m "message"  # Create a new migration
flask db upgrade        # Apply pending migrations
```

## Project Structure

```
devhub/           Python package (app source)
  routes/         Flask blueprints
  templates/      Jinja2 templates
  static/         CSS and JS assets
tests/            Pytest test suite
docs/             Project documentation
migrations/       Alembic migrations (committed to git)
sample_packages/  Example package zip files
wsgi.py           WSGI entry point
```
