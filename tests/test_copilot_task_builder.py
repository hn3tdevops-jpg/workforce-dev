"""Tests for the Copilot Task Builder feature."""

import pytest

from devhub.services.copilot_task_builder import build_prompt, validate_form


# ── Unit tests for the service layer ──────────────────────────────────────────


class TestValidateForm:
    def test_valid_data_returns_no_errors(self):
        data = {
            "project": "DevHub",
            "problem_statement": "Something is broken.",
            "acceptance_criteria": "- It works.",
        }
        assert validate_form(data) == []

    def test_missing_project_returns_error(self):
        data = {
            "project": "",
            "problem_statement": "Something is broken.",
            "acceptance_criteria": "- It works.",
        }
        errors = validate_form(data)
        assert any("Project" in e for e in errors)

    def test_missing_problem_statement_returns_error(self):
        data = {
            "project": "DevHub",
            "problem_statement": "",
            "acceptance_criteria": "- It works.",
        }
        errors = validate_form(data)
        assert any("Problem" in e for e in errors)

    def test_missing_acceptance_criteria_returns_error(self):
        data = {
            "project": "DevHub",
            "problem_statement": "Something is broken.",
            "acceptance_criteria": "",
        }
        errors = validate_form(data)
        assert any("Acceptance" in e for e in errors)


class TestBuildPrompt:
    BASE = {
        "project": "DevHub",
        "task_type": "Bug fix",
        "priority": "High",
        "target_files": "devhub/routes/admin.py",
        "problem_statement": "Admin page is accessible without auth.",
        "desired_outcome": "Admin page requires login.",
        "acceptance_criteria": "- Unauthenticated user is redirected.",
        "test_commands": "pytest tests/ -v -k admin",
        "safety_notes": "Do not break existing admin routes.",
        "extra_context": "See issue #42.",
    }

    def test_prompt_contains_project(self):
        prompt = build_prompt(self.BASE)
        assert "DevHub" in prompt

    def test_prompt_contains_problem_statement(self):
        prompt = build_prompt(self.BASE)
        assert "Admin page is accessible without auth." in prompt

    def test_prompt_contains_acceptance_criteria(self):
        prompt = build_prompt(self.BASE)
        assert "Unauthenticated user is redirected." in prompt

    def test_prompt_contains_test_commands(self):
        prompt = build_prompt(self.BASE)
        assert "pytest tests/ -v -k admin" in prompt

    def test_prompt_includes_devhub_safety_rules(self):
        prompt = build_prompt(self.BASE)
        assert "Do not expose secrets" in prompt
        assert "Do not add unsafe shell" in prompt

    def test_prompt_includes_api_safety_rules_for_api_project(self):
        data = {**self.BASE, "project": "Workforce API"}
        prompt = build_prompt(data)
        assert "tenant isolation" in prompt
        assert "RBAC" in prompt

    def test_prompt_includes_frontend_safety_rules(self):
        data = {**self.BASE, "project": "Workforce Frontend"}
        prompt = build_prompt(data)
        assert "API contract" in prompt
        assert "mobile layout" in prompt

    def test_prompt_includes_package_manager_safety_rules(self):
        data = {**self.BASE, "project": "Package Manager"}
        prompt = build_prompt(data)
        assert "audit" in prompt.lower()

    def test_prompt_includes_expected_report_format(self):
        prompt = build_prompt(self.BASE)
        assert "Expected Report Format" in prompt

    def test_optional_fields_omitted_when_empty(self):
        data = {
            "project": "Other",
            "task_type": "",
            "priority": "",
            "target_files": "",
            "problem_statement": "Minimal prompt.",
            "desired_outcome": "",
            "acceptance_criteria": "- Works.",
            "test_commands": "",
            "safety_notes": "",
            "extra_context": "",
        }
        prompt = build_prompt(data)
        assert "Target Files" not in prompt
        assert "Test Commands" not in prompt
        assert "Extra Context" not in prompt


# ── Integration tests for the route ───────────────────────────────────────────


def _login_as_admin(client, admin_user):
    """Set Flask-Login session keys directly (same pattern as test_packages.py)."""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_user.id)
        sess["_fresh"] = True


def _logout(client):
    with client.session_transaction() as sess:
        sess.pop("_user_id", None)
        sess.pop("_fresh", None)


class TestCopilotTaskBuilderRoute:
    def test_unauthenticated_redirects(self, app):
        with app.app_context():
            fresh_client = app.test_client()
            response = fresh_client.get("/dev-hub/copilot-task-builder", follow_redirects=False)
        assert response.status_code in (302, 301)

    def test_admin_can_load_page(self, client, admin_user):
        _login_as_admin(client, admin_user)
        response = client.get("/dev-hub/copilot-task-builder")
        assert response.status_code == 200
        assert b"Copilot Task Builder" in response.data
        _logout(client)

    def test_page_shows_all_template_buttons(self, client, admin_user):
        _login_as_admin(client, admin_user)
        response = client.get("/dev-hub/copilot-task-builder")
        assert response.status_code == 200
        for letter in "ABCDEFGH":
            assert letter.encode() in response.data
        _logout(client)

    def test_form_submission_generates_prompt(self, client, admin_user):
        _login_as_admin(client, admin_user)
        response = client.post(
            "/dev-hub/copilot-task-builder",
            data={
                "project": "DevHub",
                "task_type": "Bug fix",
                "priority": "High",
                "target_files": "devhub/routes/admin.py",
                "problem_statement": "Route missing admin guard.",
                "desired_outcome": "Route protected.",
                "acceptance_criteria": "- Non-admin redirected.",
                "test_commands": "pytest tests/ -v",
                "safety_notes": "",
                "extra_context": "",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Route missing admin guard." in response.data
        assert b"Non-admin redirected." in response.data
        assert b"pytest tests/ -v" in response.data
        _logout(client)

    def test_generated_prompt_includes_project_safety_rules(self, client, admin_user):
        _login_as_admin(client, admin_user)
        response = client.post(
            "/dev-hub/copilot-task-builder",
            data={
                "project": "Workforce API",
                "task_type": "Security hardening",
                "priority": "Critical",
                "target_files": "",
                "problem_statement": "Auth check missing.",
                "desired_outcome": "Auth enforced.",
                "acceptance_criteria": "- Test passes.",
                "test_commands": "pytest tests/ -v",
                "safety_notes": "",
                "extra_context": "",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"tenant isolation" in response.data
        assert b"RBAC" in response.data
        _logout(client)

    def test_missing_required_fields_shows_error(self, client, admin_user):
        _login_as_admin(client, admin_user)
        response = client.post(
            "/dev-hub/copilot-task-builder",
            data={
                "project": "",
                "task_type": "",
                "priority": "",
                "target_files": "",
                "problem_statement": "",
                "desired_outcome": "",
                "acceptance_criteria": "",
                "test_commands": "",
                "safety_notes": "",
                "extra_context": "",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"required" in response.data.lower()
        _logout(client)

    def test_nav_shows_copilot_task_builder_for_admin(self, client, admin_user):
        _login_as_admin(client, admin_user)
        response = client.get("/")
        assert b"Copilot Task Builder" in response.data
        _logout(client)
