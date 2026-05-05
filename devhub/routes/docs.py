import re
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from devhub.extensions import db
from devhub.models import Doc, AuditLog

docs_bp = Blueprint('docs', __name__, url_prefix='/docs')

def slugify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

@docs_bp.route('/')
def index():
    category = request.args.get('category')
    q = Doc.query
    if category:
        q = q.filter_by(category=category)
    all_docs = q.order_by(Doc.created_at.desc()).all()
    return render_template('docs/index.html', docs=all_docs, category=category)

@docs_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', '').strip()
        if not title:
            flash('Title is required.', 'danger')
            return render_template('docs/view.html', doc=None, edit=True)
        slug = slugify(title)
        existing = Doc.query.filter_by(slug=slug).first()
        if existing:
            slug = f'{slug}-{Doc.query.count()}'
        doc = Doc(title=title, slug=slug, content=content, category=category, author_id=current_user.id)
        db.session.add(doc)
        db.session.commit()
        flash('Document created.', 'success')
        return redirect(url_for('docs.view', slug=doc.slug))
    return render_template('docs/view.html', doc=None, edit=True)

@docs_bp.route('/<slug>')
def view(slug):
    doc = Doc.query.filter_by(slug=slug).first_or_404()
    return render_template('docs/view.html', doc=doc, edit=False)

@docs_bp.route('/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit(slug):
    doc = Doc.query.filter_by(slug=slug).first_or_404()
    if not current_user.is_admin and doc.author_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        doc.title = request.form.get('title', doc.title).strip()
        doc.content = request.form.get('content', doc.content).strip()
        doc.category = request.form.get('category', doc.category).strip()
        db.session.commit()
        flash('Document updated.', 'success')
        return redirect(url_for('docs.view', slug=doc.slug))
    return render_template('docs/view.html', doc=doc, edit=True)

@docs_bp.route('/<slug>/delete', methods=['POST'])
@login_required
def delete(slug):
    if not current_user.is_admin:
        abort(403)
    doc = Doc.query.filter_by(slug=slug).first_or_404()
    db.session.delete(doc)
    db.session.commit()
    flash('Document deleted.', 'success')
    return redirect(url_for('docs.index'))
