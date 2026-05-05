from datetime import datetime

from ..extensions import db
from ..models import Document, ProgressEntry, Project, Script, Tag, TrackedFile, User

PROJECTS = [
    {
        'slug': 'workforce-api',
        'name': 'Workforce API',
        'description': 'Workforce API backend service',
        'status': 'active',
    },
    {
        'slug': 'workforce-frontend',
        'name': 'Workforce Frontend',
        'description': 'Workforce frontend console application',
        'status': 'active',
    },
    {
        'slug': 'devhub',
        'name': 'Dev Hub',
        'description': 'Developer Hub application itself',
        'status': 'active',
    },
    {
        'slug': 'deployment',
        'name': 'Deployment',
        'description': 'Deployment and PythonAnywhere configuration',
        'status': 'active',
    },
    {
        'slug': 'packages',
        'name': 'Packages',
        'description': 'Feature modules and packages',
        'status': 'active',
    },
    {
        'slug': 'documentation',
        'name': 'Documentation',
        'description': 'Documentation and planning',
        'status': 'active',
    },
]


def run_seed():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@devhub.local', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.flush()

    projects = {}
    for proj_data in PROJECTS:
        proj = Project.query.filter_by(slug=proj_data['slug']).first()
        if not proj:
            proj = Project(**proj_data)
            db.session.add(proj)
            db.session.flush()
        projects[proj_data['slug']] = proj

    tag_names = ['api', 'frontend', 'deployment', 'security', 'database', 'testing', 'docs', 'config']
    tags = {}
    for tn in tag_names:
        tag = Tag.query.filter_by(name=tn).first()
        if not tag:
            tag = Tag(name=tn)
            db.session.add(tag)
            db.session.flush()
        tags[tn] = tag

    docs_data = [
        {
            'project': 'workforce-api', 'title': 'API Architecture Overview',
            'summary': 'Overview of the API architecture and design decisions.',
            'doc_type': 'reference', 'status': 'canonical',
            'content': '# API Architecture\n\nThis document describes the workforce API architecture.',
        },
        {
            'project': 'workforce-api', 'title': 'Authentication Flow',
            'summary': 'JWT authentication flow documentation.',
            'doc_type': 'guide', 'status': 'canonical',
            'content': '# Auth Flow\n\nDescribes the JWT-based authentication flow.',
        },
        {
            'project': 'workforce-api', 'title': 'Database Schema',
            'summary': 'Current database schema documentation.',
            'doc_type': 'reference', 'status': 'draft',
            'content': '# Database Schema\n\nSchema documentation here.',
        },
        {
            'project': 'workforce-frontend', 'title': 'Frontend Component Guide',
            'summary': 'Guide to React components used in frontend.',
            'doc_type': 'guide', 'status': 'canonical',
            'content': '# Component Guide\n\nFrontend component documentation.',
        },
        {
            'project': 'workforce-frontend', 'title': 'State Management Patterns',
            'summary': 'Redux/context patterns used in the app.',
            'doc_type': 'reference', 'status': 'stale',
            'content': '# State Management\n\nDocumentation about state management.',
        },
        {
            'project': 'devhub', 'title': 'DevHub Architecture',
            'summary': 'Architecture and design of the Dev Hub.',
            'doc_type': 'reference', 'status': 'canonical',
            'content': '# DevHub Architecture\n\nThis Flask-based tool manages project documentation and progress.',
        },
        {
            'project': 'devhub', 'title': 'Feature Flags Guide',
            'summary': 'Guide to using feature flags in DevHub.',
            'doc_type': 'guide', 'status': 'canonical',
            'content': '# Feature Flags\n\nConfigure via environment variables.',
        },
        {
            'project': 'deployment', 'title': 'PythonAnywhere Setup',
            'summary': 'Steps to deploy on PythonAnywhere.',
            'doc_type': 'guide', 'status': 'canonical',
            'content': '# PythonAnywhere Deployment\n\nStep-by-step deployment guide.',
        },
        {
            'project': 'deployment', 'title': 'Environment Variables',
            'summary': 'All required environment variables.',
            'doc_type': 'reference', 'status': 'canonical',
            'content': '# Environment Variables\n\nSECRET_KEY, DATABASE_URL, etc.',
        },
        {
            'project': 'packages', 'title': 'Package Format Spec',
            'summary': 'Specification for devhub package format.',
            'doc_type': 'reference', 'status': 'canonical',
            'content': '# Package Format\n\nPackages must be .zip files with devhub-package.json manifest.',
        },
        {
            'project': 'documentation', 'title': 'Documentation Standards',
            'summary': 'How to write and maintain docs.',
            'doc_type': 'guide', 'status': 'canonical',
            'content': '# Documentation Standards\n\nAll docs should have title, summary, and status.',
        },
    ]

    for dd in docs_data:
        existing = Document.query.filter_by(title=dd['title']).first()
        if not existing:
            doc = Document(
                project_id=projects[dd['project']].id,
                title=dd['title'],
                summary=dd['summary'],
                content=dd['content'],
                doc_type=dd['doc_type'],
                status=dd['status'],
            )
            db.session.add(doc)

    progress_data = [
        {
            'project': 'workforce-api', 'title': 'Implement user authentication endpoints',
            'status': 'completed',
            'description': 'Created login, logout, and token refresh endpoints.',
            'commands_run': 'pytest tests/test_auth.py',
        },
        {
            'project': 'workforce-api', 'title': 'Add pagination to list endpoints',
            'status': 'in_progress', 'description': 'Adding cursor-based pagination.',
        },
        {
            'project': 'workforce-frontend', 'title': 'Build login page component',
            'status': 'completed', 'description': 'Login page with form validation complete.',
        },
        {
            'project': 'workforce-frontend', 'title': 'Dashboard layout implementation',
            'status': 'in_progress', 'description': 'Working on responsive dashboard.',
        },
        {
            'project': 'devhub', 'title': 'Initial project setup',
            'status': 'completed',
            'description': 'Flask app factory, extensions, blueprints all setup.',
        },
        {
            'project': 'devhub', 'title': 'Package upload feature',
            'status': 'completed',
            'description': 'Zip upload with manifest validation and quarantine.',
        },
        {
            'project': 'devhub', 'title': 'Full-text search',
            'status': 'in_progress', 'description': 'Cross-model search implementation.',
        },
        {
            'project': 'deployment', 'title': 'PythonAnywhere WSGI config',
            'status': 'completed', 'description': 'WSGI file configured and working.',
        },
        {
            'project': 'deployment', 'title': 'Database migration on prod',
            'status': 'planned', 'description': 'Plan migration strategy.',
        },
        {
            'project': 'packages', 'title': 'Package manifest schema v1',
            'status': 'completed', 'description': 'Defined devhub-package.json schema.',
        },
        {
            'project': 'documentation', 'title': 'Write LOCAL_DEVELOPMENT.md',
            'status': 'completed', 'description': 'Complete local dev setup guide written.',
        },
    ]

    for pd in progress_data:
        existing = ProgressEntry.query.filter_by(title=pd['title']).first()
        if not existing:
            entry = ProgressEntry(
                project_id=projects[pd['project']].id,
                user_id=admin.id,
                title=pd['title'],
                description=pd.get('description', ''),
                status=pd['status'],
                commands_run=pd.get('commands_run', ''),
            )
            db.session.add(entry)

    scripts_data = [
        {
            'project': 'workforce-api', 'name': 'Run API Tests',
            'description': 'Execute the full API test suite.',
            'file_path': 'scripts/run_tests.sh', 'risk_level': 'safe',
            'dry_run_command': 'pytest --collect-only',
            'run_command': 'pytest tests/ -v', 'tags': 'testing,api',
        },
        {
            'project': 'workforce-api', 'name': 'Generate API Docs',
            'description': 'Generate OpenAPI documentation.',
            'file_path': 'scripts/gen_docs.sh', 'risk_level': 'safe',
            'run_command': 'python manage.py generate-docs', 'tags': 'docs,api',
        },
        {
            'project': 'workforce-frontend', 'name': 'Build Frontend',
            'description': 'Build the frontend for production.',
            'file_path': 'scripts/build.sh', 'risk_level': 'safe',
            'dry_run_command': 'npm run build -- --dry-run',
            'run_command': 'npm run build', 'tags': 'frontend,build',
        },
        {
            'project': 'devhub', 'name': 'Run DevHub Tests',
            'description': 'Run the pytest test suite for DevHub.',
            'file_path': 'tests/', 'risk_level': 'safe',
            'dry_run_command': 'pytest --collect-only tests/',
            'run_command': 'pytest tests/ -v', 'tags': 'testing',
        },
        {
            'project': 'devhub', 'name': 'Lint Code',
            'description': 'Run ruff linter on source code.',
            'file_path': 'workforce_devhub/', 'risk_level': 'safe',
            'run_command': 'ruff check workforce_devhub/', 'tags': 'linting',
        },
        {
            'project': 'deployment', 'name': 'Deploy to PythonAnywhere',
            'description': 'Pull latest code and reload web app.',
            'file_path': 'scripts/deploy.sh', 'risk_level': 'moderate',
            'dry_run_command': 'git log --oneline -5',
            'run_command': 'git pull && touch /var/www/wsgi.py', 'tags': 'deployment',
        },
        {
            'project': 'packages', 'name': 'Validate Package',
            'description': 'Validate a package zip against the manifest schema.',
            'file_path': 'flask validate-package', 'risk_level': 'safe',
            'run_command': 'flask validate-package <path>', 'tags': 'packages,validation',
        },
    ]

    for sd in scripts_data:
        existing = Script.query.filter_by(name=sd['name']).first()
        if not existing:
            script = Script(
                project_id=projects[sd['project']].id,
                name=sd['name'],
                description=sd.get('description', ''),
                file_path=sd.get('file_path', ''),
                risk_level=sd.get('risk_level', 'safe'),
                dry_run_command=sd.get('dry_run_command', ''),
                run_command=sd.get('run_command', ''),
                tags=sd.get('tags', ''),
            )
            db.session.add(script)

    tracked_files_data = [
        {'project': 'devhub', 'file_path': 'workforce_devhub/__init__.py', 'notes': 'App factory'},
        {'project': 'devhub', 'file_path': 'workforce_devhub/config.py', 'notes': 'Configuration'},
        {'project': 'devhub', 'file_path': 'wsgi.py', 'notes': 'WSGI entry point'},
        {'project': 'deployment', 'file_path': 'requirements.txt', 'notes': 'Python dependencies'},
        {'project': 'deployment', 'file_path': '.env.example', 'notes': 'Environment variable template'},
    ]

    for tfd in tracked_files_data:
        existing = TrackedFile.query.filter_by(file_path=tfd['file_path']).first()
        if not existing:
            tf = TrackedFile(
                project_id=projects[tfd['project']].id,
                file_path=tfd['file_path'],
                notes=tfd.get('notes', ''),
                last_scanned=datetime.utcnow(),
            )
            db.session.add(tf)

    db.session.commit()
    print('Seed data created successfully.')
