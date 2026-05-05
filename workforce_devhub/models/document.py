from datetime import datetime

from ..extensions import db

document_tags = db.Table(
    'document_tags',
    db.Column('document_id', db.Integer, db.ForeignKey('documents.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Tag {self.name}>'


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    title = db.Column(db.String(300), nullable=False)
    summary = db.Column(db.Text)
    content = db.Column(db.Text)
    doc_type = db.Column(db.String(50), default='general')
    status = db.Column(db.String(50), default='draft')
    file_path = db.Column(db.String(500))
    external_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tags = db.relationship(
        'Tag',
        secondary=document_tags,
        lazy='subquery',
        backref=db.backref('documents', lazy=True),
    )

    def __repr__(self):
        return f'<Document {self.title}>'
