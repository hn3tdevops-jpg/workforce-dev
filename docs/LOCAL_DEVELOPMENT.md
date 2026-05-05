# Local Development Setup

## Prerequisites

- Python 3.11+
- Git

## Setup

```bash
# Clone the repository
git clone <repo-url>
cd workforce-dev

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env and set SECRET_KEY at minimum

# Initialize the database
flask --app wsgi:app init-db

# Seed with demo data (creates admin user admin/admin123)
flask --app wsgi:app seed

# Run the development server
flask --app wsgi:app run
```

The app will be available at http://127.0.0.1:5000

## CLI Commands

```bash
flask --app wsgi:app init-db              # Create database tables
flask --app wsgi:app seed                 # Seed demo data
flask --app wsgi:app create-admin         # Create an admin user interactively
flask --app wsgi:app scan                 # Scan DEVHUB_WORKSPACE_ROOTS
flask --app wsgi:app validate-package <path>  # Validate a .zip package
```

## Running Tests

```bash
pytest tests/ -v
```

## Linting

```bash
ruff check workforce_devhub/
```

## Feature Flags

Set in `.env`:

```
DEVHUB_ENABLE_SCRIPT_EXECUTION=false
DEVHUB_ENABLE_PACKAGE_INSTALL=false
DEVHUB_WORKSPACE_ROOTS=/path/to/project1:/path/to/project2
```
