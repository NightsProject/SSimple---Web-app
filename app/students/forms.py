from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError, Optional
from config import MAX_FILE_SIZE


def validate_program_code(form, field):
    from ..programs.models import Programs
    if not Programs.get_by_code(field.data):
        raise ValidationError('Selected program does not exist.')


def validate_file_size(form, field):
    """Custom validator to check file size limit."""
    if field.data:
        # Get file size limit from environment or use default (3MB)
        max_file_size = MAX_FILE_SIZE 
        
        # Get file size in bytes
        field.data.seek(0, 2)  # Seek to end of file
        file_size = field.data.tell()  # Get current position (file size)
        field.data.seek(0)  # Reset file pointer to beginning
        
        # Check if file size exceeds limit
        if file_size > max_file_size:
            max_size_mb = max_file_size / (1024 * 1024)
            raise ValidationError(f'File size too large. Maximum allowed size is {max_size_mb:.1f}MB.')

class StudentForm(FlaskForm):
    id_number = StringField("ID Number", validators=[
        DataRequired(),
        Length(max=20),
        Regexp(r'^\d{4}-\d{4}$', message="ID Number must be in the format YYYY-XXXX.")
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
        FileAllowed(['png', 'jpg', 'jpeg', 'gif'], 'Images only!'),
        validate_file_size
    ])
