import pytest
from devhub.models import User, Project, Doc, ProgressReport, Script, Package, FileRecord, AuditLog
from devhub.extensions import bcrypt

def test_user_creation(db):
    hashed = bcrypt.generate_password_hash('pass').decode('utf-8')
    u = User(username='u1', email='u1@test.com', password_hash=hashed)
    db.session.add(u)
    db.session.commit()
    assert u.id is not None
    assert u.is_active is True
    assert u.is_admin is False

def test_project_creation(db, admin_user):
    p = Project(name='Test', slug='test-proj', owner_id=admin_user.id)
    db.session.add(p)
    db.session.commit()
    assert p.id is not None
    assert p.status == 'active'

def test_doc_creation(db, admin_user):
    d = Doc(title='T', slug='t', content='Body', author_id=admin_user.id)
    db.session.add(d)
    db.session.commit()
    assert d.id is not None

def test_progress_report_creation(db, admin_user):
    p = Project(name='P', slug='p-slug', owner_id=admin_user.id)
    db.session.add(p)
    db.session.flush()
    r = ProgressReport(title='R', project_id=p.id, author_id=admin_user.id)
    db.session.add(r)
    db.session.commit()
    assert r.status == 'draft'

def test_script_creation(db, admin_user):
    s = Script(name='S', slug='s-slug', content='print(1)', author_id=admin_user.id)
    db.session.add(s)
    db.session.commit()
    assert s.language == 'python'

def test_file_record_creation(db):
    fr = FileRecord(filepath='/a/b.txt', filename='b.txt', size_bytes=100)
    db.session.add(fr)
    db.session.commit()
    assert fr.scan_status == 'ok'

def test_audit_log_creation(db):
    log = AuditLog(action='test_action', resource_type='test')
    db.session.add(log)
    db.session.commit()
    assert log.id is not None

def test_user_relationships(db, admin_user):
    p = Project(name='RP', slug='rp-slug', owner_id=admin_user.id)
    db.session.add(p)
    db.session.commit()
    assert len(admin_user.projects) == 1
