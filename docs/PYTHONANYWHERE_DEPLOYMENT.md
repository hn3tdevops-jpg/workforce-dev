# PythonAnywhere Deployment Guide

## Overview

This guide explains how to deploy the Workforce Dev Hub to PythonAnywhere from the GitHub repository.

## Prerequisites

- PythonAnywhere account (free or paid)
- The GitHub repository cloned to PythonAnywhere

## Step-by-Step Deployment

### 1. Open a PythonAnywhere Bash Console

Log in to PythonAnywhere and open a Bash console.

### 2. Clone the Repository

```bash
cd ~
git clone https://github.com/hn3tdevops-jpg/workforce-dev.git workforce-dev
cd workforce-dev
```

### 3. Create a Virtual Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file (never commit this):

```bash
cp .env.example .env
nano .env
```

At minimum, set:
- `DEVHUB_SECRET_KEY` — a long random string
- `DEVHUB_DATABASE_URL` — e.g. `sqlite:////home/yourusername/workforce-dev/devhub.db`
- `DEVHUB_ADMIN_EMAIL`
- `DEVHUB_ADMIN_PASSWORD`

### 5. Initialize the Database

```bash
FLASK_APP=wsgi.py flask db upgrade
FLASK_APP=wsgi.py flask seed
FLASK_APP=wsgi.py flask create-admin
```

### 6. Configure the Web App in PythonAnywhere Dashboard

1. Go to **Web** tab → **Add a new web app**
2. Choose **Manual configuration** → **Python 3.11**
3. Set the **Source code** directory to `/home/yourusername/workforce-dev`
4. Set the **Virtualenv** to `/home/yourusername/workforce-dev/.venv`
5. Edit the **WSGI configuration file** to point to the app:

```python
import sys
import os

path = '/home/yourusername/workforce-dev'
if path not in sys.path:
    sys.path.insert(0, path)

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

from wsgi import app as application
```

### 7. Set Environment Variables in WSGI Config

You can also set environment variables directly in the PythonAnywhere WSGI config file using `os.environ`:

```python
os.environ['DEVHUB_SECRET_KEY'] = 'your-secret-key'
os.environ['DEVHUB_DATABASE_URL'] = 'sqlite:////home/yourusername/workforce-dev/devhub.db'
```

### 8. Static Files

Configure static files in the PythonAnywhere Web tab:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/workforce-dev/devhub/static/` |

### 9. Reload the Web App

Click **Reload** in the PythonAnywhere Web tab.

## Updating the Deployment

```bash
cd ~/workforce-dev
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
FLASK_APP=wsgi.py flask db upgrade
```

Then reload the web app in PythonAnywhere.

## Troubleshooting

- **500 errors**: Check the PythonAnywhere error log in the Web tab
- **Database errors**: Ensure the database path is absolute in `DEVHUB_DATABASE_URL`
- **Static files not loading**: Verify the static files URL mapping in the Web tab
- **Import errors**: Ensure the virtual environment is active and all dependencies are installed

## Security Notes

- Always use a strong, random `DEVHUB_SECRET_KEY`
- Keep `DEVHUB_ENABLE_SCRIPT_EXECUTION=false` and `DEVHUB_ENABLE_PACKAGE_INSTALL=false` unless you explicitly need them
- The `.env` file should never be committed to git
- Rotate the secret key if it is ever exposed
