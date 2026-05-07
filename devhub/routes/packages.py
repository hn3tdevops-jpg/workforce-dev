import json
import os
import uuid
from datetime import datetime

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from devhub.extensions import db
from devhub.models import AuditLog, Package
from devhub.package_validator import validate_package

bp = Blueprint("packages", __name__)

ALLOWED_EXTENSIONS = {"zip"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/")
def index():
    packages = Package.query.order_by(Package.uploaded_at.desc()).all()
    install_enabled = current_app.config.get("ENABLE_PACKAGE_INSTALL", False)
    return render_template(
        "packages/index.html", packages=packages, install_enabled=install_enabled
    )


@bp.route("/<int:pkg_id>")
def view(pkg_id):
    pkg = Package.query.get_or_404(pkg_id)
    manifest = {}
    try:
        manifest = json.loads(pkg.manifest_data or "{}")
    except Exception:
        pass
    install_enabled = current_app.config.get("ENABLE_PACKAGE_INSTALL", False)
    return render_template(
        "packages/view.html", pkg=pkg, manifest=manifest, install_enabled=install_enabled
    )


@bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part.", "danger")
            return redirect(url_for("packages.upload"))
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file.", "danger")
            return redirect(url_for("packages.upload"))
        if not allowed_file(file.filename):
            flash("Only zip files are allowed.", "danger")
            return redirect(url_for("packages.upload"))

        original_filename = secure_filename(file.filename)

        # Store each upload in its own unique subdirectory to prevent overwrites.
        upload_id = uuid.uuid4().hex
        quarantine_base = current_app.config.get("QUARANTINE_DIR", "quarantine")
        upload_dir = os.path.join(quarantine_base, upload_id)
        os.makedirs(upload_dir, exist_ok=True)
        save_path = os.path.join(upload_dir, original_filename)
        file.save(save_path)

        workspace_roots = current_app.config.get("WORKSPACE_ROOTS", [])
        result = validate_package(save_path, workspace_roots)

        manifest_data = json.dumps(result.get("manifest") or {})
        pkg = Package(
            filename=original_filename,
            quarantine_path=save_path,
            manifest_valid=result["valid"],
            manifest_data=manifest_data,
            status="quarantined",
        )
        if result["valid"] and result["manifest"]:
            m = result["manifest"]
            pkg.package_key = m.get("package_key")
            pkg.name = m.get("name")
            pkg.version = m.get("version")
            pkg.description = m.get("description")
            pkg.target_project = m.get("target_project")
            pkg.risk_level = m.get("risk_level", "safe")
            pkg.requires_manual_review = m.get("requires_manual_review", True)

        db.session.add(pkg)

        audit = AuditLog(
            action="package_upload",
            resource_type="package",
            user_email=current_user.email,
            details=f"Uploaded {original_filename} (id={upload_id}), valid={result['valid']}",
        )
        db.session.add(audit)
        db.session.commit()

        if result["valid"]:
            flash(f"Package uploaded and validated: {original_filename}", "success")
        else:
            flash(f"Package uploaded but validation failed: {result['error']}", "warning")

        return redirect(url_for("packages.view", pkg_id=pkg.id))

    return render_template("packages/upload.html")


@bp.route("/<int:pkg_id>/approve", methods=["POST"])
@login_required
def approve(pkg_id):
    if not current_user.is_admin:
        flash("Admin access required.", "danger")
        return redirect(url_for("packages.index"))
    pkg = Package.query.get_or_404(pkg_id)
    if not pkg.manifest_valid:
        flash("Cannot approve a package with invalid manifest.", "danger")
        return redirect(url_for("packages.view", pkg_id=pkg_id))
    pkg.status = "approved"
    pkg.approved_at = datetime.utcnow()
    pkg.approved_by = current_user.email
    audit = AuditLog(
        action="package_approve",
        resource_type="package",
        resource_id=pkg.id,
        user_email=current_user.email,
    )
    db.session.add(audit)
    db.session.commit()
    flash("Package approved.", "success")
    return redirect(url_for("packages.view", pkg_id=pkg_id))


@bp.route("/<int:pkg_id>/install", methods=["POST"])
@login_required
def install(pkg_id):
    if not current_user.is_admin:
        flash("Admin access required.", "danger")
        return redirect(url_for("packages.index"))
    pkg = Package.query.get_or_404(pkg_id)
    if not current_app.config.get("ENABLE_PACKAGE_INSTALL", False):
        flash(
            "Package install is disabled. Set DEVHUB_ENABLE_PACKAGE_INSTALL=true to enable.",
            "warning",
        )
        return redirect(url_for("packages.view", pkg_id=pkg_id))
    if pkg.status != "approved":
        flash("Package must be approved before install.", "danger")
        return redirect(url_for("packages.view", pkg_id=pkg_id))
    flash("Install is disabled in this version. Review the install plan manually.", "info")
    return redirect(url_for("packages.view", pkg_id=pkg_id))
