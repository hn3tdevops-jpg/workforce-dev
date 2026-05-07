from flask import Blueprint, jsonify, render_template, request

from devhub.models import Document, Package, ProgressEntry, Project, Script, TrackedFile
from devhub.search import search_all

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    all_projects = Project.query.order_by(Project.name).all()
    projects = [project for project in all_projects if project.status == "active"]
    recent_progress = ProgressEntry.query.order_by(ProgressEntry.entry_date.desc()).limit(5).all()
    recent_docs = Document.query.order_by(Document.updated_at.desc()).limit(5).all()
    recent_files = TrackedFile.query.order_by(TrackedFile.last_modified.desc()).limit(5).all()
    recent_packages = Package.query.order_by(Package.uploaded_at.desc()).limit(5).all()
    recent_scripts = Script.query.order_by(Script.created_at.desc()).limit(5).all()
    stats = {
        "projects": Project.query.count(),
        "docs": Document.query.count(),
        "progress": ProgressEntry.query.count(),
        "scripts": Script.query.count(),
        "packages": Package.query.count(),
        "files": TrackedFile.query.count(),
    }
    return render_template(
        "index.html",
        projects=projects,
        all_projects=all_projects,
        stats=stats,
        recent_progress=recent_progress,
        recent_docs=recent_docs,
        recent_files=recent_files,
        recent_packages=recent_packages,
        recent_scripts=recent_scripts,
    )


@bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = {}
    if q:
        results = search_all(q)
    return render_template("search/results.html", query=q, results=results)


@bp.route("/files")
def files():
    tracked_files = TrackedFile.query.order_by(TrackedFile.last_modified.desc()).all()
    return render_template("files/index.html", files=tracked_files)


@bp.route("/health")
def health():
    return jsonify({"status": "ok", "version": "1.0.0"})
