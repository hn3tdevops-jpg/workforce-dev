from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import URL, DataRequired, Length, Optional


class DocumentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 300)])
    summary = TextAreaField('Summary', validators=[Optional()])
    content = TextAreaField('Content', validators=[Optional()])
    doc_type = SelectField(
        'Type',
        choices=[
            ('general', 'General'),
            ('api', 'API'),
            ('guide', 'Guide'),
            ('reference', 'Reference'),
            ('planning', 'Planning'),
            ('meeting', 'Meeting'),
        ],
    )
    status = SelectField(
        'Status',
        choices=[
            ('draft', 'Draft'),
            ('canonical', 'Canonical'),
            ('stale', 'Stale'),
            ('archived', 'Archived'),
        ],
    )
    project_id = SelectField('Project', coerce=int, validators=[Optional()])
    external_url = StringField('External URL', validators=[Optional(), URL()])
    tags = StringField('Tags (comma-separated)', validators=[Optional()])
    submit = SubmitField('Save Document')


class UploadDocForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 300)])
    doc_file = FileField(
        'Document File',
        validators=[FileAllowed(['md', 'txt', 'html'], 'Only .md, .txt, .html files allowed')],
    )
    project_id = SelectField('Project', coerce=int, validators=[Optional()])
    submit = SubmitField('Upload')
