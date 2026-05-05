"""Entry point for python -m devhub."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devhub.app import create_app

app = create_app()

with app.app_context():
    from devhub.cli import (
        create_admin_cmd,
        init_db_cmd,
        scan_cmd,
        seed_cmd,
        validate_package_cmd,
    )

    commands = {
        "init-db": init_db_cmd,
        "seed": seed_cmd,
        "scan": scan_cmd,
        "create-admin": create_admin_cmd,
        "validate-package": validate_package_cmd,
    }

    if len(sys.argv) > 1 and sys.argv[1] in commands:
        cmd = commands[sys.argv[1]]
        sys.argv = sys.argv[1:]
        cmd.main(standalone_mode=True)
    else:
        print(f"Available commands: {', '.join(commands.keys())}")
        print("Or run with flask: flask <command>")
