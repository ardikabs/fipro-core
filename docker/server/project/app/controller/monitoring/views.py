

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
    title = "Top Attacks"
    moi = MoI()
    if moi.check_conn() is False:
        return render_template('monitoring/top_attacks.html', title=title, db_info=False)
    return render_template('monitoring/top_attacks.html', title=title, db_info=True)


@monitoring.route('/event-statistics/')
@login_required
def event_statistics():
    import time
    start = time.time()
    title = "Event Statistics"
    moi = MoI()
    if moi.check_conn() is False:
        return render_template('monitoring/event_statistics.html', title=title, db_info=False)
    
    events = moi.logs.events_histogram(identifier= current_user.identifier, limit=10)
    print ("1. {}".format(time.time() - start))
    countries = moi.logs.countries_histogram(identifier= current_user.identifier, limit=10)
    print ("2. {}".format(time.time() - start))
    ports = moi.logs.ports_histogram(identifier= current_user.identifier, limit=11)
    print ("3. {}".format(time.time() - start)) 

    sensor_events_histogram = json.dumps(events, default=json_util.default)
    countries_event_histogram = json.dumps(countries, default=json_util.default)
    ports_event_histogram = json.dumps(ports, default=json_util.default)

    sensor_events = moi.logs.events_count(identifier= current_user.identifier)
    print ("4. {}".format(time.time() - start))
    ports_events = moi.logs.ports_events_count(identifier= current_user.identifier, limit=15)
    print ("5. {}".format(time.time() - start))
    countries_ports_events = moi.logs.top_countries_port(identifier= current_user.identifier, limit=6)
    print ("6. {}".format(time.time() - start))
    
    return render_template(
        'monitoring/event_statistics.html',
        title=title, 
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
    title = "Event Hourly Statistics"    
    moi = MoI()
    if moi.check_conn() is False:
        return render_template('monitoring/event_hourly.html', title=title, db_info=False)
    
    current = current_datetime()
    date = current.strftime("%Y-%m-%d")
    ts = datetime.datetime.strptime(date, "%Y-%m-%d")

    sensor_event = moi.logs.sensor_event_statistics(identifier= current_user.identifier, date=ts)
    agent_event = moi.logs.agents_event_statistics(identifier= current_user.identifier, date=ts)
    ports_event  = moi.logs.ports_event_statistics(identifier= current_user.identifier, date=ts, limit=10)
    countries_event = moi.logs.countries_event_statistics(identifier= current_user.identifier, date=ts, limit=10)
    for agent in agent_event:
        ag = Agents.query.filter_by(ipaddr=agent.get('label')).first()
        agent['agent_ip']  = agent['label']
        agent['label'] = ag.show_info()
    

    return render_template(
        'monitoring/event_hourly.html',
        title=title,
        db_info=True,
        sensor_event = sensor_event,
        agent_event = agent_event,
        ports_event = ports_event,
        countries_event = countries_event
    )



# AJAX ENDPOINT

@monitoring.route('/top-attacks/ajax/', methods=['GET','POST'])
@login_required
def top_attacks_ajax():
    moi = MoI()
    if moi.check_conn() is False:
        return make_response(jsonify([]), 500)

    res = None
    type = request.args.get('type', None)
    limit = request.args.get('limit', 10)
    identifier = current_user.identifier
    options = {'limit': limit}

    if identifier is None:
        return make_response(jsonify({'message': 'Identifier required'}), 403)

    if type == 'top_srcip_port':
        res = moi.logs.top_sourceip_port(identifier = identifier)
    
    elif type == 'top_asn':
        res = moi.logs.top_asn(identifier = identifier, options=options)
    
    elif type == 'top_countries':
        res = moi.logs.top_countries(identifier = identifier, options=options)
    
    elif type == 'top_src_ip':
        res = moi.logs.top_sourceip(identifier = identifier, options=options)
    
    elif type == 'top_unknown':
        res = moi.logs.top_unknown_sourceip(identifier = identifier, options=options)

    if res:
        return make_response(jsonify(res), 200)

    else:
        if res is not None:
            res = {'message': 'No data available', 'status':False}
            return make_response(jsonify(res), 503)

        return make_response(jsonify({"message":"Type is not recognized", "status": False}), 404)

@monitoring.route('/event-hourly-statistics/ajax/')
@login_required
def event_hourly_ajax():
    moi = MoI()
    if moi.check_conn() is False:
        return make_response(jsonify([]), 500)

    type = request.args.get('type')
    date = request.args.get('date')
    identifier = current_user.identifier

    if identifier is None:
        return make_response(jsonify({'message': 'Identifier required'}), 403)

    if date is None:
        return make_response(jsonify({'message': 'Date param is not initialized'}), 404)

    ts = datetime.datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=pytz.utc)
    
    if type == 'sensor-event':
        data = moi.logs.sensor_event_statistics(identifier= identifier, date=ts)

    elif type == 'agents-event':
        data = moi.logs.agents_event_statistics(identifier= identifier, date=ts)
        for agent in data:
            ag = Agents.query.filter_by(ipaddr=agent.get('label')).first()
            if ag is None:
                ag = OldAgents.query.filter_by(ipaddr=agent.get('label')).first()

            agent['agent_ip']  = agent['label']
            agent['label'] = ag.show_info()
        

    elif type == 'ports-event':
        data = moi.logs.ports_event_statistics(identifier= identifier, date=ts, limit=10)

    elif type == 'countries-event':
        data = moi.logs.countries_event_statistics(identifier= identifier, date=ts, limit=10)


    if data:
        return make_response(jsonify(data), 200)
    
    else:
        return make_response(jsonify([]), 404)