

from flask import jsonify, render_template
from . import agents

@agents.route('/')
def index():
    return render_template('agents/index.html')

@agents.route('/<int:agent_id>')
@agents.route('/<int:agent_id>/')
def details(agent_id):
    return str(agent_id)