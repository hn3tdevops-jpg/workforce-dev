from flask import Blueprint, render_template
from flask_login import login_required

from ...models import AuditLog, Document, ProgressEntry, Project

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    projects = Project.query.all()
    recent_progress = ProgressEntry.query.order_by(ProgressEntry.created_at.desc()).limit(10).all()
    recent_docs = Document.query.order_by(Document.updated_at.desc()).limit(5).all()
    recent_activity = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(5).all()
    return render_template(
        'main/index.html',
        projects=projects,
        recent_progress=recent_progress,
        recent_docs=recent_docs,
        recent_activity=recent_activity,
    )
