from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from devhub.extensions import db
from devhub.models import ProgressReport, Project

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def index():
    all_reports = ProgressReport.query.order_by(ProgressReport.created_at.desc()).all()
    return render_template('reports/index.html', reports=all_reports)

@reports_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    projects = Project.query.all()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        project_id_raw = request.form.get('project_id', '').strip()
        status = request.form.get('status', 'draft')
        if not title:
            flash('Title is required.', 'danger')
            return render_template('reports/view.html', report=None, edit=True, projects=projects)
        if not project_id_raw:
            flash('Project is required.', 'danger')
            return render_template('reports/view.html', report=None, edit=True, projects=projects)
        try:
            project_id = int(project_id_raw)
        except (TypeError, ValueError):
            flash('Please select a valid project.', 'danger')
            return render_template('reports/view.html', report=None, edit=True, projects=projects)
        project = Project.query.get(project_id)
        if project is None:
            flash('Selected project does not exist.', 'danger')
            return render_template('reports/view.html', report=None, edit=True, projects=projects)
        report = ProgressReport(title=title, content=content, project_id=project.id,
                                author_id=current_user.id, status=status)
        db.session.add(report)
        db.session.commit()
        flash('Report created.', 'success')
        return redirect(url_for('reports.view', id=report.id))
    return render_template('reports/view.html', report=None, edit=True, projects=projects)

@reports_bp.route('/<int:id>')
@login_required
def view(id):
    report = ProgressReport.query.get_or_404(id)
    return render_template('reports/view.html', report=report, edit=False, projects=[])

@reports_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    report = ProgressReport.query.get_or_404(id)
    if not current_user.is_admin and report.author_id != current_user.id:
        abort(403)
    projects = Project.query.all()
    if request.method == 'POST':
        report.title = request.form.get('title', report.title).strip()
        report.content = request.form.get('content', report.content).strip()
        report.status = request.form.get('status', report.status)
        db.session.commit()
        flash('Report updated.', 'success')
        return redirect(url_for('reports.view', id=report.id))
    return render_template('reports/view.html', report=report, edit=True, projects=projects)
