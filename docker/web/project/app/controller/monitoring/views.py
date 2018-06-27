

import datetime
import pytz
import json
from bson import json_util
from flask import (
    current_app, 
    jsonify, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash,
    make_response
)

from flask_login import (
    current_user,
    login_required
)

from . import monitoring
from app.utils import get_datetime, current_datetime
from app.commons.MongoInterface import MongoInterface as MoI
from app.models import Agents, OldAgents

@monitoring.route('/')
@login_required
def index():
    return redirect(url_for('main.index'))

@monitoring.route('/top-attacks/')
@login_required
def top_attacks():
    moi = MoI(mongodburl=current_app.config['MONGODB_URL'])
    if moi.check_conn() is False:
        return render_template('monitoring/top_attacks.html', db_info=False)
    return render_template('monitoring/top_attacks.html', db_info=True)


@monitoring.route('/event-statistics/')
@login_required
def event_statistics():

    moi = MoI(mongodburl=current_app.config['MONGODB_URL'])
    if moi.check_conn() is False:
        return render_template('monitoring/event_statistics.html', db_info=False)
    
    events = moi.logs.events_histogram(identifier= current_user.identifier, limit=10)
    countries = moi.logs.countries_histogram(identifier= current_user.identifier, limit=10)
    ports = moi.logs.ports_histogram(identifier= current_user.identifier, limit=11)

    sensor_events_histogram = json.dumps(events, default=json_util.default)
    countries_event_histogram = json.dumps(countries, default=json_util.default)
    ports_event_histogram = json.dumps(ports, default=json_util.default)

    sensor_events = moi.logs.events_count(identifier= current_user.identifier)
    ports_events = moi.logs.ports_events_count(identifier= current_user.identifier, limit=15)
    countries_ports_events = moi.logs.top_countries_port(identifier= current_user.identifier, limit=6)
    
   
    return render_template(
        'monitoring/event_statistics.html', 
        db_info=True,
        sensor_event_histogram=sensor_events_histogram,
        countries_event_histogram=countries_event_histogram,
        ports_event_histogram=ports_event_histogram,
        sensor_events=sensor_events,
        ports_events=ports_events,
        countries_ports_events=countries_ports_events
    )

@monitoring.route('/event-hourly-statistics/')
@login_required
def event_hourly_statistics():
    moi = MoI(mongodburl=current_app.config['MONGODB_URL'])
    if moi.check_conn() is False:
        return render_template('monitoring/event_hourly.html', db_info=False)
    
    ts = current_datetime()
    sensor_event = moi.logs.sensor_event_statistics(identifier= current_user.identifier, date=ts)
    agent_event = moi.logs.agents_event_statistics(identifier= current_user.identifier, date=ts)
    ports_event  = moi.logs.ports_event_statistics(identifier= current_user.identifier, date=ts)
    countries_event = moi.logs.countries_event_statistics(identifier= current_user.identifier, date=ts)
    
    for agent in agent_event:
        ag = Agents.query.filter_by(ipaddr=agent.get('label')).first()
        agent['agent_ip']  = agent['label']
        agent['label'] = ag.show_info()
    

    return render_template(
        'monitoring/event_hourly.html',
        db_info=True,
        sensor_event = sensor_event,
        agent_event = agent_event,
        ports_event = ports_event,
        countries_event = countries_event
    )



# AJAX ENDPOINT

@monitoring.route('/top-attacks/ajax/', methods=['GET','POST'])
def top_attacks_ajax():
    moi = MoI(mongodburl=current_app.config['MONGODB_URL'])
    if moi.check_conn() is False:
        return make_response(jsonify([]), 500)

    res = None
    type = request.args.get('type', None)
    limit = request.args.get('limit', 10)
    options = {'limit': limit}


    if type == 'top_srcip_port':
        res = moi.logs.top_sourceip_port(identifier = current_user.identifier)
    
    elif type == 'top_asn':
        res = moi.logs.top_asn(identifier = current_user.identifier, options=options)
    
    elif type == 'top_countries':
        res = moi.logs.top_countries(identifier = current_user.identifier, options=options)
    
    elif type == 'top_src_ip':
        res = moi.logs.top_sourceip(identifier = current_user.identifier, options=options)
    
    elif type == 'top_unknown':
        res = moi.logs.top_unknown_sourceip(identifier = current_user.identifier, options=options)

    if res:
        return make_response(jsonify(res), 200)

    else:
        if res is not None:
            res = {'message': 'No data available', 'status':False}
            return make_response(jsonify(res), 503)

        return make_response(jsonify({"message":"Type is not recognized", "status": False}), 404)

@monitoring.route('/event-hourly-statistics/ajax/')
def event_hourly_ajax():
    moi = MoI(mongodburl=current_app.config['MONGODB_URL'])
    if moi.check_conn() is False:
        return make_response(jsonify([]), 500)

    type = request.args.get('type')
    date = request.args.get('date')
    
    if date is None:
        return make_response(jsonify({'message': 'Date param is not initialized'}), 404)

    ts = datetime.datetime.strptime(date, '%Y-%m-%d')
    

    if type == 'sensor-event':
        data = moi.logs.sensor_event_statistics(identifier= current_user.identifier, date=ts)

    elif type == 'agents-event':
        data = moi.logs.agents_event_statistics(identifier= current_user.identifier, date=ts, limit=10)
        print (data)
        for agent in data:
            ag = Agents.query.filter_by(ipaddr=agent.get('label')).first()
            if ag is None:
                ag = OldAgents.query.filter_by(ipaddr=agent.get('label')).first()

            agent['agent_ip']  = agent['label']
            agent['label'] = ag.show_info()
        
        print (data)

    elif type == 'ports-event':
        data = moi.logs.ports_event_statistics(identifier= current_user.identifier, date=ts, limit=10)

    elif type == 'countries-event':
        data = moi.logs.countries_event_statistics(identifier= current_user.identifier, date=ts, limit=10)

    if data:
        return make_response(jsonify(data), 200)
    
    else:
        return make_response(jsonify([]), 404)