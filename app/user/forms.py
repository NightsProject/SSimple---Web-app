from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

class LoginForm(FlaskForm):
    """Simple login form."""
    username = StringField(
        'Username',
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter your username"}
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter your password"}
    )
    remember_me = BooleanField('Remember Me')
    submit = SubmitField("Log in")
class RegistrationForm(FlaskForm):
    """Simple registration form for the 'New' button."""
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=4, max=25)],
        render_kw={"placeholder": "Choose a username"}
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Enter a valid email address"}
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()],
        render_kw={"placeholder": "Choose a password"}
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')],
        render_kw={"placeholder": "Confirm your password"}
    )
    profile_picture = FileField(
        'Profile Picture',
        validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!'), Optional()]
    )
    submit = SubmitField("Submit")

class SettingsForm(FlaskForm):
    """Form for user settings."""
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=4, max=25)],
        render_kw={"placeholder": "Enter username"}
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Enter email"}
    )
    fullname = StringField(
        'Full Name',
        validators=[Optional(), Length(max=150)],
        render_kw={"placeholder": "Enter full name"}
    )
    address = TextAreaField(
        'Address',
        validators=[Optional(), Length(max=200)],
        render_kw={"placeholder": "Enter address"}
    )
    birthday = DateField(
        'Birthday',
        validators=[Optional()],
        render_kw={"placeholder": "YYYY-MM-DD"}
    )
    profile_picture = FileField(
        'Profile Picture',
        validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!'), Optional()]
    )
    current_password = PasswordField(
        'Current Password',
        validators=[Optional()],
        render_kw={"placeholder": "Enter current password to change password"}
    )
    new_password = PasswordField(
        'New Password',
        validators=[Optional(), Length(min=6)],
        render_kw={"placeholder": "Enter new password"}
    )
    confirm_new_password = PasswordField(
        'Confirm New Password',
        validators=[Optional(), EqualTo('new_password', message='Passwords must match')],
        render_kw={"placeholder": "Confirm new password"}
    )
    submit = SubmitField("Save Changes")
