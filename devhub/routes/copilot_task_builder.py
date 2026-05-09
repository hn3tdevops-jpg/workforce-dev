import json

from flask import Blueprint, flash, render_template, request
from flask_login import login_required

from devhub.data.copilot_templates import TEMPLATES
from devhub.routes.admin import admin_required
from devhub.services.copilot_task_builder import build_prompt, validate_form

bp = Blueprint("dev_hub", __name__)

# Ordered list of (project, task_type, priority) options kept here so the
# template doesn't have to hardcode them.
PROJECTS = [
    "Workforce API",
    "Workforce Frontend",
    "DevHub",
    "Package Manager",
    "Deployment/PythonAnywhere",
    "Other",
]

TASK_TYPES = [
    "Bug fix",
    "Feature build",
    "Security hardening",
    "Test/regression coverage",
    "Refactor",
    "Deployment/debugging",
    "Documentation",
    "PR review",
    "Package install/update",
]

PRIORITIES = ["Low", "Medium", "High", "Critical"]


@bp.route("/copilot-task-builder", methods=["GET", "POST"])
@login_required
@admin_required
def copilot_task_builder():
    prompt: str | None = None
    form_data: dict = {}

    if request.method == "POST":
        form_data = {
            "project": request.form.get("project", ""),
            "task_type": request.form.get("task_type", ""),
            "priority": request.form.get("priority", ""),
            "target_files": request.form.get("target_files", ""),
            "problem_statement": request.form.get("problem_statement", ""),
            "desired_outcome": request.form.get("desired_outcome", ""),
            "acceptance_criteria": request.form.get("acceptance_criteria", ""),
            "test_commands": request.form.get("test_commands", ""),
            "safety_notes": request.form.get("safety_notes", ""),
            "extra_context": request.form.get("extra_context", ""),
        }
        errors = validate_form(form_data)
        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template(
                "dev_hub/copilot_task_builder.html",
                projects=PROJECTS,
                task_types=TASK_TYPES,
                priorities=PRIORITIES,
                templates_json=json.dumps(TEMPLATES),
                template_keys=sorted(TEMPLATES.keys()),
                templates=TEMPLATES,
                form_data=form_data,
                prompt=None,
            )
        prompt = build_prompt(form_data)

    return render_template(
        "dev_hub/copilot_task_builder.html",
        projects=PROJECTS,
        task_types=TASK_TYPES,
        priorities=PRIORITIES,
        templates_json=json.dumps(TEMPLATES),
        template_keys=sorted(TEMPLATES.keys()),
        templates=TEMPLATES,
        form_data=form_data,
        prompt=prompt,
    )
