from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional

from devhub.extensions import db
from devhub.models import Document, Project, Tag

bp = Blueprint("docs", __name__)


class DocForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    summary = TextAreaField("Summary")
    content = TextAreaField("Content")
    doc_type = SelectField(
        "Type",
        choices=[
            ("markdown", "Markdown"),
            ("text", "Text"),
            ("html", "HTML"),
            ("link", "External Link"),
        ],
    )
    status = SelectField(
        "Status",
        choices=[
            ("draft", "Draft"),
            ("canonical", "Canonical"),
            ("stale", "Stale"),
            ("archived", "Archived"),
        ],
    )
    external_url = StringField("External URL", validators=[Optional()])
    project_id = SelectField("Project", coerce=int, validators=[Optional()])
    tags = StringField("Tags (comma-separated)", validators=[Optional()])
    submit = SubmitField("Save")


@bp.route("/")
def index():
    project_id = request.args.get("project_id", type=int)
    status = request.args.get("status")
    doc_type = request.args.get("type")
    q = request.args.get("q", "").strip()

    query = Document.query
    if project_id:
        query = query.filter_by(project_id=project_id)
    if status:
        query = query.filter_by(status=status)
    if doc_type:
        query = query.filter_by(doc_type=doc_type)
    if q:
        query = query.filter(
            (Document.title.ilike(f"%{q}%"))
            | (Document.summary.ilike(f"%{q}%"))
            | (Document.content.ilike(f"%{q}%"))
        )

    docs = query.order_by(Document.updated_at.desc()).all()
    projects = Project.query.all()
    return render_template("docs/index.html", docs=docs, projects=projects, query=q)


@bp.route("/<int:doc_id>")
def view(doc_id):
    doc = Document.query.get_or_404(doc_id)
    return render_template("docs/view.html", doc=doc)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    form = DocForm()
    form.project_id.choices = [(0, "-- None --")] + [
        (p.id, p.name) for p in Project.query.all()
    ]
    if form.validate_on_submit():
        doc = Document(
            title=form.title.data,
            summary=form.summary.data,
            content=form.content.data,
            doc_type=form.doc_type.data,
            status=form.status.data,
            external_url=form.external_url.data,
            project_id=form.project_id.data if form.project_id.data else None,
        )
        if form.tags.data:
            for tag_name in [t.strip() for t in form.tags.data.split(",") if t.strip()]:
                tag = Tag.query.filter_by(name=tag_name).first() or Tag(name=tag_name)
                doc.tags.append(tag)
        db.session.add(doc)
        db.session.commit()
        flash("Document created.", "success")
        return redirect(url_for("docs.view", doc_id=doc.id))
    return render_template("docs/edit.html", form=form, doc=None)


@bp.route("/<int:doc_id>/edit", methods=["GET", "POST"])
@login_required
def edit(doc_id):
    doc = Document.query.get_or_404(doc_id)
    form = DocForm(obj=doc)
    form.project_id.choices = [(0, "-- None --")] + [
        (p.id, p.name) for p in Project.query.all()
    ]
    if form.validate_on_submit():
        doc.title = form.title.data
        doc.summary = form.summary.data
        doc.content = form.content.data
        doc.doc_type = form.doc_type.data
        doc.status = form.status.data
        doc.external_url = form.external_url.data
        doc.project_id = form.project_id.data if form.project_id.data else None
        doc.tags.clear()
        if form.tags.data:
            for tag_name in [t.strip() for t in form.tags.data.split(",") if t.strip()]:
                tag = Tag.query.filter_by(name=tag_name).first() or Tag(name=tag_name)
                doc.tags.append(tag)
        db.session.commit()
        flash("Document updated.", "success")
        return redirect(url_for("docs.view", doc_id=doc.id))
    form.tags.data = ", ".join(t.name for t in doc.tags)
    if doc.project_id:
        form.project_id.data = doc.project_id
    return render_template("docs/edit.html", form=form, doc=doc)


@bp.route("/<int:doc_id>/delete", methods=["POST"])
@login_required
def delete(doc_id):
    doc = Document.query.get_or_404(doc_id)
    db.session.delete(doc)
    db.session.commit()
    flash("Document deleted.", "success")
    return redirect(url_for("docs.index"))
