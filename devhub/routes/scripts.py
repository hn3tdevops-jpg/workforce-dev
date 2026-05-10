import re
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from devhub.extensions import db
from devhub.models import Script
from devhub.script_runner import ScriptRunner

scripts_bp = Blueprint('scripts', __name__, url_prefix='/scripts')

def slugify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

def generate_unique_slug(name):
    base = slugify(name) or 'script'
    candidate = base
    suffix = 2
    while Script.query.filter_by(slug=candidate).first() is not None:
        candidate = f'{base}-{suffix}'
        suffix += 1
    return candidate

@scripts_bp.route('/')
@login_required
def index():
    all_scripts = Script.query.order_by(Script.created_at.desc()).all()
    return render_template('scripts/index.html', scripts=all_scripts)

@scripts_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if not current_user.is_admin:
        abort(403)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        content = request.form.get('content', '').strip()
        language = request.form.get('language', 'python')
        if not name:
            flash('Name is required.', 'danger')
            return render_template('scripts/view.html', script=None, edit=True)
        slug = generate_unique_slug(name)
        script = Script(name=name, slug=slug, description=description, content=content,
                        language=language, author_id=current_user.id)
        db.session.add(script)
        db.session.commit()
        flash('Script created.', 'success')
        return redirect(url_for('scripts.view', slug=script.slug))
    return render_template('scripts/view.html', script=None, edit=True)

@scripts_bp.route('/<slug>')
@login_required
def view(slug):
    script = Script.query.filter_by(slug=slug).first_or_404()
    return render_template('scripts/view.html', script=script, edit=False)

@scripts_bp.route('/<slug>/run', methods=['POST'])
@login_required
def run(slug):
    if not current_user.is_admin:
        abort(403)
    script = Script.query.filter_by(slug=slug).first_or_404()
    runner = ScriptRunner()
    result = runner.run_script(script.id, current_user.id)
    flash(result.get('error', result.get('output', 'Done')), 'info')
    return redirect(url_for('scripts.view', slug=slug))
