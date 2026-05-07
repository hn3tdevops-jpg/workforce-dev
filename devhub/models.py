from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from devhub.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default="active")
    repo_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    docs = db.relationship("Document", back_populates="project", lazy="dynamic")
    progress_entries = db.relationship("ProgressEntry", back_populates="project", lazy="dynamic")
    scripts = db.relationship("Script", back_populates="project", lazy="dynamic")


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


document_tags = db.Table(
    "document_tags",
    db.Column("document_id", db.Integer, db.ForeignKey("documents.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id")),
)

progress_tags = db.Table(
    "progress_tags",
    db.Column("progress_id", db.Integer, db.ForeignKey("progress_entries.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id")),
)

script_tags = db.Table(
    "script_tags",
    db.Column("script_id", db.Integer, db.ForeignKey("scripts.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id")),
)


class Document(db.Model):
    __tablename__ = "documents"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    summary = db.Column(db.Text)
    content = db.Column(db.Text)
    doc_type = db.Column(db.String(50), default="markdown")
    status = db.Column(db.String(50), default="draft")
    external_url = db.Column(db.String(500))
    file_path = db.Column(db.String(500))
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = db.relationship("Project", back_populates="docs")
    tags = db.relationship("Tag", secondary=document_tags, backref="documents")


class ProgressEntry(db.Model):
    __tablename__ = "progress_entries"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default="in-progress")
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    evidence_links = db.Column(db.Text)
    file_paths = db.Column(db.Text)
    commands_run = db.Column(db.Text)
    test_results = db.Column(db.Text)
    notes = db.Column(db.Text)
    entry_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = db.relationship("Project", back_populates="progress_entries")
    tags = db.relationship("Tag", secondary=progress_tags, backref="progress_entries")


class Script(db.Model):
    __tablename__ = "scripts"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    file_path = db.Column(db.String(500))
    risk_level = db.Column(db.String(20), default="safe")
    dry_run_command = db.Column(db.String(1000))
    normal_command = db.Column(db.String(1000))
    parameters_schema = db.Column(db.Text)
    owner = db.Column(db.String(255))
    notes = db.Column(db.Text)
    last_run_status = db.Column(db.String(50))
    last_run_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship("Project", back_populates="scripts")
    tags = db.relationship("Tag", secondary=script_tags, backref="scripts")
    run_logs = db.relationship("ScriptRunLog", back_populates="script", lazy="dynamic")


class ScriptRunLog(db.Model):
    __tablename__ = "script_run_logs"
    id = db.Column(db.Integer, primary_key=True)
    script_id = db.Column(db.Integer, db.ForeignKey("scripts.id"))
    command_run = db.Column(db.String(1000))
    exit_code = db.Column(db.Integer)
    stdout = db.Column(db.Text)
    stderr = db.Column(db.Text)
    dry_run = db.Column(db.Boolean, default=True)
    run_at = db.Column(db.DateTime, default=datetime.utcnow)
    run_by = db.Column(db.String(255))

    script = db.relationship("Script", back_populates="run_logs")


class Package(db.Model):
    __tablename__ = "packages"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(500), nullable=False)
    quarantine_path = db.Column(db.String(500))
    package_key = db.Column(db.String(255))
    name = db.Column(db.String(255))
    version = db.Column(db.String(50))
    description = db.Column(db.Text)
    target_project = db.Column(db.String(255))
    manifest_valid = db.Column(db.Boolean, default=False)
    manifest_data = db.Column(db.Text)
    risk_level = db.Column(db.String(20), default="safe")
    requires_manual_review = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(50), default="quarantined")
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.String(255))
    install_log = db.Column(db.Text)


class TrackedFile(db.Model):
    __tablename__ = "tracked_files"
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(1000), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    file_type = db.Column(db.String(50))
    last_modified = db.Column(db.DateTime)
    sha256_hash = db.Column(db.String(64))
    size_bytes = db.Column(db.Integer)
    status = db.Column(db.String(50), default="present")
    notes = db.Column(db.Text)
    is_important = db.Column(db.Boolean, default=False)
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_scanned = db.Column(db.DateTime)

    project = db.relationship("Project")


class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(100))
    resource_id = db.Column(db.Integer)
    user_email = db.Column(db.String(255))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
