from devhub.models import Doc, Script, Project, ProgressReport
from devhub.extensions import db

class SearchEngine:
    def search(self, query, types=None, page=1, per_page=10):
        if not query:
            return {'docs': [], 'scripts': [], 'projects': [], 'reports': []}

        pattern = f'%{query}%'
        results = {}

        if types is None or 'docs' in types:
            docs = Doc.query.filter(
                db.or_(Doc.title.ilike(pattern), Doc.content.ilike(pattern))
            ).limit(per_page).all()
            results['docs'] = [{'id': d.id, 'title': d.title, 'slug': d.slug, 'type': 'doc'} for d in docs]

        if types is None or 'scripts' in types:
            scripts = Script.query.filter(
                db.or_(Script.name.ilike(pattern), Script.description.ilike(pattern))
            ).limit(per_page).all()
            results['scripts'] = [{'id': s.id, 'name': s.name, 'slug': s.slug, 'type': 'script'} for s in scripts]

        if types is None or 'projects' in types:
            projects = Project.query.filter(
                db.or_(Project.name.ilike(pattern), Project.description.ilike(pattern))
            ).limit(per_page).all()
            results['projects'] = [{'id': p.id, 'name': p.name, 'slug': p.slug, 'type': 'project'} for p in projects]

        if types is None or 'reports' in types:
            reports = ProgressReport.query.filter(
                db.or_(ProgressReport.title.ilike(pattern), ProgressReport.content.ilike(pattern))
            ).limit(per_page).all()
            results['reports'] = [{'id': r.id, 'title': r.title, 'type': 'report'} for r in reports]

        return results
