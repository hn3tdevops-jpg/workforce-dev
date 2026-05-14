# Workspace Scan Configuration Guide

## Overview

This guide explains how to configure and run scan scripts in the Workforce Dev Hub. The scan functionality indexes workspace files for tracking and monitoring.

---

## 📋 Configuration Guide

### Step 1: Copy the Environment File

```bash
cp .env.example .env
```

### Step 2: Configure `DEVHUB_WORKSPACE_ROOTS` in `.env`

Edit your `.env` file and set the `DEVHUB_WORKSPACE_ROOTS` variable. This is a **comma-separated list** of directories to scan.

#### Example Configurations

**Option A: Single directory (e.g., your main project)**
```dotenv
DEVHUB_WORKSPACE_ROOTS=/home/user/workforce-api
```

**Option B: Multiple directories**
```dotenv
DEVHUB_WORKSPACE_ROOTS=/home/user/workforce-api,/home/user/frontend-console,/home/user/workforce-dev
```

**Option C: Relative paths from project root**
```dotenv
DEVHUB_WORKSPACE_ROOTS=.,../other-project
```

**Option D: Production deployment paths**
```dotenv
DEVHUB_WORKSPACE_ROOTS=/var/www/workforce-api,/var/www/frontend,/opt/deployment/workspace
```

### Step 3: Other Important Configuration

While you're editing `.env`, also set these:

```dotenv
DEVHUB_SECRET_KEY=your-unique-secret-key-here-change-this
DEVHUB_ADMIN_EMAIL=your-admin-email@example.com
DEVHUB_ADMIN_PASSWORD=strong-password-here
DEVHUB_DATABASE_URL=sqlite:///devhub.db
FLASK_APP=wsgi.py
FLASK_ENV=development
```

---

## 🔧 Running Scans

### Method 1: Use Pre-configured Roots (Recommended)

After setting `DEVHUB_WORKSPACE_ROOTS` in `.env`:

```bash
FLASK_APP=wsgi.py flask scan
```

This will scan all directories listed in your `.env` file.

### Method 2: Override with Command-Line Arguments

```bash
FLASK_APP=wsgi.py flask scan --root /path/to/dir1 --root /path/to/dir2
```

You can specify multiple `--root` options. These are added to (not replace) the configured roots.

### Method 3: Python Module Entry Point

```bash
python -m devhub scan --root /path/to/workspace
```

---

## 📊 How Scanning Works

From the code (`devhub/scanner.py`):

1. **Automatically skips**:
   - Hidden directories (starting with `.`)
   - `__pycache__`, `node_modules`, `.git`, `venv`, `.venv`

2. **Indexes all visible files** with:
   - File path
   - File type (extension)
   - Size and modification date
   - SHA256 hash (for integrity tracking)

3. **Stores results** in the database (`tracked_files` table)

---

## 📈 Viewing Scan Results

After running a scan:

1. **Web UI**: Navigate to `http://localhost:5000/files`
2. **Database**: Query `tracked_files` table
3. **CLI feedback**: The command outputs the count of indexed files

---

## ⚙️ Complete `.env` Example for Development

```dotenv
DEVHUB_SECRET_KEY=my-development-secret-key-12345
DEVHUB_ADMIN_EMAIL=admin@workforce.local
DEVHUB_ADMIN_PASSWORD=dev-password-123
DEVHUB_DATABASE_URL=sqlite:///devhub.db
DEVHUB_UPLOAD_DIR=uploads
DEVHUB_QUARANTINE_DIR=quarantine
DEVHUB_ENABLE_SCRIPT_EXECUTION=false
DEVHUB_ENABLE_PACKAGE_INSTALL=false
DEVHUB_WORKSPACE_ROOTS=/home/user/workforce-api,/home/user/workforce-frontend,/home/user/workforce-dev
FLASK_APP=wsgi.py
FLASK_ENV=development
```

---

## 🚀 Quick Start Checklist

- [ ] Copy `.env.example` → `.env`
- [ ] Set `DEVHUB_WORKSPACE_ROOTS` to your target directories
- [ ] Set `DEVHUB_SECRET_KEY` to a unique value
- [ ] Run `FLASK_APP=wsgi.py flask init-db` (first time only)
- [ ] Run `FLASK_APP=wsgi.py flask create-admin` (first time only)
- [ ] Run `FLASK_APP=wsgi.py flask scan` to index files
- [ ] Start the app: `FLASK_APP=wsgi.py flask run`
- [ ] Visit `http://localhost:5000/files` to view results

---

## 📚 Related Documentation

- [Local Development Guide](LOCAL_DEVELOPMENT.md)
- [Architecture Overview](ARCHITECTURE.md)

## Additional Directory Recommendations

The **`scan`** command is designed to index workspace files. You should run scans on:

1. **Application directories** (main source code):
   - `devhub/` — Your main application package
   - `tests/` — Your test suite
   - `migrations/` — Database migration files

2. **Project root or specific workspace roots** — The scan command accepts custom roots via the `--root` flag or `DEVHUB_WORKSPACE_ROOTS` environment variable.

3. **Directories automatically excluded** (filtered by scanner):
   - `__pycache__` — Python cache files
   - `node_modules` — Node dependencies (if applicable)
   - `.git` — Git internals
   - `venv` / `.venv` — Virtual environments
   - Directories starting with `.` (hidden directories)
