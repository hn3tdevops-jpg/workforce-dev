# PythonAnywhere Deployment Guide

## Prerequisites

- A PythonAnywhere account (free tier works for SQLite)
- Your code pushed to a Git repository

## Steps

### 1. Upload Code

Open a PythonAnywhere Bash console:

```bash
git clone <your-repo-url> ~/workforce-dev
cd ~/workforce-dev
```

### 2. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
nano .env
```

Set at minimum:
- `SECRET_KEY` – a long random string
- `DATABASE_URL` – e.g. `sqlite:////home/<user>/workforce-dev/instance/devhub.db`

### 4. Initialize Database

```bash
flask --app wsgi:app init-db
flask --app wsgi:app seed
```

### 5. Configure WSGI

In the PythonAnywhere Web tab, set:
- **Source code:** `/home/<user>/workforce-dev`
- **Working directory:** `/home/<user>/workforce-dev`
- **WSGI configuration file:** Edit to contain:

```python
import sys
import os

sys.path.insert(0, '/home/<user>/workforce-dev')
os.environ['SECRET_KEY'] = 'your-secret-key'
os.environ['DATABASE_URL'] = 'sqlite:////home/<user>/workforce-dev/instance/devhub.db'

from wsgi import app as application
```

### 6. Set Virtualenv

In the Web tab, set the virtualenv path to `/home/<user>/workforce-dev/venv`.

### 7. Reload

Click "Reload" in the Web tab. Your app is live.

## Updates

```bash
cd ~/workforce-dev
git pull
source venv/bin/activate
pip install -r requirements.txt
flask --app wsgi:app db upgrade  # run migrations
# Reload via Web tab
```
