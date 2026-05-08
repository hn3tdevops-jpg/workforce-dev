from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional

from devhub.extensions import db
from devhub.models import Project, Script, ScriptRunLog, Tag

bp = Blueprint("scripts", __name__)


class ScriptForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    project_id = SelectField("Project", coerce=int, validators=[Optional()])
    file_path = StringField("File Path")
    risk_level = SelectField(
        "Risk Level",
        choices=[("safe", "Safe"), ("moderate", "Moderate"), ("dangerous", "Dangerous")],
    )
    dry_run_command = StringField("Dry Run Command")
    normal_command = StringField("Normal Command")
    owner = StringField("Owner")
    notes = TextAreaField("Notes")
    tags = StringField("Tags (comma-separated)")
    submit = SubmitField("Save")


@bp.route("/")
@login_required
def index():
    project_id = request.args.get("project_id", type=int)
    risk = request.args.get("risk")
    query = Script.query
    if project_id:
        query = query.filter_by(project_id=project_id)
    if risk:
        query = query.filter_by(risk_level=risk)
    scripts = query.order_by(Script.name).all()
    projects = Project.query.all()
    execution_enabled = current_app.config.get("ENABLE_SCRIPT_EXECUTION", False)
    return render_template(
        "scripts/index.html",
        scripts=scripts,
        projects=projects,
        execution_enabled=execution_enabled,
    )


@bp.route("/<int:script_id>")
@login_required
def view(script_id):
    script = Script.query.get_or_404(script_id)
    logs = (
        ScriptRunLog.query.filter_by(script_id=script_id)
        .order_by(ScriptRunLog.run_at.desc())
        .limit(20)
        .all()
    )
    execution_enabled = current_app.config.get("ENABLE_SCRIPT_EXECUTION", False)
    return render_template(
        "scripts/view.html", script=script, logs=logs, execution_enabled=execution_enabled
    )


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    form = ScriptForm()
    form.project_id.choices = [(0, "-- None --")] + [
        (p.id, p.name) for p in Project.query.all()
    ]
    if form.validate_on_submit():
        script = Script(
            name=form.name.data,
            description=form.description.data,
            project_id=form.project_id.data if form.project_id.data else None,
            file_path=form.file_path.data,
            risk_level=form.risk_level.data,
            dry_run_command=form.dry_run_command.data,
            normal_command=form.normal_command.data,
            owner=form.owner.data,
            notes=form.notes.data,
        )
        if form.tags.data:
            for tag_name in [t.strip() for t in form.tags.data.split(",") if t.strip()]:
                tag = Tag.query.filter_by(name=tag_name).first() or Tag(name=tag_name)
                script.tags.append(tag)
        db.session.add(script)
        db.session.commit()
        flash("Script added.", "success")
        return redirect(url_for("scripts.view", script_id=script.id))
    return render_template("scripts/edit.html", form=form, script=None)


@bp.route("/<int:script_id>/edit", methods=["GET", "POST"])
@login_required
def edit(script_id):
    script = Script.query.get_or_404(script_id)
    form = ScriptForm(obj=script)
    form.project_id.choices = [(0, "-- None --")] + [
        (p.id, p.name) for p in Project.query.all()
    ]
    if form.validate_on_submit():
        script.name = form.name.data
        script.description = form.description.data
        script.project_id = form.project_id.data if form.project_id.data else None
        script.file_path = form.file_path.data
        script.risk_level = form.risk_level.data
        script.dry_run_command = form.dry_run_command.data
        script.normal_command = form.normal_command.data
        script.owner = form.owner.data
        script.notes = form.notes.data
        script.tags.clear()
        if form.tags.data:
            for tag_name in [t.strip() for t in form.tags.data.split(",") if t.strip()]:
                tag = Tag.query.filter_by(name=tag_name).first() or Tag(name=tag_name)
                script.tags.append(tag)
        db.session.commit()
        flash("Script updated.", "success")
        return redirect(url_for("scripts.view", script_id=script.id))
    form.tags.data = ", ".join(t.name for t in script.tags)
    if script.project_id:
        form.project_id.data = script.project_id
    return render_template("scripts/edit.html", form=form, script=script)
