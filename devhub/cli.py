import click
from flask.cli import with_appcontext

from devhub.extensions import db


def register_commands(app):
    app.cli.add_command(init_db_cmd)
    app.cli.add_command(seed_cmd)
    app.cli.add_command(scan_cmd)
    app.cli.add_command(create_admin_cmd)
    app.cli.add_command(validate_package_cmd)


@click.command("init-db")
@with_appcontext
def init_db_cmd():
    """Initialize the database."""
    db.create_all()
    click.echo("Database initialized.")


@click.command("seed")
@with_appcontext
def seed_cmd():
    """Seed the database with starter data."""
    from devhub.seed import seed_data

    seed_data()
    click.echo("Seed data loaded.")


@click.command("scan")
@click.option("--root", multiple=True, help="Additional workspace roots to scan")
@with_appcontext
def scan_cmd(root):
    """Scan workspace roots and update file index."""
    from flask import current_app

    from devhub.scanner import scan_workspace

    roots = list(root) + current_app.config.get("WORKSPACE_ROOTS", [])
    if not roots:
        click.echo("No workspace roots configured. Set DEVHUB_WORKSPACE_ROOTS or pass --root.")
        return
    count = scan_workspace(
        roots,
        excluded_dirs=current_app.config["SCANNER_EXCLUDED_DIRS"],
        excluded_extensions=current_app.config["SCANNER_EXCLUDED_EXTENSIONS"],
    )
    click.echo(f"Scan complete. {count} files indexed.")


@click.command("create-admin")
@click.option("--email", prompt=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@with_appcontext
def create_admin_cmd(email, password):
    """Create an admin user."""
    from devhub.models import User

    existing = User.query.filter_by(email=email).first()
    if existing:
        click.echo(f"User {email} already exists.")
        return
    user = User(email=email, is_admin=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f"Admin user {email} created.")


@click.command("validate-package")
@click.argument("path")
@with_appcontext
def validate_package_cmd(path):
    """Validate a package zip file."""
    from devhub.package_validator import validate_package

    result = validate_package(path)
    if result["valid"]:
        click.echo("Package is valid.")
        click.echo(f"  Name: {result['manifest'].get('name')}")
        click.echo(f"  Version: {result['manifest'].get('version')}")
        click.echo(f"  Risk: {result['manifest'].get('risk_level')}")
    else:
        click.echo(f"Package validation failed: {result['error']}")
