"""Service layer for the Copilot Task Builder.

Generates a structured Copilot prompt from a dictionary of form values.
No I/O, no Flask context needed — pure transformation.
"""

from devhub.data.copilot_templates import SAFETY_RULES

# Fields that must be present (non-empty) for a valid prompt.
REQUIRED_FIELDS = ("project", "problem_statement", "acceptance_criteria")


def build_prompt(data: dict) -> str:
    """Return a formatted Markdown Copilot prompt string from *data*.

    *data* is expected to contain the keys that match the Copilot Task Builder
    form fields.  Missing or empty optional fields are omitted gracefully.
    """
    project = (data.get("project") or "").strip()
    task_type = (data.get("task_type") or "").strip()
    priority = (data.get("priority") or "").strip()
    target_files = (data.get("target_files") or "").strip()
    problem_statement = (data.get("problem_statement") or "").strip()
    desired_outcome = (data.get("desired_outcome") or "").strip()
    acceptance_criteria = (data.get("acceptance_criteria") or "").strip()
    test_commands = (data.get("test_commands") or "").strip()
    safety_notes = (data.get("safety_notes") or "").strip()
    extra_context = (data.get("extra_context") or "").strip()

    safety_rules = SAFETY_RULES.get(project, SAFETY_RULES["Other"])

    lines: list[str] = []

    # ── Header ────────────────────────────────────────────────────────────────
    lines += [
        "# Copilot Task Prompt",
        "",
        f"**Project:** {project}  ",
        f"**Task type:** {task_type}  ",
        f"**Priority:** {priority}",
        "",
    ]

    # ── Goal / Problem statement ───────────────────────────────────────────────
    lines += [
        "## Goal",
        problem_statement,
        "",
    ]

    # ── Desired outcome ────────────────────────────────────────────────────────
    if desired_outcome:
        lines += [
            "## Desired Outcome",
            desired_outcome,
            "",
        ]

    # ── Target files ──────────────────────────────────────────────────────────
    if target_files:
        lines += [
            "## Target Files / Directories",
            target_files,
            "",
        ]

    # ── Acceptance criteria ────────────────────────────────────────────────────
    lines += [
        "## Acceptance Criteria",
        acceptance_criteria,
        "",
    ]

    # ── Test commands ──────────────────────────────────────────────────────────
    if test_commands:
        lines += [
            "## Test Commands",
            "```",
            test_commands,
            "```",
            "",
        ]

    # ── Safety constraints ─────────────────────────────────────────────────────
    lines.append("## Safety Constraints")
    for rule in safety_rules:
        lines.append(f"- {rule}")
    if safety_notes:
        lines.append(f"- {safety_notes}")
    lines.append("")

    # ── Extra context ──────────────────────────────────────────────────────────
    if extra_context:
        lines += [
            "## Extra Context",
            extra_context,
            "",
        ]

    # ── Expected report format ─────────────────────────────────────────────────
    lines += [
        "## Expected Report Format",
        "After completing the task, report:",
        "- Files changed (with a brief description of each change)",
        "- Route or endpoint added (if applicable)",
        "- Exact test command run",
        "- Exact test result (pass/fail counts)",
        "- Any limitations or follow-up work",
    ]

    return "\n".join(lines)


def validate_form(data: dict) -> list[str]:
    """Return a list of human-readable validation error messages.

    An empty list means the form is valid.
    """
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if not (data.get(field) or "").strip():
            label = field.replace("_", " ").capitalize()
            errors.append(f"{label} is required.")
    return errors
