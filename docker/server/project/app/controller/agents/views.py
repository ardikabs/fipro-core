import requests
from multiprocessing.dummy import Pool as ThreadPool

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
from app.models import ApiKey, Agents, User, Sensor, OldAgents
from . import agents


def model_update(model):
    return model.update()

@agents.route('/', methods=['GET','POST'])
@login_required
def index():
    title = "Agents"
    if request.form.get('_operation'):
        operation = request.form.get('_operation')
        id = request.form.get('id')
        agent = Agents.query.filter_by(id=id, user_id= current_user.id).first()
        
        if operation == 'DESTROY':
            _ = [sensor.destroy() for sensor in agent.sensor]
            agent.destroy()
            msg = ("Success!", "Destroy agent {0} with {1} sensor".format(agent.name, agent.sensor.count()))
            flash(msg,"alert-warning")
        
        elif operation == 'DELETE':
            # Removed Agent
            db.session.delete(agent)

            # Archieved removed agent
            removed_agent = OldAgents(**agent.to_archieved())
            db.session.add(removed_agent)
            db.session.commit()
            msg = ("Success!", "Agent {0} has been deleted".format(agent.name))
            flash(msg,"alert-success")
        
        else:
            try:
                url = "http://{0}:5000/api/v1/sensor/{1}/{2}".format(agent.ipaddr, agent.string_id, operation.lower())
                req = requests.get(url, timeout=10)
                resp = req.json()

                if resp.get('status'):
                    msg = ("Success!", "Agent {0} on {1}".format(agent.show_info(), operation.capitalize()))
                    flash(msg,"alert-success")
                else:
                    msg = ("Failed!", "Agent {0} failed to {1}".format(agent.show_info(), operation.capitalize()))
                    flash(msg,"alert-danger")
            except:
                msg = ("Failed!", "Agent {0} failed to {1}".format(agent.show_info(), operation.capitalize()))
                flash(msg,"alert-danger")

            

        
        return redirect(url_for('agents.index'))


    pool = ThreadPool(4)
    agents = pool.map(model_update, Agents.query.filter_by(user_id= current_user.id).all())
    pool.close()
    pool.join()

    db.session.commit()
    return render_template('agents/index.html', title=title, agents=agents)

@agents.route('/<int:agent_id>')
@agents.route('/<int:agent_id>/')
@login_required
def details(agent_id):
    return str(agent_id)

