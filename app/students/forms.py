from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp


class StudentForm(FlaskForm):
    id_number = StringField("ID Number", validators=[DataRequired(), Length(max=20)])
    
    # Year prefix used for the ID (format YEAR-XXXX). Default is set in controller to current year.
    id_year = StringField("ID Year", validators=[DataRequired(), Length(min=4, max=4)])
    first_name = StringField("First Name", validators=[
        DataRequired(),
        Length(max=50),
        #Regexp(r'^[a-zA-Z\s]+$', message="First name must contain only letters and spaces, no numbers.")
    ])
    last_name = StringField("Last Name", validators=[
        DataRequired(),
        Length(max=50),
        #Regexp(r'^[a-zA-Z\s]+$', message="Last name must contain only letters and spaces, no numbers.")
    ])

    program_code = SelectField("Program", choices=[], validators=[DataRequired()])
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
    submit = SubmitField("Save Student")