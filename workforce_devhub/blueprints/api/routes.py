from flask import Blueprint, jsonify, request

from ...models import Document, ProgressEntry, Project

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'workforce-devhub'})


@api_bp.route('/status')
def status():
    projects = Project.query.all()
    return jsonify({
        'projects': [
            {'slug': p.slug, 'name': p.name, 'status': p.status}
            for p in projects
        ]
    })


@api_bp.route('/projects')
def projects():
    ps = Project.query.all()
    return jsonify([
        {'id': p.id, 'slug': p.slug, 'name': p.name, 'status': p.status,
         'description': p.description}
        for p in ps
    ])


@api_bp.route('/projects/<slug>')
def project_detail(slug):
    p = Project.query.filter_by(slug=slug).first_or_404()
    return jsonify({
        'id': p.id, 'slug': p.slug, 'name': p.name, 'status': p.status,
        'description': p.description, 'created_at': p.created_at.isoformat(),
    })


@api_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'results': []})
    like = f'%{q}%'
    docs = Document.query.filter(
        (Document.title.ilike(like)) | (Document.summary.ilike(like))
    ).limit(5).all()
    progress = ProgressEntry.query.filter(
        (ProgressEntry.title.ilike(like)) | (ProgressEntry.description.ilike(like))
    ).limit(5).all()
    return jsonify({
        'query': q,
        'results': {
            'docs': [{'id': d.id, 'title': d.title} for d in docs],
            'progress': [{'id': e.id, 'title': e.title} for e in progress],
        },
    })
