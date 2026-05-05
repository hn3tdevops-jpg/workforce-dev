from ..extensions import db


class TrackedFile(db.Model):
    __tablename__ = 'tracked_files'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    file_path = db.Column(db.String(1000), nullable=False)
    last_scanned = db.Column(db.DateTime)
    file_size = db.Column(db.Integer)
    last_modified = db.Column(db.DateTime)
    checksum = db.Column(db.String(64))
    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<TrackedFile {self.file_path}>'
