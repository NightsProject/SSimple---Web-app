from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional


class ProgramForm(FlaskForm):
    code = StringField("Program Code", validators=[DataRequired(), Length(max=20)])
    name = StringField("Program Name", validators=[DataRequired(), Length(max=100)])
    
    # will be populated by the controller with available colleges
    # require selection (do not allow empty/None)
    college_code = SelectField("College Code", choices=[], validators=[DataRequired()])
    submit = SubmitField("Save Program")
