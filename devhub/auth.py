from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from devhub.extensions import db, bcrypt
from devhub.models import User, AuditLog

auth = Blueprint('auth', __name__, url_prefix='/auth')

def _log(action, user_id=None, details=None):
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type='user',
        details=details,
        ip_address=request.remote_addr,
    )
    db.session.add(entry)
    db.session.commit()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and user.is_active and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            _log('login', user_id=user.id, details=f'User {username} logged in')
            return redirect(url_for('dashboard.index'))
        flash('Invalid username or password.', 'danger')
        _log('login_failed', details=f'Failed login attempt for {username}')
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    _log('logout', user_id=current_user.id, details=f'User {current_user.username} logged out')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if not current_app.config.get('DEVHUB_ALLOW_REGISTRATION', False):
        flash('Registration is currently disabled.', 'info')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('auth/register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')
        is_first = User.query.count() == 0
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=hashed, is_admin=is_first)
        db.session.add(user)
        db.session.commit()
        _log('register', user_id=user.id, details=f'User {username} registered')
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')
