from datetime import datetime

from ..extensions import db


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    documents = db.relationship('Document', backref='project', lazy='dynamic')
    progress_entries = db.relationship('ProgressEntry', backref='project', lazy='dynamic')
    scripts = db.relationship('Script', backref='project', lazy='dynamic')
    tracked_files = db.relationship('TrackedFile', backref='project', lazy='dynamic')

    def __repr__(self):
        return f'<Project {self.slug}>'
