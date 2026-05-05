from functools import wraps

from flask import Blueprint, abort, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

from ...extensions import db
from ...models import AuditLog, Project, User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    is_admin = BooleanField('Admin')
    submit = SubmitField('Save User')


class EditProjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 200)])
    description = StringField('Description', validators=[Optional()])
    status = SelectField(
        'Status',
        choices=[('active', 'Active'), ('paused', 'Paused'), ('archived', 'Archived')],
    )
    submit = SubmitField('Save Project')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@login_required
@admin_required
def index():
    users = User.query.all()
    projects = Project.query.all()
    audit_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(50).all()
    config = {
        'ENABLE_SCRIPT_EXECUTION': current_app.config['ENABLE_SCRIPT_EXECUTION'],
        'ENABLE_PACKAGE_INSTALL': current_app.config['ENABLE_PACKAGE_INSTALL'],
        'WORKSPACE_ROOTS': current_app.config['WORKSPACE_ROOTS'],
    }
    return render_template(
        'admin/index.html',
        users=users,
        projects=projects,
        audit_logs=audit_logs,
        config=config,
    )


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash('User updated.', 'success')
        return redirect(url_for('admin.index'))
    return render_template(
        'admin/index.html',
        edit_user=user,
        edit_user_form=form,
        users=User.query.all(),
        projects=Project.query.all(),
        audit_logs=AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(50).all(),
        config={
            'ENABLE_SCRIPT_EXECUTION': current_app.config['ENABLE_SCRIPT_EXECUTION'],
            'ENABLE_PACKAGE_INSTALL': current_app.config['ENABLE_PACKAGE_INSTALL'],
            'WORKSPACE_ROOTS': current_app.config['WORKSPACE_ROOTS'],
        },
    )


@admin_bp.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    form = EditProjectForm(obj=project)
    if form.validate_on_submit():
        project.name = form.name.data
        project.description = form.description.data
        project.status = form.status.data
        db.session.commit()
        flash('Project updated.', 'success')
    return redirect(url_for('admin.index'))
