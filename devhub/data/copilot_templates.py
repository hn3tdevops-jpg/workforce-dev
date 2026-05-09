# Safety rules applied automatically to every generated prompt, keyed by project name.
SAFETY_RULES: dict[str, list[str]] = {
    "Workforce API": [
        "Preserve tenant isolation — never expose one tenant's data to another.",
        "Preserve RBAC behaviour — do not weaken or bypass permission checks.",
        "Do not weaken or remove any auth checks.",
        "Keep routers thin; put business logic in service modules.",
        "Use Alembic for all schema changes; do not alter the DB schema directly.",
        "Add or update tests for every permission-sensitive code path.",
    ],
    "Workforce Frontend": [
        "Preserve the existing API contract — do not change request/response shapes.",
        "Keep the mobile layout usable on small screens.",
        "Do not hardcode API URLs; use environment variables or config.",
        "Do not remove or weaken existing auth handling.",
        "Keep build output and deployment behaviour intact.",
    ],
    "DevHub": [
        "Do not expose secrets or sensitive configuration values.",
        "Do not add unsafe shell or command execution.",
        "Protect all admin/control pages with the existing admin guard.",
        "Keep logs and generated artefacts out of public views unless explicitly intended.",
        "Preserve PythonAnywhere WSGI/deployment compatibility.",
    ],
    "Package Manager": [
        "Do not reveal package existence to unauthorised users.",
        "Check admin permissions before any object lookup where applicable.",
        "Preserve audit/action log entries for all state-changing operations.",
        "Make install/approve/uninstall flows explicit and testable.",
    ],
    "Deployment/PythonAnywhere": [
        "Do not break the PythonAnywhere WSGI entry point.",
        "Validate all environment variables before use.",
        "Do not add shell execution without an explicit safety review.",
        "Preserve existing reload/restart procedures.",
    ],
    "Other": [
        "Do not expose secrets or credentials.",
        "Preserve existing auth and permission checks.",
        "Do not introduce unsafe shell execution.",
        "Add or update tests for any changed behaviour.",
    ],
}

# Built-in templates: keys A–H.  Each entry pre-fills every form field.
TEMPLATES: dict[str, dict[str, str]] = {
    "A": {
        "label": "Fix PythonAnywhere WSGI/import error",
        "project": "Deployment/PythonAnywhere",
        "task_type": "Deployment/debugging",
        "priority": "High",
        "target_files": "wsgi.py, devhub/app.py",
        "problem_statement": (
            "The app fails to import or start on PythonAnywhere with a WSGI/import error."
        ),
        "desired_outcome": (
            "The app starts cleanly on PythonAnywhere with no import errors in the error log."
        ),
        "acceptance_criteria": (
            "- App loads at the PythonAnywhere URL without a 500 error\n"
            "- No import errors in the PythonAnywhere error log\n"
            "- Existing routes continue to work"
        ),
        "test_commands": (
            "pytest tests/ -v\n"
            "python -c 'from devhub.app import create_app; app = create_app(); print(\"OK\")'"
        ),
        "safety_notes": (
            "Do not break the WSGI entry point or change the app factory signature."
        ),
        "extra_context": "",
    },
    "B": {
        "label": "Harden admin-only route",
        "project": "DevHub",
        "task_type": "Security hardening",
        "priority": "High",
        "target_files": "devhub/routes/admin.py, devhub/routes/",
        "problem_statement": (
            "An admin-only route is missing the admin_required decorator "
            "or is accessible by non-admin users."
        ),
        "desired_outcome": (
            "The route correctly rejects non-admin users with a redirect, "
            "and the behaviour is covered by a test."
        ),
        "acceptance_criteria": (
            "- Non-admin user receives a redirect when accessing the route\n"
            "- Admin user can access the route normally\n"
            "- A test covers both cases"
        ),
        "test_commands": "pytest tests/ -v -k admin",
        "safety_notes": (
            "Do not remove or weaken the existing admin_required decorator on other routes."
        ),
        "extra_context": "",
    },
    "C": {
        "label": "Add regression test",
        "project": "DevHub",
        "task_type": "Test/regression coverage",
        "priority": "Medium",
        "target_files": "tests/",
        "problem_statement": (
            "A bug was fixed but there is no regression test to prevent it reoccurring."
        ),
        "desired_outcome": (
            "A pytest test that reproduces the original failure and passes after the fix."
        ),
        "acceptance_criteria": (
            "- Test fails against the unfixed code (if verifiable)\n"
            "- Test passes after the fix\n"
            "- No existing tests are broken"
        ),
        "test_commands": "pytest tests/ -v",
        "safety_notes": "Do not modify or delete existing tests.",
        "extra_context": "",
    },
    "D": {
        "label": "Improve mobile navigation",
        "project": "Workforce Frontend",
        "task_type": "Feature build",
        "priority": "Medium",
        "target_files": "devhub/templates/base.html, devhub/static/css/devhub.css",
        "problem_statement": "The sidebar navigation is not usable on small mobile screens.",
        "desired_outcome": (
            "Navigation works cleanly on screens ≤ 375 px; "
            "existing desktop layout is unchanged."
        ),
        "acceptance_criteria": (
            "- Hamburger/offcanvas menu opens and closes on mobile\n"
            "- All nav links are reachable on mobile\n"
            "- Desktop sidebar remains unchanged\n"
            "- No JS errors in console"
        ),
        "test_commands": (
            "pytest tests/ -v\n"
            "# Also test manually at 375 px viewport width"
        ),
        "safety_notes": (
            "Preserve existing API contract. "
            "Do not remove or restructure existing nav links."
        ),
        "extra_context": "",
    },
    "E": {
        "label": "Add package manager feature",
        "project": "Package Manager",
        "task_type": "Feature build",
        "priority": "Medium",
        "target_files": "devhub/routes/packages.py, devhub/templates/packages/",
        "problem_statement": (
            "A new workflow is needed in the package manager "
            "(describe the specific feature here)."
        ),
        "desired_outcome": (
            "The feature is implemented with appropriate admin checks, "
            "audit logging, and tests."
        ),
        "acceptance_criteria": (
            "- Feature is accessible only to authorised users\n"
            "- Audit log entry is created for state-changing actions\n"
            "- Tests cover the happy path and at least one error case"
        ),
        "test_commands": "pytest tests/test_packages.py -v",
        "safety_notes": (
            "Do not reveal package existence to unauthorised users. "
            "Check admin permissions before object lookup."
        ),
        "extra_context": "",
    },
    "F": {
        "label": "Review GitHub PR",
        "project": "DevHub",
        "task_type": "PR review",
        "priority": "Medium",
        "target_files": "",
        "problem_statement": (
            "Review the linked GitHub PR for correctness, security, and style consistency."
        ),
        "desired_outcome": (
            "A structured review with: summary of changes, security concerns, "
            "style issues, test coverage assessment, and approval/request-changes recommendation."
        ),
        "acceptance_criteria": (
            "- All changed files are reviewed\n"
            "- Security and auth impact is assessed\n"
            "- Test coverage is assessed\n"
            "- A clear recommendation is provided"
        ),
        "test_commands": "pytest tests/ -v",
        "safety_notes": (
            "Do not approve changes that weaken auth, expose secrets, "
            "or skip tests for permission-sensitive code."
        ),
        "extra_context": "PR URL: (add here)",
    },
    "G": {
        "label": "Add deployment health check",
        "project": "Deployment/PythonAnywhere",
        "task_type": "Feature build",
        "priority": "Low",
        "target_files": "devhub/routes/main.py, devhub/templates/",
        "problem_statement": (
            "There is no automated health check endpoint that verifies "
            "the deployment is working end-to-end."
        ),
        "desired_outcome": (
            "A /health endpoint (or enhancement to the existing one) that checks "
            "DB connectivity and returns structured JSON."
        ),
        "acceptance_criteria": (
            "- GET /health returns 200 with JSON status\n"
            "- DB connectivity is checked\n"
            "- Response includes version and environment\n"
            "- A test covers the endpoint"
        ),
        "test_commands": "pytest tests/ -v -k health",
        "safety_notes": (
            "Do not expose sensitive config values or secrets in the health response."
        ),
        "extra_context": "",
    },
    "H": {
        "label": "Add CORS/auth debugger",
        "project": "DevHub",
        "task_type": "Feature build",
        "priority": "Low",
        "target_files": "devhub/routes/admin.py, devhub/templates/admin/",
        "problem_statement": (
            "Developers need a way to inspect CORS headers and auth state "
            "for a given request from within the admin UI."
        ),
        "desired_outcome": (
            "An admin-only debug page that shows CORS configuration "
            "and current session/auth state."
        ),
        "acceptance_criteria": (
            "- Page is accessible only to admin users\n"
            "- Shows CORS origin/method configuration\n"
            "- Shows current user auth state\n"
            "- Does not expose secrets or tokens"
        ),
        "test_commands": "pytest tests/ -v -k admin",
        "safety_notes": (
            "Do not expose secret keys, tokens, or passwords. "
            "Admin guard must be applied."
        ),
        "extra_context": "",
    },
}
