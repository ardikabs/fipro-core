

from flask import jsonify, render_template
from . import agents

@agents.route('/')
def index():
    return render_template('agents/index.html')