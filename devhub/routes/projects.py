from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional

from devhub.extensions import db
from devhub.models import Document, ProgressEntry, Project, Script

bp = Blueprint("projects", __name__)


class ProjectForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    description = TextAreaField("Description")
    status = SelectField(
        "Status",
        choices=[("active", "Active"), ("paused", "Paused"), ("archived", "Archived")],
    )
    repo_url = StringField("Repo URL", validators=[Optional()])
    submit = SubmitField("Save")


@bp.route("/")
@login_required
def index():
    projects = Project.query.order_by(Project.name).all()
    return render_template("projects/index.html", projects=projects)


@bp.route("/<slug>")
@login_required
def view(slug):
    project = Project.query.filter_by(slug=slug).first_or_404()
    recent_progress = (
        ProgressEntry.query.filter_by(project_id=project.id)
        .order_by(ProgressEntry.entry_date.desc())
        .limit(5)
        .all()
    )
    recent_docs = (
        Document.query.filter_by(project_id=project.id)
        .order_by(Document.updated_at.desc())
        .limit(5)
        .all()
    )
    scripts = Script.query.filter_by(project_id=project.id).all()
    return render_template(
        "projects/view.html",
        project=project,
        recent_progress=recent_progress,
        recent_docs=recent_docs,
        scripts=scripts,
    )


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            name=form.name.data,
            slug=form.slug.data,
            description=form.description.data,
            status=form.status.data,
            repo_url=form.repo_url.data,
        )
        db.session.add(project)
        db.session.commit()
        flash("Project created.", "success")
        return redirect(url_for("projects.view", slug=project.slug))
    return render_template("projects/edit.html", form=form, project=None)


@bp.route("/<slug>/edit", methods=["GET", "POST"])
@login_required
def edit(slug):
    project = Project.query.filter_by(slug=slug).first_or_404()
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        project.name = form.name.data
        project.slug = form.slug.data
        project.description = form.description.data
        project.status = form.status.data
        project.repo_url = form.repo_url.data
        db.session.commit()
        flash("Project updated.", "success")
        return redirect(url_for("projects.view", slug=project.slug))
    return render_template("projects/edit.html", form=form, project=project)
