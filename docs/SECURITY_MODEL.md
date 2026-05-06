# Security Model

## Overview

Workforce Dev Hub is designed as an internal developer tool. This document describes the security model, trust boundaries, and threat mitigations.

## Authentication

- **Flask-Login** is used for session-based authentication.
- Passwords are hashed with **Werkzeug's `generate_password_hash`** (PBKDF2-SHA256 by default).
- CSRF protection is enabled globally via **Flask-WTF/CSRFProtect** on all POST forms.
- Sessions are signed with `DEVHUB_SECRET_KEY` — this key must be kept secret and rotated if compromised.

## Authorization

- Most read-only views are public within the application (no authentication required).
- Write operations (create, edit, delete) require the user to be **logged in**.
- Admin-only operations (approve packages, view audit log, manage users) require `is_admin=True`.
- The `admin_required` decorator enforces this at the route level.

## Package Security

Packages go through a strict quarantine workflow:

1. **Upload** — file is saved to the quarantine directory (never directly to production paths).
2. **Validation** — `package_validator.validate_package()` checks:
   - Valid zip file
   - No path traversal in zip entries (`..` or absolute paths)
   - Presence of `devhub-package.json` manifest
   - All required manifest fields present
   - Valid `risk_level` value
   - `intended_paths` do not escape workspace roots
3. **Admin Approval** — only admin users can approve a quarantined package.
4. **Install** — disabled by default (`DEVHUB_ENABLE_PACKAGE_INSTALL=false`). Even when enabled, the current implementation requires manual review.

### Path Traversal Prevention

- Zip entries are checked for `..`, leading `/`, and absolute paths.
- Manifest `intended_paths` are checked for `..` and absolute paths not within configured workspace roots.
- `os.path.abspath` and path prefix checks are used for workspace root validation.

## Script Execution Security

- Script execution is **disabled by default** (`DEVHUB_ENABLE_SCRIPT_EXECUTION=false`).
- When disabled, no script commands are run regardless of UI actions.
- The Script library is a read-only catalog when execution is disabled.
- Scripts are tagged with `risk_level`: `safe`, `moderate`, or `dangerous`.
- All script runs are logged to `ScriptRunLog` with stdout, stderr, exit code, and who ran them.

## Audit Logging

All sensitive actions are written to the `AuditLog` table:
- Package uploads and approvals
- (Extendable to: user creation, document deletion, etc.)

Audit logs are viewable by admin users at `/admin/audit`.

## Secrets Management

- `DEVHUB_SECRET_KEY` — must be a long random string in production.
- Never commit `.env` to git (`.gitignore` excludes it).
- PythonAnywhere deployments should set environment variables in the WSGI config file.
- No credentials are hardcoded in source code.

## Input Validation

- All forms use **WTForms validators** (DataRequired, Email, Optional).
- CSRF tokens are required on all POST forms.
- File uploads are restricted to `.zip` only via extension check and `secure_filename`.
- Package manifest JSON is parsed safely with error handling.

## Threat Model

| Threat | Mitigation |
|--------|-----------|
| CSRF attacks | Flask-WTF CSRF protection on all forms |
| Password brute force | No rate limiting built-in (add nginx/PythonAnywhere rate limiting) |
| Path traversal in packages | Zip entry and manifest path validation |
| Malicious package install | Disabled by default; requires admin approval first |
| Script injection | Execution disabled by default |
| Session hijacking | Signed sessions; use HTTPS in production |
| XSS | Jinja2 auto-escaping enabled |
| Secrets exposure | `.env` excluded from git; secret key configurable via env |

## Recommendations for Production

1. Use HTTPS (PythonAnywhere provides this automatically).
2. Set a strong, random `DEVHUB_SECRET_KEY`.
3. Keep `DEVHUB_ENABLE_SCRIPT_EXECUTION=false` and `DEVHUB_ENABLE_PACKAGE_INSTALL=false`.
4. Regularly rotate the secret key.
5. Review audit logs periodically.
6. Restrict access to the PythonAnywhere account itself.
