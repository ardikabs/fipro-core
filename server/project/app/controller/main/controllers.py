

from flask import jsonify, render_template, abort
from . import main
from flask_login import(
    current_user,
    login_required,
    login_user,
    logout_user
)

@main.route('/')
@login_required
def index():
    return render_template('main/index.html')