from flask import Blueprint, jsonify, request
from flask_login import login_required
from devhub.models import Project, Doc
from devhub.search import SearchEngine

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/health')
def health():
    return jsonify({'status': 'ok'})

@api_bp.route('/projects')
@login_required
def projects():
    all_projects = Project.query.all()
    return jsonify([{
        'id': p.id, 'name': p.name, 'slug': p.slug,
        'description': p.description, 'status': p.status,
    } for p in all_projects])

@api_bp.route('/docs')
@login_required
def docs():
    all_docs = Doc.query.all()
    return jsonify([{
        'id': d.id, 'title': d.title, 'slug': d.slug, 'category': d.category,
    } for d in all_docs])

@api_bp.route('/search')
@login_required
def search():
    q = request.args.get('q', '').strip()
    engine = SearchEngine()
    results = engine.search(q)
    return jsonify(results)
