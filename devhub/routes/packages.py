import os
import uuid
import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from devhub.extensions import db
from devhub.models import Package, AuditLog
from devhub.package_validator import PackageValidator

packages_bp = Blueprint('packages', __name__, url_prefix='/packages')

@packages_bp.route('/')
@login_required
def index():
    all_packages = Package.query.order_by(Package.uploaded_at.desc()).all()
    return render_template('packages/index.html', packages=all_packages)

@packages_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file provided.', 'danger')
            return render_template('packages/upload.html')
        f = request.files['file']
        if not f.filename:
            flash('No file selected.', 'danger')
            return render_template('packages/upload.html')
        if not f.filename.endswith('.zip'):
            flash('Only .zip files are allowed.', 'danger')
            return render_template('packages/upload.html')

        folder = current_app.config.get('UPLOAD_FOLDER', 'uploads/quarantine')
        os.makedirs(folder, exist_ok=True)
        safe_name = f'{uuid.uuid4().hex}.zip'
        filepath = os.path.join(folder, safe_name)
        f.save(filepath)

        validator = PackageValidator()
        result = validator.validate_zip(filepath)

        status = 'validated' if result['valid'] else 'rejected'
        manifest_json = json.dumps(result['manifest']) if result['manifest'] else None
        notes = '; '.join(result['errors']) if result['errors'] else None

        pkg = Package(
            filename=safe_name,
            original_filename=f.filename,
            manifest_data=manifest_json,
            status=status,
            uploaded_by=current_user.id,
            notes=notes,
        )
        db.session.add(pkg)

        log = AuditLog(user_id=current_user.id, action='package_upload',
                       resource_type='package', details=f'Uploaded {f.filename}',
                       ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()

        flash(f'Package uploaded and {status}.', 'success' if result['valid'] else 'warning')
        return redirect(url_for('packages.view', id=pkg.id))
    return render_template('packages/upload.html')

@packages_bp.route('/<int:id>')
@login_required
def view(id):
    pkg = Package.query.get_or_404(id)
    manifest = {}
    if pkg.manifest_data:
        try:
            manifest = json.loads(pkg.manifest_data)
        except Exception:
            manifest = {}
    return render_template('packages/index.html', packages=[], pkg=pkg, manifest=manifest)

@packages_bp.route('/<int:id>/validate', methods=['POST'])
@login_required
def validate(id):
    if not current_user.is_admin:
        abort(403)
    pkg = Package.query.get_or_404(id)
    folder = current_app.config.get('UPLOAD_FOLDER', 'uploads/quarantine')
    filepath = os.path.join(folder, pkg.filename)
    validator = PackageValidator()
    result = validator.validate_zip(filepath)
    pkg.status = 'validated' if result['valid'] else 'rejected'
    pkg.notes = '; '.join(result['errors']) if result['errors'] else None
    if result['manifest']:
        pkg.manifest_data = json.dumps(result['manifest'])
    log = AuditLog(
        user_id=current_user.id,
        action='package_revalidate',
        resource_type='package',
        resource_id=pkg.id,
        details=f'package_id={pkg.id}; actor_id={current_user.id}; outcome={pkg.status}',
        ip_address=request.remote_addr,
    )
    db.session.add(log)
    db.session.commit()
    flash(f'Package re-validated: {pkg.status}', 'info')
    return redirect(url_for('packages.view', id=pkg.id))
