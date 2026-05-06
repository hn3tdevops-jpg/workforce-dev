"""Script runner module - execution is disabled by default for security."""


def run_script(script, dry_run=True, run_by=None):
    """Run a script. Returns dict with exit_code, stdout, stderr."""
    raise NotImplementedError(
        "Script execution is disabled. Set DEVHUB_ENABLE_SCRIPT_EXECUTION=true to enable."
    )
