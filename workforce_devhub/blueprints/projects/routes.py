from flask import Blueprint, render_template
from flask_login import login_required

from ...models import Document, ProgressEntry, Project

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')


@projects_bp.route('/')
@login_required
def index():
    projects = Project.query.all()
    return render_template('projects/index.html', projects=projects)


@projects_bp.route('/<slug>')
@login_required
def detail(slug):
    project = Project.query.filter_by(slug=slug).first_or_404()
    recent_progress = (
        project.progress_entries.order_by(ProgressEntry.created_at.desc()).limit(5).all()
    )
    recent_docs = project.documents.order_by(Document.updated_at.desc()).limit(5).all()
    scripts = project.scripts.all()
    tracked_files = project.tracked_files.limit(10).all()
    return render_template(
        'projects/detail.html',
        project=project,
        recent_progress=recent_progress,
        recent_docs=recent_docs,
        scripts=scripts,
        tracked_files=tracked_files,
    )
