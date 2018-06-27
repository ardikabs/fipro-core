

from flask import (
    current_app, 
    jsonify, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash
)
from . import main
from flask_login import(
    current_user,
    login_required,
    login_user,
    logout_user
)
import datetime
import pytz

from app.models import ApiKey, Agents, Sensor
from app.commons.MongoInterface import MongoInterface as MoI

@main.route('/')
@login_required
def index():
    timezone        = pytz.timezone('Asia/Jakarta')
    today           = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(timezone)
    date_now        = today.strftime("%b %d")

    moi = MoI(mongodburl=current_app.config['MONGODB_URL'])
    if moi.check_conn() is False:
        return render_template('main/index.html', date = date_now, db_info=False)

    dt = datetime.datetime.strptime('2017-11-01',"%Y-%m-%d")

    cursor_today    = moi.daily.get_one(identifier= current_user.identifier, date= dt)
    cursor_dionaea  = moi.sensor_event.get_one(identifier= current_user.identifier, date= dt, sensor="dionaea")
    cursor_cowrie   = moi.sensor_event.get_one(identifier= current_user.identifier, date= dt, sensor="cowrie")
    cursor_glastopf = moi.sensor_event.get_one(identifier= current_user.identifier, date= dt, sensor="glastopf")

    agents          = Agents.query.filter_by(user_id=current_user.id, condition_id=4).count()
    sensor          = Sensor.query.filter_by(user_id=current_user.id, condition_id=4).count()


    today_attack    = cursor_today.counts if cursor_today else 0
    dionaea_events  = cursor_dionaea.counts if cursor_dionaea else 0
    cowrie_events   = cursor_cowrie.counts if cursor_cowrie else 0 
    glastopf_events = cursor_glastopf.counts if cursor_glastopf else 0

    recent_attacks = moi.logs.recent_attacks(options={ 'limit': 10 }, identifier= current_user.identifier, hours_ago=8760)
    attack_daily_stats = moi.daily.get(options={ "order_by": "date" },identifier= current_user.identifier, months_ago=12 )
    

    return render_template(
        'main/index.html',
        date=date_now,
        today_attack=today_attack,
        agents=agents,
        sensor=sensor,
        dionaea_events=dionaea_events,
        cowrie_events=cowrie_events,
        glastopf_events=glastopf_events,
        recent_attacks=recent_attacks,
        attack_daily_stats=attack_daily_stats
    )