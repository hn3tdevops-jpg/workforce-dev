from datetime import datetime

from ..extensions import db


class Script(db.Model):
    __tablename__ = 'scripts'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    risk_level = db.Column(db.String(50), default='safe')
    parameters_schema = db.Column(db.Text)
    dry_run_command = db.Column(db.String(500))
    run_command = db.Column(db.String(500))
    last_run_at = db.Column(db.DateTime)
    last_run_status = db.Column(db.String(50))
    tags = db.Column(db.String(500))
    owner = db.Column(db.String(100))
    notes = db.Column(db.Text)

    run_logs = db.relationship('ScriptRunLog', backref='script', lazy='dynamic')

    def __repr__(self):
        return f'<Script {self.name}>'


class ScriptRunLog(db.Model):
    __tablename__ = 'script_run_logs'
    id = db.Column(db.Integer, primary_key=True)
    script_id = db.Column(db.Integer, db.ForeignKey('scripts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    command = db.Column(db.String(500))
    output = db.Column(db.Text)
    status = db.Column(db.String(50))
    ran_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='script_run_logs')

    def __repr__(self):
        return f'<ScriptRunLog {self.id}>'
