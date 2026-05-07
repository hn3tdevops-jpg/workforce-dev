from devhub.models import Document, Package, ProgressEntry, Script, TrackedFile


def search_all(query, limit=50):
    q = f"%{query}%"
    results = {"docs": [], "progress": [], "scripts": [], "packages": [], "files": []}

    docs = Document.query.filter(
        (Document.title.ilike(q)) | (Document.summary.ilike(q)) | (Document.content.ilike(q))
    ).limit(limit).all()
    results["docs"] = [
        {"id": d.id, "title": d.title, "type": "doc", "url": f"/docs/{d.id}"} for d in docs
    ]

    progress = ProgressEntry.query.filter(
        (ProgressEntry.title.ilike(q)) | (ProgressEntry.description.ilike(q))
    ).limit(limit).all()
    results["progress"] = [
        {"id": p.id, "title": p.title, "type": "progress", "url": f"/progress/{p.id}"}
        for p in progress
    ]

    scripts = Script.query.filter(
        (Script.name.ilike(q)) | (Script.description.ilike(q))
    ).limit(limit).all()
    results["scripts"] = [
        {"id": s.id, "title": s.name, "type": "script", "url": f"/scripts/{s.id}"}
        for s in scripts
    ]

    packages = Package.query.filter(
        (Package.name.ilike(q)) | (Package.description.ilike(q))
    ).limit(limit).all()
    results["packages"] = [
        {"id": p.id, "title": p.name, "type": "package", "url": f"/packages/{p.id}"}
        for p in packages
    ]

    files = TrackedFile.query.filter(TrackedFile.file_path.ilike(q)).limit(limit).all()
    results["files"] = [
        {"id": f.id, "title": f.file_path, "type": "file", "url": f"/files/{f.id}"}
        for f in files
    ]

    return results
