from flask import Blueprint, current_app, render_template
from flask_login import login_required

from ...models import Project, Script, ScriptRunLog

scripts_bp = Blueprint('scripts', __name__, url_prefix='/scripts')


@scripts_bp.route('/')
@login_required
def index():
    scripts = Script.query.all()
    projects = Project.query.all()
    return render_template(
        'scripts/index.html',
        scripts=scripts,
        projects=projects,
        exec_enabled=current_app.config['ENABLE_SCRIPT_EXECUTION'],
    )


@scripts_bp.route('/<int:script_id>')
@login_required
def detail(script_id):
    script = Script.query.get_or_404(script_id)
    run_logs = script.run_logs.order_by(ScriptRunLog.ran_at.desc()).limit(20).all()
    exec_enabled = current_app.config['ENABLE_SCRIPT_EXECUTION']
    return render_template(
        'scripts/detail.html',
        script=script,
        run_logs=run_logs,
        exec_enabled=exec_enabled,
    )
