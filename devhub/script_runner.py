from datetime import datetime
from devhub.extensions import db
from devhub.models import Script, AuditLog

class ScriptRunner:
    def run_script(self, script_id, user_id, app=None):
        if app is None:
            from flask import current_app
            enabled = current_app.config.get('DEVHUB_ENABLE_SCRIPT_EXECUTION', False)
        else:
            enabled = app.config.get('DEVHUB_ENABLE_SCRIPT_EXECUTION', False)

        script = Script.query.get(script_id)
        script_name = script.name if script else f'id={script_id}'

        log = AuditLog(
            user_id=user_id,
            action='script_run_attempt',
            resource_type='script',
            resource_id=script_id,
            details=f'Attempted to run script: {script_name}',
            created_at=datetime.utcnow(),
        )
        db.session.add(log)
        db.session.commit()

        if not enabled:
            return {'success': False, 'output': '', 'error': 'Script execution is disabled'}

        if not script:
            return {'success': False, 'output': '', 'error': 'Script not found'}

        return {'success': False, 'output': '', 'error': 'Script execution is disabled'}
