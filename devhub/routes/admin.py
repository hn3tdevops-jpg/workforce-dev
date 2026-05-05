from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from devhub.extensions import db
from devhub.models import User, Project, Doc, Script, Package, AuditLog

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def require_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

@admin_bp.route('/')
@login_required
def index():
    require_admin()
    stats = {
        'users': User.query.count(),
        'projects': Project.query.count(),
        'docs': Doc.query.count(),
        'scripts': Script.query.count(),
        'packages': Package.query.count(),
    }
    return render_template('admin/index.html', stats=stats)

@admin_bp.route('/users')
@login_required
def users():
    require_admin()
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/users/<int:id>/toggle-admin', methods=['POST'])
@login_required
def toggle_admin(id):
    require_admin()
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Cannot modify your own admin status.', 'danger')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'Admin status updated for {user.username}.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:id>/deactivate', methods=['POST'])
@login_required
def deactivate(id):
    require_admin()
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Cannot deactivate yourself.', 'danger')
    else:
        user.is_active = False
        db.session.commit()
        flash(f'User {user.username} deactivated.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/audit')
@login_required
def audit():
    require_admin()
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/audit.html', logs=logs)
