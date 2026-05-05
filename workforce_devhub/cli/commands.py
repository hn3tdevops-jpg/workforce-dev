import hashlib
import os
from datetime import datetime

import click
from flask.cli import with_appcontext

from ..extensions import db
from ..models import TrackedFile, User


def register_commands(app):
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_command)
    app.cli.add_command(scan_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(validate_package_command)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database."""
    db.create_all()
    click.echo('Database initialized.')


@click.command('seed')
@with_appcontext
def seed_command():
    """Seed the database with initial data."""
    from ..seed.data import run_seed
    run_seed()
    click.echo('Database seeded.')


@click.command('scan')
@with_appcontext
def scan_command():
    """Scan workspace roots and track files."""
    from flask import current_app
    roots = current_app.config.get('WORKSPACE_ROOTS', [])
    if not roots:
        click.echo('No DEVHUB_WORKSPACE_ROOTS configured.')
        return

    scanned = 0
    for root in roots:
        if not os.path.exists(root):
            click.echo(f'Warning: root not found: {root}')
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [
                d for d in dirnames
                if not d.startswith('.') and d not in ('__pycache__', 'node_modules', '.git')
            ]
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                try:
                    stat = os.stat(fpath)
                    with open(fpath, 'rb') as f:
                        checksum = hashlib.sha256(f.read()).hexdigest()
                    existing = TrackedFile.query.filter_by(file_path=fpath).first()
                    if existing:
                        existing.last_scanned = datetime.utcnow()
                        existing.file_size = stat.st_size
                        existing.last_modified = datetime.fromtimestamp(stat.st_mtime)
                        existing.checksum = checksum
                    else:
                        tf = TrackedFile(
                            file_path=fpath,
                            last_scanned=datetime.utcnow(),
                            file_size=stat.st_size,
                            last_modified=datetime.fromtimestamp(stat.st_mtime),
                            checksum=checksum,
                        )
                        db.session.add(tf)
                    scanned += 1
                except (OSError, PermissionError):
                    pass
    db.session.commit()
    click.echo(f'Scanned {scanned} files.')


@click.command('create-admin')
@with_appcontext
def create_admin_command():
    """Create an admin user."""
    username = click.prompt('Username')
    email = click.prompt('Email')
    password = click.prompt('Password', hide_input=True, confirmation_prompt=True)
    user = User.query.filter_by(username=username).first()
    if user:
        click.echo(f'User {username} already exists.')
        return
    user = User(username=username, email=email, is_admin=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f'Admin user {username} created.')


@click.command('validate-package')
@click.argument('path')
@with_appcontext
def validate_package_command(path):
    """Validate a package zip file."""
    from ..blueprints.packages.routes import validate_package_zip
    if not os.path.exists(path):
        click.echo(f'File not found: {path}')
        return
    manifest, errors = validate_package_zip(path)
    if errors:
        click.echo('Validation FAILED:')
        for e in errors:
            click.echo(f'  - {e}')
    else:
        click.echo('Validation PASSED.')
        click.echo(f'Package: {manifest.get("name")} v{manifest.get("version")}')
        click.echo(f'Target: {manifest.get("target_project")}')
        click.echo(f'Risk level: {manifest.get("risk_level")}')
