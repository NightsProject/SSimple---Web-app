from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional, ValidationError, Regexp


def validate_program_code_uniqueness(form, field):
    from .models import Programs
    existing = Programs.get_by_code(field.data)
    if existing:
        raise ValidationError('Program code already exists.')

class ProgramForm(FlaskForm):
    code = StringField("Program Code", validators=[
        DataRequired(),
        Length(max=20),
        Regexp(r'^[a-zA-Z0-9]+$', message="Program code must contain only alphanumeric characters."),
        validate_program_code_uniqueness
    ])
    name = StringField("Program Name", validators=[DataRequired(), Length(max=100)])

    # will be populated by the controller with available colleges
    # require selection (do not allow empty/None)
    college_code = SelectField("College Code", choices=[], validators=[DataRequired()])
    submit = SubmitField("Save Program")
