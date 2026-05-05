import json
import os
import zipfile

from flask import Blueprint, abort, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import SubmitField
from wtforms.validators import DataRequired

from ...extensions import db
from ...models import Package, PackageAuditLog

packages_bp = Blueprint('packages', __name__, url_prefix='/packages')

REQUIRED_MANIFEST_KEYS = [
    'package_key', 'name', 'version', 'description', 'target_project',
    'intended_paths', 'install_steps', 'rollback_notes', 'risk_level',
    'requires_manual_review',
]


class UploadPackageForm(FlaskForm):
    package_file = FileField(
        'Package (.zip)',
        validators=[DataRequired(), FileAllowed(['zip'], 'Only .zip files allowed')],
    )
    submit = SubmitField('Upload Package')


def validate_package_zip(filepath):
    """Validate a .zip package. Returns (manifest_dict, errors_list)."""
    errors = []
    manifest = None

    if not zipfile.is_zipfile(filepath):
        return None, ['File is not a valid ZIP archive.']

    with zipfile.ZipFile(filepath, 'r') as zf:
        names = zf.namelist()

        for name in names:
            if '..' in name or name.startswith('/') or name.startswith('\\'):
                errors.append(f'Path traversal detected in zip entry: {name}')

        if errors:
            return None, errors

        if 'devhub-package.json' not in names:
            return None, ['Missing devhub-package.json manifest in zip root.']

        try:
            manifest_bytes = zf.read('devhub-package.json')
            manifest = json.loads(manifest_bytes.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return None, [f'Invalid manifest JSON: {e}']

        missing = [k for k in REQUIRED_MANIFEST_KEYS if k not in manifest]
        if missing:
            errors.append(f'Missing manifest keys: {", ".join(missing)}')

        if 'intended_paths' in manifest:
            for path in manifest.get('intended_paths', []):
                if '..' in path or os.path.isabs(path):
                    errors.append(f'Path traversal in intended_paths: {path}')

    return manifest, errors


@packages_bp.route('/')
@login_required
def index():
    packages = Package.query.order_by(Package.uploaded_at.desc()).all()
    return render_template(
        'packages/index.html',
        packages=packages,
        install_enabled=current_app.config['ENABLE_PACKAGE_INSTALL'],
    )


@packages_bp.route('/<int:pkg_id>')
@login_required
def detail(pkg_id):
    pkg = Package.query.get_or_404(pkg_id)
    audit_logs = pkg.audit_logs.order_by(PackageAuditLog.timestamp.desc()).all()
    install_enabled = current_app.config['ENABLE_PACKAGE_INSTALL']
    manifest = None
    if pkg.manifest:
        try:
            manifest = json.loads(pkg.manifest)
        except Exception:
            pass
    return render_template(
        'packages/detail.html',
        pkg=pkg,
        audit_logs=audit_logs,
        install_enabled=install_enabled,
        manifest=manifest,
    )


@packages_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadPackageForm()
    if form.validate_on_submit():
        f = form.package_file.data
        quarantine_dir = current_app.config['QUARANTINE_FOLDER']
        os.makedirs(quarantine_dir, exist_ok=True)

        filename = f.filename
        save_path = os.path.join(quarantine_dir, filename)
        f.save(save_path)

        manifest, errors = validate_package_zip(save_path)

        if errors:
            os.remove(save_path)
            for e in errors:
                flash(f'Validation error: {e}', 'danger')
            return render_template('packages/upload.html', form=form)

        pkg = Package(
            name=manifest.get('name', filename),
            version=manifest.get('version', '0.0.0'),
            package_key=manifest.get('package_key', filename),
            description=manifest.get('description', ''),
            target_project=manifest.get('target_project', ''),
            filename=filename,
            manifest=json.dumps(manifest),
            status='validated',
            risk_level=manifest.get('risk_level', 'unknown'),
            uploaded_by=current_user.id,
        )
        db.session.add(pkg)
        db.session.flush()

        log = PackageAuditLog(
            package_id=pkg.id,
            user_id=current_user.id,
            action='uploaded',
            detail=f'Uploaded and validated: {filename}',
        )
        db.session.add(log)
        db.session.commit()

        flash(f'Package "{pkg.name}" uploaded and validated.', 'success')
        return redirect(url_for('packages.detail', pkg_id=pkg.id))

    return render_template('packages/upload.html', form=form)


@packages_bp.route('/<int:pkg_id>/approve', methods=['POST'])
@login_required
def approve(pkg_id):
    if not current_user.is_admin:
        abort(403)
    pkg = Package.query.get_or_404(pkg_id)
    pkg.status = 'approved'
    log = PackageAuditLog(
        package_id=pkg.id, user_id=current_user.id, action='approved', detail='Approved by admin'
    )
    db.session.add(log)
    db.session.commit()
    flash('Package approved.', 'success')
    return redirect(url_for('packages.detail', pkg_id=pkg.id))


@packages_bp.route('/<int:pkg_id>/reject', methods=['POST'])
@login_required
def reject(pkg_id):
    if not current_user.is_admin:
        abort(403)
    pkg = Package.query.get_or_404(pkg_id)
    pkg.status = 'rejected'
    log = PackageAuditLog(
        package_id=pkg.id,
        user_id=current_user.id,
        action='rejected',
        detail='Rejected by admin',
    )
    db.session.add(log)
    db.session.commit()
    flash('Package rejected.', 'danger')
    return redirect(url_for('packages.detail', pkg_id=pkg.id))
