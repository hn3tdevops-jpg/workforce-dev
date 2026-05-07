import json
import os
import re
import zipfile
from pathlib import Path

REQUIRED_MANIFEST_FIELDS = [
    "package_key",
    "name",
    "version",
    "description",
    "target_project",
    "intended_paths",
    "install_steps",
    "rollback_notes",
    "risk_level",
    "requires_manual_review",
]

MANIFEST_FILENAME = "devhub-package.json"


def _is_within_root(path_str, root_str):
    """Return True iff the resolved path_str is inside (or equal to) resolved root_str.

    Uses Path.resolve() + os.path.commonpath() to prevent prefix-escape attacks such as
    /workspace_api_evil escaping root /workspace_api, and to normalise ``..`` / ``.``
    segments and redundant slashes before comparison.
    """
    try:
        resolved = str(Path(path_str).resolve())
        resolved_root = str(Path(root_str).resolve())
        common = os.path.commonpath([resolved, resolved_root])
        return common == resolved_root
    except ValueError:
        # commonpath raises ValueError on mixed drive roots on Windows — treat as unsafe
        return False


def validate_package(zip_path, workspace_roots=None):
    """Validate a package zip. Returns dict with valid bool, manifest, error."""
    if not os.path.exists(zip_path):
        return {"valid": False, "error": "File not found", "manifest": None}

    if not zipfile.is_zipfile(zip_path):
        return {"valid": False, "error": "Not a valid zip file", "manifest": None}

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()

            for name in names:
                if ".." in name or name.startswith("/") or os.path.isabs(name):
                    return {
                        "valid": False,
                        "error": f"Path traversal detected in zip entry: {name}",
                        "manifest": None,
                    }
                if re.match(r"^[A-Za-z]:", name):
                    return {
                        "valid": False,
                        "error": f"Absolute path detected in zip entry: {name}",
                        "manifest": None,
                    }

            if MANIFEST_FILENAME not in names:
                return {
                    "valid": False,
                    "error": f"Missing {MANIFEST_FILENAME} in package",
                    "manifest": None,
                }

            manifest_data = zf.read(MANIFEST_FILENAME)
            try:
                manifest = json.loads(manifest_data)
            except json.JSONDecodeError as e:
                return {"valid": False, "error": f"Invalid manifest JSON: {e}", "manifest": None}

            missing = [f for f in REQUIRED_MANIFEST_FIELDS if f not in manifest]
            if missing:
                return {
                    "valid": False,
                    "error": f"Missing manifest fields: {missing}",
                    "manifest": manifest,
                }

            if manifest.get("risk_level") not in ("safe", "moderate", "dangerous"):
                return {
                    "valid": False,
                    "error": "Invalid risk_level. Must be safe, moderate, or dangerous",
                    "manifest": manifest,
                }

            if workspace_roots:
                for path in manifest.get("intended_paths", []):
                    if os.path.isabs(path):
                        if not any(_is_within_root(path, root) for root in workspace_roots):
                            return {
                                "valid": False,
                                "error": f"Path {path} escapes workspace roots",
                                "manifest": manifest,
                            }
                    else:
                        # Resolve relative paths against each root and verify containment
                        for root in workspace_roots:
                            candidate = os.path.join(root, path)
                            if not _is_within_root(candidate, root):
                                return {
                                    "valid": False,
                                    "error": f"Path traversal in intended_path: {path}",
                                    "manifest": manifest,
                                }
            else:
                for path in manifest.get("intended_paths", []):
                    if os.path.isabs(path):
                        return {
                            "valid": False,
                            "error": f"Unsafe absolute path in intended_paths: {path}",
                            "manifest": manifest,
                        }
                    # Resolve relative path and ensure it stays below a safe sentinel root
                    sentinel = Path("/safe_root")
                    try:
                        resolved = (sentinel / path).resolve()
                        common = os.path.commonpath([str(resolved), str(sentinel)])
                        if common != str(sentinel):
                            return {
                                "valid": False,
                                "error": f"Path traversal in intended_paths: {path}",
                                "manifest": manifest,
                            }
                    except Exception:
                        return {
                            "valid": False,
                            "error": f"Unsafe path in intended_paths: {path}",
                            "manifest": manifest,
                        }

            return {"valid": True, "error": None, "manifest": manifest, "file_list": names}

    except zipfile.BadZipFile as e:
        return {"valid": False, "error": f"Bad zip file: {e}", "manifest": None}
    except Exception as e:
        return {"valid": False, "error": f"Validation error: {e}", "manifest": None}
