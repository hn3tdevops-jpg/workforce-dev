# Deploying to PythonAnywhere

## Prerequisites
- PythonAnywhere account
- This repository cloned to your PythonAnywhere files

## Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/workforce-dev.git
   ```

2. **Create a virtual environment**
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 workforce-dev
   pip install -r requirements.txt
   ```

3. **Set environment variables** in the PythonAnywhere web app configuration:
   - `FLASK_APP=devhub.app`
   - `FLASK_ENV=production`
   - `SECRET_KEY=<your-secret-key>`
   - `DATABASE_URL=sqlite:////home/<username>/workforce-dev/devhub.db`

4. **Configure the WSGI file** (set in PythonAnywhere dashboard):
   ```python
   import sys, os
   sys.path.insert(0, '/home/<username>/workforce-dev')
   os.environ['FLASK_ENV'] = 'production'
   from devhub.app import create_app
   application = create_app('production')
   ```

5. **Initialize the database**:
   ```bash
   flask db init
   flask db migrate -m "initial"
   flask db upgrade
   flask create-admin
   ```

6. **Reload** the web app from the PythonAnywhere dashboard.
