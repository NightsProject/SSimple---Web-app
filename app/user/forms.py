from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

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
    submit = SubmitField("Submit")