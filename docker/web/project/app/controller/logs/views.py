

from flask import jsonify, render_template
from . import logs

@logs.route('/')
def index():
    return render_template('logs/index.html')