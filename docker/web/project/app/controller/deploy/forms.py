

from flask import url_for
from flask_wtf import FlaskForm
from wtforms import ValidationError,validators
from wtforms.fields import (
    StringField,
    BooleanField, 
    TextField, 
    TextAreaField, 
    PasswordField, 
    HiddenField, 
    DateTimeField, 
    SelectField,
    IntegerField,
    SubmitField
)
from wtforms.fields.html5 import (
    DateField
)

from wtforms.validators import EqualTo, InputRequired, Length


class AddDeployKeyForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(), Length(4,32)])
    expired_date = DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ")
    submit_add_key = SubmitField('ADD')

class EditDeployKeyForm(FlaskForm):
    id = IntegerField()
    name = StringField(validators=[InputRequired(), Length(4,32)])
    expired_date = DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ")
    submid_edit_key = SubmitField('EDIT')

class DeleteDeployKeyForm(FlaskForm):
    id = IntegerField()