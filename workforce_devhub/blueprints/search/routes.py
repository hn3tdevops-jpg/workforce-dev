from flask import Blueprint, render_template, request
from flask_login import login_required

from ...models import Document, Package, ProgressEntry, Script, TrackedFile

search_bp = Blueprint('search', __name__, url_prefix='/search')


@search_bp.route('/')
@login_required
def results():
    q = request.args.get('q', '').strip()
    docs = []
    progress = []
    scripts = []
    packages = []
    files = []

    if q:
        like = f'%{q}%'
        docs = Document.query.filter(
            (Document.title.ilike(like))
            | (Document.summary.ilike(like))
            | (Document.content.ilike(like))
        ).limit(10).all()

        progress = ProgressEntry.query.filter(
            (ProgressEntry.title.ilike(like))
            | (ProgressEntry.description.ilike(like))
            | (ProgressEntry.notes.ilike(like))
        ).limit(10).all()

        scripts = Script.query.filter(
            (Script.name.ilike(like))
            | (Script.description.ilike(like))
            | (Script.tags.ilike(like))
        ).limit(10).all()

        packages = Package.query.filter(
            (Package.name.ilike(like))
            | (Package.description.ilike(like))
            | (Package.package_key.ilike(like))
        ).limit(10).all()

        files = TrackedFile.query.filter(TrackedFile.file_path.ilike(like)).limit(10).all()

    return render_template(
        'search/results.html',
        q=q,
        docs=docs,
        progress=progress,
        scripts=scripts,
        packages=packages,
        files=files,
    )
