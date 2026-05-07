# Script Library Specification

## Overview

The Script Library is a catalog of automation scripts that can be stored, documented, and optionally executed within the Workforce Dev Hub. Scripts are for internal use and represent repeatable tasks performed by the dev team.

## Script Risk Levels

Each script has a `risk_level` that describes its potential impact:

| Level | Description | Examples |
|-------|-------------|---------|
| `safe` | Read-only operations, no system state changes | Report generators, data exports, file readers |
| `moderate` | Local file writes, database updates, workspace changes | Data migrations, config generators, file copiers |
| `dangerous` | Shell commands, network requests, system-level operations | Deployment scripts, package installers, OS operations |

## Script Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Human-readable name |
| `slug` | string | URL-safe identifier |
| `description` | text | Full description of what the script does |
| `script_type` | string | Language: `python`, `bash`, `powershell` |
| `risk_level` | string | `safe`, `moderate`, or `dangerous` |
| `is_active` | boolean | Whether the script is enabled in the catalog |
| `content` | text | The script source code |
| `tags` | many-to-many | Associated tags |

## Execution Policy

Script execution is **disabled by default** and is **not yet implemented** in the current version.
This is controlled by:

```
DEVHUB_ENABLE_SCRIPT_EXECUTION=false   ← default (and only supported value)
```

When `false` (current behavior):
- No script commands are executed, regardless of UI actions.
- The script catalog is a **read-only reference library**.
- `script_runner.py` raises `NotImplementedError`.

When `true` (reserved for a future release — not yet implemented):
- A controlled allowlisted runner will be implemented with safe directories, timeout,
  audit logs, and dry-run support.
- All runs will be logged to `ScriptRunLog`.
- Do not set this to `true` in the current version — it has no effect beyond the flag.

## Dry-Run Pattern

All scripts should be written with a dry-run mode:

```python
import sys

DRY_RUN = "--dry-run" in sys.argv

if DRY_RUN:
    print("[DRY RUN] Would delete 42 rows from stale_records")
else:
    cursor.execute("DELETE FROM stale_records WHERE ...")
    print(f"Deleted {cursor.rowcount} rows")
```

This allows operators to preview changes before applying them.

## Security Rules

1. **Never enable execution on a public-facing instance** without network-level access controls.
2. Scripts with `risk_level: dangerous` should be reviewed by a second team member before being marked `is_active=True`.
3. Script content is stored as plain text in the database — treat it as trusted code, not user input.
4. Script execution runs in a subprocess with a timeout; no persistent shell sessions.
5. `ScriptRunLog` entries are immutable — do not delete run history.

## Catalog Conventions

- Use descriptive `title` values that explain the outcome, not the mechanism (e.g., "Export Weekly Workforce Report" not "run_export.py").
- Tag scripts with relevant project and category tags.
- Keep `description` accurate — it is the primary documentation for users deciding whether to run a script.
- Scripts that are retired should be set `is_active=False` rather than deleted, to preserve run history.

## Example Script Entry

```
Title:       Export Weekly Workforce Report
Slug:        export-weekly-report
Type:        python
Risk Level:  safe
Description: Exports the current week's workforce progress entries to a CSV file
             in the exports/ directory. Supports --dry-run to preview output path.
Tags:        reporting, weekly, workforce-api
```

```python
#!/usr/bin/env python3
"""Export weekly workforce progress to CSV."""
import sys
import csv
import os
from datetime import datetime, timedelta

DRY_RUN = "--dry-run" in sys.argv
EXPORT_DIR = os.environ.get("DEVHUB_EXPORT_DIR", "exports")

today = datetime.today()
week_start = today - timedelta(days=today.weekday())
outfile = os.path.join(EXPORT_DIR, f"workforce-{week_start:%Y-%m-%d}.csv")

if DRY_RUN:
    print(f"[DRY RUN] Would write to {outfile}")
    sys.exit(0)

os.makedirs(EXPORT_DIR, exist_ok=True)
# ... fetch and write data ...
print(f"Exported to {outfile}")
```
