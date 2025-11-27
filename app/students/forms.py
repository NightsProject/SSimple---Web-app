from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError, Optional


def validate_program_code(form, field):
    from ..programs.models import Programs
    if not Programs.get_by_code(field.data):
        raise ValidationError('Selected program does not exist.')

class StudentForm(FlaskForm):
    id_number = StringField("ID Number", validators=[
        DataRequired(),
        Length(max=20),
        Regexp(r'^\d{4}-\d{4}$', message="ID Number must be in the format YYYY-XXXX.")
    ])

    # Year prefix used for the ID (format YEAR-XXXX). Default is set in controller to current year.
    id_year = StringField("ID Year", validators=[
        DataRequired(),
        Length(min=4, max=4),
        Regexp(r'^\d{4}$', message="ID Year must be exactly 4 digits.")
    ])
    first_name = StringField("First Name", validators=[
        DataRequired(),
        Length(max=50),
        Regexp(r'^[a-zA-Z\s]+$', message="First name must contain only letters and spaces, no numbers.")
    ])
    last_name = StringField("Last Name", validators=[
        DataRequired(),
        Length(max=50),
        Regexp(r'^[a-zA-Z\s]+$', message="Last name must contain only letters and spaces, no numbers.")
    ])

    program_code = SelectField("Program", choices=[], validators=[DataRequired(), validate_program_code])
    year = SelectField("Year Level", choices=[
        ('1st Year', '1st Year'),
        ('2nd Year', '2nd Year'),
        ('3rd Year', '3rd Year'),
        ('4th Year', '4th Year'),
        ('5th Year', '5th Year'),
    ], validators=[DataRequired()])
    gender = SelectField("Gender", choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    profile_picture = FileField("Profile Picture", validators=[
        Optional(),
        FileAllowed(['png', 'jpg', 'jpeg', 'gif'], 'Images only!')
    ])
    submit = SubmitField("Save Student")
