

import datetime
import pytz
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
from app.models import Agents

@monitoring.route('/')
def index():
    return redirect(url_for('main.index'))

@monitoring.route('/top-attacks/')
def top_attacks():

    return render_template('monitoring/top_attacks.html')


@monitoring.route('/top-attacks/ajax/', methods=['GET','POST'])
def top_attacks_ajax():
    moi = MoI(mongodburl="mongodb://192.168.1.100:27017/")

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


@monitoring.route('/event-statistics/')
def event_statistics():
    import json
    from bson import json_util
    moi = MoI(mongodburl="mongodb://192.168.1.100:27017/")
    # sensor_event_histogram = moi.logs.sensor_event_statistics(identifier= current_user.identifier, years_ago=2)
    # countries_event_histogram = moi.logs.countries_event_statistics(identifier= current_user.identifier, years_ago=2)
    # ports_event_histogram = moi.logs.ports_event_statistics(identifier= current_user.identifier, years_ago=2)
    
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
        sensor_event_histogram=sensor_events_histogram,
        countries_event_histogram=countries_event_histogram,
        ports_event_histogram=ports_event_histogram,
        sensor_events=sensor_events,
        ports_events=ports_events,
        countries_ports_events=countries_ports_events
    )

@monitoring.route('/event-hourly-statistics/')
def event_hourly_statistics():
    moi = MoI(mongodburl="mongodb://192.168.1.100:27017/")
    
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
        sensor_event = sensor_event,
        agent_event = agent_event,
        ports_event = ports_event,
        countries_event = countries_event
    )


@monitoring.route('/event-hourly-statistics/ajax/')
def event_hourly_ajax():
    option = request.args.get('type')
    date = request.args.get('date')
    print (date)
    
    if date is None:
        return make_response(jsonify({'message': 'Date param is not initialized'}), 404)

    ts = datetime.datetime.strptime(date, '%Y-%m-%d')
    moi = MoI(mongodburl="mongodb://192.168.1.100:27017/")


    data_source = {
        'sensor-event': moi.logs.sensor_event_statistics(identifier= current_user.identifier, date=ts),
        'ports-event': moi.logs.ports_event_statistics(identifier= current_user.identifier, date=ts),
        'agents-event': moi.logs.agents_event_statistics(identifier= current_user.identifier, date=ts),
        'countries-event': moi.logs.countries_event_statistics(identifier= current_user.identifier, date=ts)
    }

    if data_source['agents-event']:
        for agent in data_source['agents-event']:
            ag = Agents.query.filter_by(ipaddr=agent.get('label')).first()
            agent['agent_ip']  = agent['label']
            agent['label'] = ag.show_info()

    if data_source[option]:
        return make_response(jsonify(data_source[option]), 200)
    
    else:
        return make_response(jsonify([]), 404)