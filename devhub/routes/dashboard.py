from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from devhub.models import Project, Doc, ProgressReport

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
def root():
    return redirect(url_for('dashboard.index'))

@dashboard.route('/dashboard')
@login_required
def index():
    projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    reports = ProgressReport.query.order_by(ProgressReport.created_at.desc()).limit(5).all()
    docs = Doc.query.order_by(Doc.created_at.desc()).limit(5).all()
    return render_template('dashboard/index.html', projects=projects, reports=reports, docs=docs)

@dashboard.route('/dashboard/projects')
@login_required
def projects():
    all_projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('dashboard/index.html', projects=all_projects, reports=[], docs=[])

@dashboard.route('/dashboard/projects/<slug>')
@login_required
def project(slug):
    p = Project.query.filter_by(slug=slug).first_or_404()
    return render_template('dashboard/project.html', project=p)
