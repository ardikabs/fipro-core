
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
from . import sensor
from .forms import SensorForm

@sensor.route('/', methods=['GET','POST'])
def index():
    form = SensorForm()
    
    if request.form.get('_operation'):
        operation = request.form.get('_operation')
        sensor = Sensor.query.filter_by(id= request.form.get('id')).first()

        url = "http://{0}:5000/api/v1/sensor/{1}/{2}".format(sensor.agent.ipaddr, sensor.string_id, operation)
        req = requests.get(url)
        resp = req.json()

        return redirect(url_for('sensor.index'))

    if request.method == 'POST':
        sensor_name = form.name.data
        sensor_type = form.type.data
        agent_id = form.agent.data
        
        sensor_check = Sensor.query.filter_by(user_id=current_user.id, agent_id= agent_id, type= sensor_type).first()
        if sensor_check and sensor_check.condition_id != 1 :
            msg = "Sensor {0} in agent {1} already exists. Sensor deployment failed!".format(sensor_check.type, sensor_check.agent.show_info())
            flash(msg,"alert-danger")
            return redirect(url_for('sensor.index'))
        
        else:
            sensor = Sensor(
                name= sensor_name,
                type= sensor_type,
                agent_id= agent_id,
                user_id= current_user.id
            )
            agent = Agents.query.filter_by(id=agent_id).first()
            url = 'http://{}:5000/api/v1/sensor/'.format(agent.ipaddr)
            payload = {
                'sensor_type': sensor_type,
                'sensor_image': "ardikabs/{}:1.0".format(sensor_type)
            }
            req = requests.post(url, json=payload)
            resp = req.json()
            
            if resp.get('status', False):
                sensor.container_id = resp.get('sensor').get('id')
                sensor.string_id = resp.get('sensor').get('short_id')
                sensor.status = resp.get('sensor').get('status')
                db.session.add(sensor)
                db.session.commit()
                msg = "Successfully deploy Sensor {0} in {1}".format(sensor_name, agent.show_info())
                flash(msg,'alert-success')
                return redirect(url_for('sensor.index'))
            
            msg= "Sorry! Sensor deployment on problem in Agent {}".format(agent.show_info())
            flash(msg, 'alert-danger')
            return redirect(url_for('sensor.index'))

    agents = Agents.query.filter_by(user_id= current_user.id).all()

    sensors_query_set = Sensor.query.filter_by(user_id= current_user.id).all()
    sensors = [ sensor.update() for sensor in sensors_query_set ]
    
    
    form.type.choices = (('Low-Interaction Honeypot', (('dionaea', 'Dionaea'),('glastopf', 'Glastopf'),)), ('Medium-Interaction Honeypot', (('cowrie', 'Cowrie'),)))
    form.agent.choices = [(agent.id, agent.show_info()) for agent in agents]
    
    return render_template(
        'sensor/index.html',
        agents = agents,
        sensors = sensors,
        form = form)


@sensor.route('/<int:sensor_id>')
def details(sensor_id):
    return redirect(url_for('main.index'))


