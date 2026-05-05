from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ...extensions import db
from ...models import ProgressEntry, Project
from .forms import ProgressEntryForm

progress_bp = Blueprint('progress', __name__, url_prefix='/progress')


@progress_bp.route('/')
@login_required
def index():
    project_id = request.args.get('project_id', type=int)
    status = request.args.get('status', '')

    query = ProgressEntry.query
    if project_id:
        query = query.filter_by(project_id=project_id)
    if status:
        query = query.filter_by(status=status)

    entries = query.order_by(ProgressEntry.created_at.desc()).all()
    projects = Project.query.all()
    return render_template(
        'progress/index.html',
        entries=entries,
        projects=projects,
        selected_project=project_id,
        selected_status=status,
    )


@progress_bp.route('/<int:entry_id>')
@login_required
def detail(entry_id):
    entry = ProgressEntry.query.get_or_404(entry_id)
    return render_template('progress/detail.html', entry=entry)


@progress_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = ProgressEntryForm()
    form.project_id.choices = [(0, '-- None --')] + [
        (p.id, p.name) for p in Project.query.all()
    ]
    if form.validate_on_submit():
        entry = ProgressEntry(
            title=form.title.data,
            description=form.description.data,
            status=form.status.data,
            project_id=form.project_id.data or None,
            user_id=current_user.id,
            evidence_links=form.evidence_links.data,
            file_paths=form.file_paths.data,
            commands_run=form.commands_run.data,
            test_results=form.test_results.data,
            notes=form.notes.data,
        )
        db.session.add(entry)
        db.session.commit()
        flash('Progress entry created.', 'success')
        return redirect(url_for('progress.detail', entry_id=entry.id))
    return render_template('progress/edit.html', form=form, entry=None)


@progress_bp.route('/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(entry_id):
    entry = ProgressEntry.query.get_or_404(entry_id)
    form = ProgressEntryForm(obj=entry)
    form.project_id.choices = [(0, '-- None --')] + [
        (p.id, p.name) for p in Project.query.all()
    ]
    if form.validate_on_submit():
        entry.title = form.title.data
        entry.description = form.description.data
        entry.status = form.status.data
        entry.project_id = form.project_id.data or None
        entry.evidence_links = form.evidence_links.data
        entry.file_paths = form.file_paths.data
        entry.commands_run = form.commands_run.data
        entry.test_results = form.test_results.data
        entry.notes = form.notes.data
        db.session.commit()
        flash('Progress entry updated.', 'success')
        return redirect(url_for('progress.detail', entry_id=entry.id))
    return render_template('progress/edit.html', form=form, entry=entry)


@progress_bp.route('/report')
@login_required
def report():
    days = request.args.get('days', 7, type=int)
    project_id = request.args.get('project_id', type=int)
    since = datetime.utcnow() - timedelta(days=days)

    query = ProgressEntry.query.filter(ProgressEntry.created_at >= since)
    if project_id:
        query = query.filter_by(project_id=project_id)
    entries = query.order_by(ProgressEntry.created_at.desc()).all()
    projects = Project.query.all()
    return render_template(
        'progress/report.html',
        entries=entries,
        days=days,
        projects=projects,
        selected_project=project_id,
        since=since,
    )
