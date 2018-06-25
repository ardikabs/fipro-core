import requests
from flask import (
    current_app, 
    jsonify, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash
)
from flask_login import (
    current_user,
    login_required
)
from app import db, csrf
from app.models import ApiKey, Agents, User, Sensor
from . import agents

@agents.route('/', methods=['GET','POST'])
def index():

    if request.form.get('_method') == "DELETE" :
        id = request.form.get('id')
        agent = Agents.query.filter_by(id=id, user_id= current_user.id).first()
        
        _ = [sensor.destroy() for sensor in agent.sensor]
        db.session.delete(agent)
        db.session.commit()

        msg = "Successfully deleted agent {0} and {1} sensor".format(agent.name, agent.sensor.count())
        flash(msg,"alert-warning")
        return redirect(url_for('agents.index'))


    query_set = Agents.query.filter_by(user_id= current_user.id).all()
    agents_list = [ agent.update() for agent in query_set ]

    return render_template('agents/index.html', agents=agents_list)

@agents.route('/<int:agent_id>')
@agents.route('/<int:agent_id>/')
def details(agent_id):
    return str(agent_id)