import os
import sys
from functools import wraps

from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from devhub.models import AuditLog, User

bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    return decorated


@bp.route("/")
@login_required
@admin_required
def index():
    return redirect(url_for("admin.settings"))


@bp.route("/settings")
@login_required
@admin_required
def settings():
    db_url = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if "@" in db_url:
        db_url = f"...@{db_url.split('@')[-1]}"
    config_info = {
        "version": current_app.config.get("VERSION", "1.0.0"),
        "db_url_masked": db_url,
        "workspace_roots": current_app.config.get("WORKSPACE_ROOTS", []),
        "upload_dir": current_app.config.get("UPLOAD_DIR", "uploads"),
        "quarantine_dir": current_app.config.get("QUARANTINE_DIR", "quarantine"),
        "script_execution": current_app.config.get("ENABLE_SCRIPT_EXECUTION", False),
        "package_install": current_app.config.get("ENABLE_PACKAGE_INSTALL", False),
        "python_version": sys.version,
        "environment": os.environ.get("FLASK_ENV", "production"),
    }
    return render_template("admin/settings.html", config_info=config_info)


@bp.route("/users")
@login_required
@admin_required
def users():
    all_users = User.query.all()
    return render_template("admin/users.html", users=all_users)


@bp.route("/audit")
@login_required
@admin_required
def audit():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()
    return render_template("admin/audit.html", logs=logs)
