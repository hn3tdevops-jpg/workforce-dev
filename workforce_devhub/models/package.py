from datetime import datetime

from ..extensions import db


class Package(db.Model):
    __tablename__ = 'packages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    version = db.Column(db.String(50))
    package_key = db.Column(db.String(200), unique=True)
    description = db.Column(db.Text)
    target_project = db.Column(db.String(100))
    filename = db.Column(db.String(300))
    manifest = db.Column(db.Text)
    status = db.Column(db.String(50), default='quarantined')
    risk_level = db.Column(db.String(50), default='unknown')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    uploader = db.relationship('User', backref='packages')
    audit_logs = db.relationship('PackageAuditLog', backref='package', lazy='dynamic')

    def __repr__(self):
        return f'<Package {self.name}>'


class PackageAuditLog(db.Model):
    __tablename__ = 'package_audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    detail = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='package_audit_logs')

    def __repr__(self):
        return f'<PackageAuditLog {self.action}>'
