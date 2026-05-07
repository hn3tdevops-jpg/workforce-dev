import json
from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional

from devhub.extensions import db
from devhub.models import ProgressEntry, Project, Tag

bp = Blueprint("progress", __name__)


class ProgressForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description")
    status = SelectField(
        "Status",
        choices=[
            ("in-progress", "In Progress"),
            ("completed", "Completed"),
            ("blocked", "Blocked"),
            ("planned", "Planned"),
        ],
    )
    project_id = SelectField("Project", coerce=int, validators=[Optional()])
    evidence_links = TextAreaField("Evidence Links (one per line)")
    file_paths = TextAreaField("File Paths (one per line)")
    commands_run = TextAreaField("Commands Run")
    test_results = TextAreaField("Test Results")
    notes = TextAreaField("Notes")
    tags = StringField("Tags (comma-separated)")
    submit = SubmitField("Save")


@bp.route("/")
def index():
    project_id = request.args.get("project_id", type=int)
    status = request.args.get("status")
    since = request.args.get("since")

    query = ProgressEntry.query
    if project_id:
        query = query.filter_by(project_id=project_id)
    if status:
        query = query.filter_by(status=status)
    if since:
        try:
            since_dt = datetime.strptime(since, "%Y-%m-%d")
            query = query.filter(ProgressEntry.entry_date >= since_dt)
        except ValueError:
            pass

    entries = query.order_by(ProgressEntry.entry_date.desc()).all()
    projects = Project.query.all()
    return render_template("progress/index.html", entries=entries, projects=projects)


@bp.route("/<int:entry_id>")
def view(entry_id):
    entry = ProgressEntry.query.get_or_404(entry_id)
    evidence = []
    try:
        evidence = json.loads(entry.evidence_links or "[]")
    except Exception:
        pass
    return render_template("progress/view.html", entry=entry, evidence=evidence)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    form = ProgressForm()
    form.project_id.choices = [(0, "-- None --")] + [
        (p.id, p.name) for p in Project.query.all()
    ]
    if form.validate_on_submit():
        links = [lnk.strip() for lnk in form.evidence_links.data.split("\n") if lnk.strip()]
        paths = [p.strip() for p in form.file_paths.data.split("\n") if p.strip()]
        entry = ProgressEntry(
            title=form.title.data,
            description=form.description.data,
            status=form.status.data,
            project_id=form.project_id.data if form.project_id.data else None,
            evidence_links=json.dumps(links),
            file_paths=json.dumps(paths),
            commands_run=form.commands_run.data,
            test_results=form.test_results.data,
            notes=form.notes.data,
        )
        if form.tags.data:
            for tag_name in [t.strip() for t in form.tags.data.split(",") if t.strip()]:
                tag = Tag.query.filter_by(name=tag_name).first() or Tag(name=tag_name)
                entry.tags.append(tag)
        db.session.add(entry)
        db.session.commit()
        flash("Progress entry created.", "success")
        return redirect(url_for("progress.view", entry_id=entry.id))
    return render_template("progress/edit.html", form=form, entry=None)


@bp.route("/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def edit(entry_id):
    entry = ProgressEntry.query.get_or_404(entry_id)
    form = ProgressForm(obj=entry)
    form.project_id.choices = [(0, "-- None --")] + [
        (p.id, p.name) for p in Project.query.all()
    ]
    if form.validate_on_submit():
        links = [lnk.strip() for lnk in form.evidence_links.data.split("\n") if lnk.strip()]
        paths = [p.strip() for p in form.file_paths.data.split("\n") if p.strip()]
        entry.title = form.title.data
        entry.description = form.description.data
        entry.status = form.status.data
        entry.project_id = form.project_id.data if form.project_id.data else None
        entry.evidence_links = json.dumps(links)
        entry.file_paths = json.dumps(paths)
        entry.commands_run = form.commands_run.data
        entry.test_results = form.test_results.data
        entry.notes = form.notes.data
        entry.tags.clear()
        if form.tags.data:
            for tag_name in [t.strip() for t in form.tags.data.split(",") if t.strip()]:
                tag = Tag.query.filter_by(name=tag_name).first() or Tag(name=tag_name)
                entry.tags.append(tag)
        db.session.commit()
        flash("Progress entry updated.", "success")
        return redirect(url_for("progress.view", entry_id=entry.id))
    form.tags.data = ", ".join(t.name for t in entry.tags)
    if entry.project_id:
        form.project_id.data = entry.project_id
    try:
        form.evidence_links.data = "\n".join(json.loads(entry.evidence_links or "[]"))
        form.file_paths.data = "\n".join(json.loads(entry.file_paths or "[]"))
    except Exception:
        pass
    return render_template("progress/edit.html", form=form, entry=entry)


@bp.route("/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete(entry_id):
    entry = ProgressEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted.", "success")
    return redirect(url_for("progress.index"))


@bp.route("/report")
def report():
    days = request.args.get("days", 30, type=int)
    project_id = request.args.get("project_id", type=int)
    since = datetime.utcnow() - timedelta(days=days)
    query = ProgressEntry.query.filter(ProgressEntry.entry_date >= since)
    if project_id:
        query = query.filter_by(project_id=project_id)
    entries = query.order_by(ProgressEntry.entry_date.desc()).all()
    projects = Project.query.all()
    return render_template(
        "progress/report.html", entries=entries, projects=projects, days=days
    )
