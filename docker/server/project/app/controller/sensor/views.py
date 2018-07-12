
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
from app.models import ApiKey, Agents, User, Sensor
from . import sensor
from .forms import SensorForm

def model_update(model):
    return model.update()

@sensor.route('/', methods=['GET','POST'])
@login_required
def index():
    form = SensorForm()
    title = "Sensor"
    
    if request.form.get('_operation'):
        operation = request.form.get('_operation')
        sensor = Sensor.query.filter_by(id= request.form.get('id')).first()
        
        if operation == 'DELETE':
            msg = ("Success!", "Sensor {0} in agent {1} has been deleted".format(sensor.name, sensor.agent.show_info()))
            flash(msg,"alert-success")

            db.session.delete(sensor)
            db.session.commit()
            
        
        else:
            url = "http://{0}:5000/api/v1/sensor/{1}/{2}".format(sensor.agent.ipaddr, sensor.string_id, operation.lower())
            req = requests.get(url)
            resp = req.json()

            if resp.get('status'):
                msg = ("Success!", "Sensor {0} in agent {1} on {2}".format(sensor.name, sensor.agent.show_info(), operation.capitalize()))
                flash(msg,"alert-success")
            else:
                msg = ("Failed!", "Sensor {0} in agent {1} failed to {2}".format(sensor.name, sensor.agent.show_info(), operation.capitalize()))
                flash(msg,"alert-warning")

        return redirect(url_for('sensor.index'))

    if request.method == 'POST':
        sensor_name = form.name.data
        sensor_type = form.type.data
        agent_id = form.agent.data
        
        # Memperbarui Informasi Agent di database
        agent = Agents.query.filter_by(id=agent_id).first()
        agent.update()
        db.session.commit()

        sensor_check = Sensor.query.filter_by(user_id=current_user.id, agent_id= agent_id, type= sensor_type).first()
        if sensor_check and sensor_check.condition_id != 1 :
            msg = ("Failed!", "Sensor {0} in Agent {1} already exists".format(sensor_type.capitalize(), agent.show_info()))
            flash(msg,"alert-warning")
            return redirect(url_for('sensor.index'))
        
        else:
            
            if agent.condition_id == 4:
                sensor = Sensor(
                    name= sensor_name,
                    type= sensor_type,
                    agent_id= agent_id,
                    user_id= current_user.id
                )
                url = 'http://{}:5000/api/v1/sensor/'.format(agent.ipaddr)
                payload = {
                    'sensor_type': sensor_type,
                    'sensor_image': "ardikabs/{}".format(sensor_type)
                }
                req = requests.post(url, json=payload)
                resp = req.json()
                
                if resp.get('status', False):
                    sensor.container_id = resp.get('sensor').get('id')
                    sensor.string_id = resp.get('sensor').get('short_id')
                    sensor.status = resp.get('sensor').get('status')
                    db.session.add(sensor)
                    msg = ("Success!", "Added Sensor {0} in Agent {1}".format(sensor_name, agent.show_info()))
                    flash(msg,'alert-success')
                    return redirect(url_for('sensor.index'))
                
                msg = ("Failed!", "There is problem on deployment Sensor {0} in Agent {1}".format(sensor_type.capitalize(), agent.show_info()))
                flash(msg, 'alert-danger')
                return redirect(url_for('sensor.index'))
            
            else:
                msg = ("Failed!", "There is problem on Agent {}".format(agent.show_info()))
                flash(msg, 'alert-danger')
                return redirect(url_for('sensor.index'))

    agents = Agents.query.filter_by(user_id= current_user.id, condition_id=4).all()

    pool = ThreadPool(4)
    sensors = pool.map(model_update, Sensor.query.filter_by(user_id= current_user.id).all())
    pool.close()
    pool.join()

    db.session.commit()
    form.type.choices = (('Low-Interaction Honeypot', (('dionaea', 'Dionaea'),('glastopf', 'Glastopf'),)), ('Medium-Interaction Honeypot', (('cowrie', 'Cowrie'),)))
    form.agent.choices = [(agent.id, agent.show_info()) for agent in agents]
    
    return render_template(
        'sensor/index.html',
        title = title,
        agents = agents,
        sensors = sensors,
        form = form)


@sensor.route('/<int:sensor_id>')
@login_required
def details(sensor_id):
    return redirect(url_for('main.index'))


