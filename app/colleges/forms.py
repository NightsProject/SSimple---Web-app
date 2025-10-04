from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, Regexp


def validate_college_code_uniqueness(form, field):
    from .models import Colleges
    existing = Colleges.get_by_code(field.data)
    if existing:
        raise ValidationError('College code already exists.')

class CollegeForm(FlaskForm):
    code = StringField("College Code", validators=[
        DataRequired(),
        Length(max=10),
        Regexp(r'^[a-zA-Z0-9]+$', message="College code must contain only alphanumeric characters."),
        validate_college_code_uniqueness
    ])
    name = StringField("College Name", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Save College")
