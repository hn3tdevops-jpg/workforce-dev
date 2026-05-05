from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class ProgressEntryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 300)])
    description = TextAreaField('Description', validators=[Optional()])
    status = SelectField(
        'Status',
        choices=[
            ('planned', 'Planned'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('blocked', 'Blocked'),
        ],
    )
    project_id = SelectField('Project', coerce=int, validators=[Optional()])
    evidence_links = TextAreaField('Evidence Links (one per line)', validators=[Optional()])
    file_paths = TextAreaField('File Paths (one per line)', validators=[Optional()])
    commands_run = TextAreaField('Commands Run', validators=[Optional()])
    test_results = TextAreaField('Test Results', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Entry')
