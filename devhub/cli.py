import click
import os
from flask.cli import with_appcontext
from devhub.extensions import db, bcrypt
from devhub.models import User, Project, Doc, ProgressReport, Script

def register_commands(app):
    app.cli.add_command(seed_db)
    app.cli.add_command(create_admin)
    app.cli.add_command(scan_files)
    app.cli.add_command(init_uploads)

@click.command('seed-db')
@with_appcontext
def seed_db():
    """Seed the database with sample data."""
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        click.echo('No admin user found. Run create-admin first.')
        return

    p = Project(name='Sample Project', slug='sample-project',
                description='A sample project for demonstration.', owner_id=admin.id)
    db.session.add(p)
    db.session.flush()

    d = Doc(title='Getting Started', slug='getting-started',
            content='Welcome to the Workforce Developer Hub.', category='general',
            project_id=p.id, author_id=admin.id)
    db.session.add(d)

    r = ProgressReport(title='Week 1 Report', project_id=p.id, author_id=admin.id,
                       content='Initial setup completed.', status='published')
    db.session.add(r)

    s = Script(name='Hello World', slug='hello-world',
               description='Prints hello world', content='print("Hello, World!")',
               language='python', author_id=admin.id)
    db.session.add(s)

    db.session.commit()
    click.echo('Database seeded.')

@click.command('create-admin')
@with_appcontext
def create_admin():
    """Create an admin user."""
    username = click.prompt('Username')
    email = click.prompt('Email')
    password = click.prompt('Password', hide_input=True, confirmation_prompt=True)
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=username, email=email, password_hash=hashed, is_admin=True)
    db.session.add(user)
    db.session.commit()
    click.echo(f'Admin user {username} created.')

@click.command('scan-files')
@with_appcontext
def scan_files():
    """Run file scanner."""
    from devhub.scanner import FileScanner
    from flask import current_app
    path = current_app.config.get('DEVHUB_SCAN_PATH', '.')
    scanner = FileScanner()
    records = scanner.scan_directory(path)
    scanner.update_database(records)
    click.echo(f'Scanned {len(records)} files.')

@click.command('init-uploads')
@with_appcontext
def init_uploads():
    """Create upload quarantine directory."""
    from flask import current_app
    folder = current_app.config.get('UPLOAD_FOLDER', 'uploads/quarantine')
    os.makedirs(folder, exist_ok=True)
    click.echo(f'Upload directory ready: {folder}')
