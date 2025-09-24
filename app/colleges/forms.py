from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class CollegeForm(FlaskForm):
    code = StringField("College Code", validators=[DataRequired(), Length(max=10)])
    name = StringField("College Name", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Save College")