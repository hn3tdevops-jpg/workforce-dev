from datetime import datetime
from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ...extensions import db
from ...models import User
from .forms import LoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def _safe_next(next_url: str | None) -> str:
    """Return next_url only when it is a relative URL (no scheme or host)."""
    if not next_url:
        return url_for('main.index')
    parsed = urlsplit(next_url)
    if parsed.scheme or parsed.netloc:
        return url_for('main.index')
    return next_url


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=form.remember_me.data)
            return redirect(_safe_next(request.args.get('next')))
        flash('Invalid username or password.', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
