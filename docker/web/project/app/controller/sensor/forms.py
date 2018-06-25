

from flask import url_for
from flask_wtf import FlaskForm
from wtforms import ValidationError,validators
from wtforms.fields import (
    StringField,
    SelectField,
    SubmitField
)
from wtforms.fields.html5 import (
    DateField
)

from wtforms.validators import EqualTo, InputRequired, Length
from app.utils import SelectField as CustomSelectField, ButtonField

class SensorForm(FlaskForm):

    name = StringField('name', validators=[InputRequired(), Length(4,32)])
    type = CustomSelectField('type')
    agent = SelectField('agent')
    submit = SubmitField('ADD')
    cancel = ButtonField('CANCEL')


