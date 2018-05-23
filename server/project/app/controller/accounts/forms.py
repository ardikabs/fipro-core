

from flask import url_for
from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.fields import (
    BooleanField,
    PasswordField,
    StringField,
    SubmitField
)

from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length


from app.models import User

class LoginForm(FlaskForm):
    email = EmailField(
        'Email', validators= [InputRequired(),
                              Length(1,64),
                              Email()])
    
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')