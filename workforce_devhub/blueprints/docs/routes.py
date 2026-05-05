import os

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ...extensions import db
from ...models import Document, Project, Tag
from .forms import DocumentForm, UploadDocForm

docs_bp = Blueprint('docs', __name__, url_prefix='/docs')


@docs_bp.route('/')
@login_required
def index():
    q = request.args.get('q', '')
    project_id = request.args.get('project_id', type=int)
    status = request.args.get('status', '')
    doc_type = request.args.get('doc_type', '')

    query = Document.query
    if q:
        like = f'%{q}%'
        query = query.filter(
            (Document.title.ilike(like))
            | (Document.summary.ilike(like))
            | (Document.content.ilike(like))
        )
    if project_id:
        query = query.filter_by(project_id=project_id)
    if status:
        query = query.filter_by(status=status)
    if doc_type:
        query = query.filter_by(doc_type=doc_type)

    docs = query.order_by(Document.updated_at.desc()).all()
    projects = Project.query.all()
    return render_template(
        'docs/index.html',
        docs=docs,
        projects=projects,
        q=q,
        selected_project=project_id,
        selected_status=status,
        selected_type=doc_type,
    )


@docs_bp.route('/<int:doc_id>')
@login_required
def detail(doc_id):
    doc = Document.query.get_or_404(doc_id)
    return render_template('docs/detail.html', doc=doc)


@docs_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = DocumentForm()
    form.project_id.choices = [(0, '-- None --')] + [
        (p.id, p.name) for p in Project.query.all()
    ]
    if form.validate_on_submit():
        doc = Document(
            title=form.title.data,
            summary=form.summary.data,
            content=form.content.data,
            doc_type=form.doc_type.data,
            status=form.status.data,
            project_id=form.project_id.data or None,
            external_url=form.external_url.data or None,
        )
        if form.tags.data:
            for tag_name in [t.strip() for t in form.tags.data.split(',') if t.strip()]:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                doc.tags.append(tag)
        db.session.add(doc)
        db.session.commit()
        flash('Document created.', 'success')
        return redirect(url_for('docs.detail', doc_id=doc.id))
    return render_template('docs/edit.html', form=form, doc=None)


@docs_bp.route('/<int:doc_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(doc_id):
    doc = Document.query.get_or_404(doc_id)
    form = DocumentForm(obj=doc)
    form.project_id.choices = [(0, '-- None --')] + [
        (p.id, p.name) for p in Project.query.all()
    ]
    if form.validate_on_submit():
        doc.title = form.title.data
        doc.summary = form.summary.data
        doc.content = form.content.data
        doc.doc_type = form.doc_type.data
        doc.status = form.status.data
        doc.project_id = form.project_id.data or None
        doc.external_url = form.external_url.data or None
        doc.tags.clear()
        if form.tags.data:
            for tag_name in [t.strip() for t in form.tags.data.split(',') if t.strip()]:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                doc.tags.append(tag)
        db.session.commit()
        flash('Document updated.', 'success')
        return redirect(url_for('docs.detail', doc_id=doc.id))
    form.tags.data = ', '.join([t.name for t in doc.tags])
    return render_template('docs/edit.html', form=form, doc=doc)


@docs_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadDocForm()
    form.project_id.choices = [(0, '-- None --')] + [
        (p.id, p.name) for p in Project.query.all()
    ]
    if form.validate_on_submit():
        f = form.doc_file.data
        if f:
            filename = f.filename
            upload_dir = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            f.save(save_path)
            content = ''
            try:
                with open(save_path, encoding='utf-8', errors='replace') as fh:
                    content = fh.read()
            except Exception:
                pass
            doc = Document(
                title=form.title.data,
                content=content,
                file_path=save_path,
                project_id=form.project_id.data or None,
                status='draft',
            )
            db.session.add(doc)
            db.session.commit()
            flash('Document uploaded.', 'success')
            return redirect(url_for('docs.detail', doc_id=doc.id))
    return render_template('docs/upload.html', form=form)
