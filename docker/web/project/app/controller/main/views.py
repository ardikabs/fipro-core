

from flask import jsonify, render_template, abort
from . import main
from flask_login import(
    current_user,
    login_required,
    login_user,
    logout_user
)

from app.models import ApiKey

@main.route('/')
@login_required
def index():
    # api = ApiKey.query.filter_by(user_id=current_user.id).first()
    # return render_template('main/index.html',api_key=api.api_key)
    return render_template('main/index.html')