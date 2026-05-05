from flask import Blueprint, render_template, request
from flask_login import login_required

from ...models import Project, TrackedFile

files_bp = Blueprint('files', __name__, url_prefix='/files')


@files_bp.route('/')
@login_required
def index():
    project_id = request.args.get('project_id', type=int)
    query = TrackedFile.query
    if project_id:
        query = query.filter_by(project_id=project_id)
    files = query.order_by(TrackedFile.last_scanned.desc()).all()
    projects = Project.query.all()
    return render_template(
        'files/index.html',
        files=files,
        projects=projects,
        selected_project=project_id,
    )
