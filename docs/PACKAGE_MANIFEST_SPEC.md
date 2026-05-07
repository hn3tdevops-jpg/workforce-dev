# Package Manifest Specification

## Overview

Every package zip must include a `devhub-package.json` manifest in the zip root. This file describes the package, its purpose, risk level, and the files it intends to place.

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Human-readable package name |
| `slug` | string | URL-safe identifier (lowercase, hyphens) |
| `version` | string | SemVer version string (e.g. `1.2.0`) |
| `description` | string | Short description of what this package does |
| `author` | string | Author name or email |
| `risk_level` | string | One of: `safe`, `moderate`, `dangerous` |
| `intended_paths` | array of strings | List of paths where files will be installed |
| `python_requires` | string | Minimum Python version (e.g. `>=3.11`) |
| `dependencies` | array of strings | Python package dependencies (pip format) |
| `entry_point` | string | Main script or module path inside the zip |

## Field Details

### `risk_level`

Describes the potential impact of this package:

- **`safe`** — Read-only operations, no system changes, no external network calls.
- **`moderate`** — May write files to disk within the workspace, makes local changes.
- **`dangerous`** — May install system dependencies, execute shell commands, make network requests, or modify files outside the workspace.

Admin approval is required before any package with `risk_level: dangerous` can be installed.

### `intended_paths`

A list of file paths or directory paths where this package's files will be placed. These paths:

- Must be **relative paths** (no absolute paths starting with `/`)
- Must **not contain `..`** (no path traversal)
- Must be within the configured `DEVHUB_WORKSPACE_ROOTS`

**Example (valid):**
```json
"intended_paths": ["scripts/my_script.py", "config/my_config.json"]
```

**Example (invalid — rejected):**
```json
"intended_paths": ["../../etc/passwd", "/usr/bin/evil"]
```

### `dependencies`

Standard pip requirement specifiers:

```json
"dependencies": ["requests>=2.28", "pandas>=1.5.0"]
```

## Full Example Manifest

```json
{
  "name": "Workforce Report Generator",
  "slug": "workforce-report-gen",
  "version": "1.0.0",
  "description": "Generates weekly workforce status reports from database snapshots.",
  "author": "Dev Team <dev@example.com>",
  "risk_level": "safe",
  "intended_paths": [
    "scripts/generate_report.py",
    "scripts/report_utils.py"
  ],
  "python_requires": ">=3.11",
  "dependencies": [
    "jinja2>=3.1",
    "openpyxl>=3.1"
  ],
  "entry_point": "generate_report.py"
}
```

## Validation Rules

During upload, `package_validator.validate_package()` enforces:

1. The file is a valid zip archive.
2. `devhub-package.json` is present in the zip root.
3. The manifest is valid JSON.
4. All 10 required fields are present (non-empty values for strings, list type for arrays).
5. `risk_level` is one of `safe`, `moderate`, `dangerous`.
6. No zip entry paths contain `..` or start with `/`.
7. No `intended_paths` entries contain `..` or start with `/`.

Packages that fail validation are rejected and not stored.

## Package Zip Structure

```
my-package-1.0.0.zip
├── devhub-package.json   ← required manifest (zip root)
├── generate_report.py    ← entry_point
├── report_utils.py
└── README.md             ← optional
```
