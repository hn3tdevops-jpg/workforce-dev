import sys
import os
from datetime import datetime
from flask import Blueprint, jsonify, request

from devhub.models import Document, Package, ProgressEntry, Project, Script
from devhub.search import search_all

bp = Blueprint("api", __name__)


@bp.route("/status")
def status():
    from flask import current_app

    return jsonify(
        {
            "status": "ok",
            "version": current_app.config.get("VERSION", "1.0.0"),
            "script_execution_enabled": current_app.config.get("ENABLE_SCRIPT_EXECUTION", False),
            "package_install_enabled": current_app.config.get("ENABLE_PACKAGE_INSTALL", False),
            "python_version": sys.version,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "q parameter required"}), 400
    results = search_all(q)
    return jsonify(results)


@bp.route("/progress/recent")
def recent_progress():
    entries = ProgressEntry.query.order_by(ProgressEntry.entry_date.desc()).limit(10).all()
    return jsonify(
        [
            {
                "id": e.id,
                "title": e.title,
                "status": e.status,
                "project": e.project.name if e.project else None,
                "entry_date": e.entry_date.isoformat() if e.entry_date else None,
            }
            for e in entries
        ]
    )


@bp.route("/projects")
def projects():
    projs = Project.query.all()
    return jsonify(
        [
            {
                "id": p.id,
                "name": p.name,
                "slug": p.slug,
                "status": p.status,
                "description": p.description,
            }
            for p in projs
        ]
    )


@bp.route("/docs")
def docs():
    all_docs = Document.query.all()
    return jsonify(
        [
            {
                "id": d.id,
                "title": d.title,
                "status": d.status,
                "doc_type": d.doc_type,
                "project": d.project.name if d.project else None,
            }
            for d in all_docs
        ]
    )


@bp.route("/scripts")
def scripts():
    all_scripts = Script.query.all()
    return jsonify(
        [
            {
                "id": s.id,
                "name": s.name,
                "risk_level": s.risk_level,
                "project": s.project.name if s.project else None,
                "last_run_status": s.last_run_status,
            }
            for s in all_scripts
        ]
    )
