# Security Model

## Authentication

- All routes except `/auth/login` and `/api/*` require authentication via `@login_required`
- Passwords are hashed using Werkzeug's `generate_password_hash` (PBKDF2-HMAC-SHA256)
- Session management via Flask-Login with secure cookies
- Admin-only routes protected by `admin_required` decorator (403 for non-admins)

## CSRF Protection

- Flask-WTF CSRFProtect is applied globally to the entire application
- All HTML forms include `{{ form.hidden_tag() }}` which outputs the CSRF token
- Manual forms (approve/reject) include `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`
- The API blueprint is exempt from CSRF as it does not use forms (read-only endpoints)

## Feature Flags

Two feature flags control dangerous operations:

| Flag | Default | Effect |
|------|---------|--------|
| `DEVHUB_ENABLE_SCRIPT_EXECUTION` | `false` | When false, script commands are shown but not executed |
| `DEVHUB_ENABLE_PACKAGE_INSTALL` | `false` | When false, the install button is disabled |

## Package Upload Security

1. Only `.zip` files are accepted
2. Files are saved to a quarantine directory (`instance/quarantine/`) not the web root
3. `devhub-package.json` manifest is required and validated
4. Path traversal checks:
   - Zip entry names are checked for `..` or absolute paths
   - `intended_paths` in the manifest are checked for `..` and absolute paths
5. Admin approval required before any install action
6. Full audit log of all package actions

## Script Execution Security

- Scripts must be explicitly catalogued in the database
- Uploaded files are never executed directly
- Execution only possible when `DEVHUB_ENABLE_SCRIPT_EXECUTION=true`
- All script runs are logged to `ScriptRunLog`

## Input Validation

- All forms use WTForms validators (DataRequired, Length, URL, Email, etc.)
- File uploads use `FileAllowed` to restrict extensions
- Maximum upload size: 50MB (configurable via `MAX_CONTENT_LENGTH`)

## Audit Logging

- `AuditLog` model records user actions
- `PackageAuditLog` records all package lifecycle events
- Admin panel displays recent audit entries
