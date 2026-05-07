from devhub.extensions import db
from devhub.models import Document, ProgressEntry, Project, Script, Tag


def seed_data():
    projects_data = [
        {
            "name": "Workforce API",
            "slug": "workforce-api",
            "description": "Backend REST API for the Workforce system",
            "status": "active",
        },
        {
            "name": "Workforce Frontend Console",
            "slug": "workforce-frontend",
            "description": "Frontend console for Workforce management",
            "status": "active",
        },
        {
            "name": "Workforce Dev Hub",
            "slug": "workforce-devhub",
            "description": "Developer hub and tooling platform",
            "status": "active",
        },
        {
            "name": "PythonAnywhere Deployment",
            "slug": "pythonanywhere",
            "description": "Deployment infrastructure and docs for PythonAnywhere",
            "status": "active",
        },
        {
            "name": "Feature Packages",
            "slug": "feature-packages",
            "description": "Developer feature packages and modules",
            "status": "active",
        },
        {
            "name": "Documentation",
            "slug": "documentation",
            "description": "Project documentation and planning",
            "status": "active",
        },
    ]
    for pd in projects_data:
        if not Project.query.filter_by(slug=pd["slug"]).first():
            db.session.add(Project(**pd))
    db.session.flush()

    projects = {pd["slug"]: Project.query.filter_by(slug=pd["slug"]).first() for pd in projects_data}

    tag_names = ["api", "frontend", "deployment", "docs", "testing", "devhub", "packages", "security"]
    for tn in tag_names:
        if not Tag.query.filter_by(name=tn).first():
            db.session.add(Tag(name=tn))
    db.session.flush()

    tags = {tn: Tag.query.filter_by(name=tn).first() for tn in tag_names}

    docs_data = [
        {
            "title": "Workforce Master Plan",
            "summary": "Overall architecture and goals for the Workforce system",
            "content": "# Workforce Master Plan\n\nThis document describes the overall architecture and goals...",
            "doc_type": "markdown",
            "status": "canonical",
            "project_slug": "documentation",
            "tags": ["docs"],
        },
        {
            "title": "API Progress Report",
            "summary": "Current state of the Workforce API development",
            "content": "# API Progress Report\n\nThis report tracks the progress of the Workforce API...",
            "doc_type": "markdown",
            "status": "draft",
            "project_slug": "workforce-api",
            "tags": ["api", "docs"],
        },
        {
            "title": "Frontend Progress Report",
            "summary": "Current state of the frontend console development",
            "content": "# Frontend Progress Report\n\nThis report tracks the progress of the frontend console...",
            "doc_type": "markdown",
            "status": "draft",
            "project_slug": "workforce-frontend",
            "tags": ["frontend", "docs"],
        },
        {
            "title": "PythonAnywhere Deployment Notes",
            "summary": "Notes for deploying to PythonAnywhere",
            "content": "# PythonAnywhere Deployment Notes\n\nSee docs/PYTHONANYWHERE_DEPLOYMENT.md for full instructions...",
            "doc_type": "markdown",
            "status": "canonical",
            "project_slug": "pythonanywhere",
            "tags": ["deployment", "docs"],
        },
        {
            "title": "Package Manifest Spec",
            "summary": "Specification for devhub-package.json manifest files",
            "content": "# Package Manifest Spec\n\nSee docs/PACKAGE_MANIFEST_SPEC.md for full specification...",
            "doc_type": "markdown",
            "status": "canonical",
            "project_slug": "feature-packages",
            "tags": ["packages", "docs"],
        },
        {
            "title": "Script Library Spec",
            "summary": "Specification and security rules for the script library",
            "content": "# Script Library Spec\n\nSee docs/SCRIPT_LIBRARY_SPEC.md for full specification...",
            "doc_type": "markdown",
            "status": "canonical",
            "project_slug": "workforce-devhub",
            "tags": ["security", "docs"],
        },
    ]
    for dd in docs_data:
        if not Document.query.filter_by(title=dd["title"]).first():
            doc = Document(
                title=dd["title"],
                summary=dd["summary"],
                content=dd["content"],
                doc_type=dd["doc_type"],
                status=dd["status"],
                project_id=projects[dd["project_slug"]].id,
            )
            for tn in dd.get("tags", []):
                if tn in tags:
                    doc.tags.append(tags[tn])
            db.session.add(doc)

    scripts_data = [
        {
            "name": "Run Backend Tests",
            "description": "Run the Workforce API test suite",
            "project_slug": "workforce-api",
            "risk_level": "safe",
            "dry_run_command": "pytest tests/ --collect-only",
            "normal_command": "pytest tests/ -v",
            "tags": ["api", "testing"],
        },
        {
            "name": "Frontend Build",
            "description": "Build the frontend console assets",
            "project_slug": "workforce-frontend",
            "risk_level": "safe",
            "dry_run_command": "npm run build --dry-run",
            "normal_command": "npm run build",
            "tags": ["frontend"],
        },
        {
            "name": "Alembic Upgrade",
            "description": "Run database migrations",
            "project_slug": "workforce-api",
            "risk_level": "moderate",
            "dry_run_command": "flask db upgrade --sql",
            "normal_command": "flask db upgrade",
            "tags": ["api", "deployment"],
        },
        {
            "name": "Dev Hub Scan",
            "description": "Scan workspace and update file index",
            "project_slug": "workforce-devhub",
            "risk_level": "safe",
            "dry_run_command": "python -m devhub scan --dry-run",
            "normal_command": "python -m devhub scan",
            "tags": ["devhub"],
        },
        {
            "name": "PythonAnywhere Log Check",
            "description": "Check PythonAnywhere error logs (placeholder)",
            "project_slug": "pythonanywhere",
            "risk_level": "safe",
            "dry_run_command": "cat /var/log/error.log | tail -100",
            "normal_command": "cat /var/log/error.log | tail -100",
            "tags": ["deployment"],
        },
        {
            "name": "Validate Package",
            "description": "Validate a package zip file",
            "project_slug": "feature-packages",
            "risk_level": "safe",
            "dry_run_command": "python -m devhub validate-package path/to/package.zip",
            "normal_command": "python -m devhub validate-package path/to/package.zip",
            "tags": ["packages", "security"],
        },
    ]
    for sd in scripts_data:
        if not Script.query.filter_by(name=sd["name"]).first():
            script = Script(
                name=sd["name"],
                description=sd["description"],
                project_id=projects[sd["project_slug"]].id,
                risk_level=sd["risk_level"],
                dry_run_command=sd["dry_run_command"],
                normal_command=sd["normal_command"],
            )
            for tn in sd.get("tags", []):
                if tn in tags:
                    script.tags.append(tags[tn])
            db.session.add(script)

    progress_data = [
        {
            "title": "Initial Dev Hub rebuild started",
            "description": "Began fresh rebuild of the Workforce Dev Hub from GitHub-first architecture.",
            "status": "completed",
            "project_slug": "workforce-devhub",
            "tags": ["devhub"],
        },
        {
            "title": "GitHub-first architecture selected",
            "description": "Decided to build and version the dev hub entirely in GitHub before any PythonAnywhere deployment.",
            "status": "completed",
            "project_slug": "workforce-devhub",
            "tags": ["devhub", "deployment"],
        },
        {
            "title": "PythonAnywhere deployment target documented",
            "description": "Created deployment docs explaining how to deploy from GitHub to PythonAnywhere.",
            "status": "completed",
            "project_slug": "pythonanywhere",
            "tags": ["deployment", "docs"],
        },
    ]
    for pd in progress_data:
        if not ProgressEntry.query.filter_by(title=pd["title"]).first():
            entry = ProgressEntry(
                title=pd["title"],
                description=pd["description"],
                status=pd["status"],
                project_id=projects[pd["project_slug"]].id,
            )
            for tn in pd.get("tags", []):
                if tn in tags:
                    entry.tags.append(tags[tn])
            db.session.add(entry)

    db.session.commit()
    return True
