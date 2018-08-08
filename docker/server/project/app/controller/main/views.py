

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
from app.commons.mongo import MongoCore
@main.route('/')
@login_required
def index():
    title           = "Dashboard"
    timezone        = pytz.timezone('Asia/Jakarta')
    today           = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(timezone)
    date_now        = today.strftime("%b %d")
    
    mongo = MongoCore()
    if mongo.check_connection():
        print ("Mantap")
    else:
        print ("Bosok")
        
    moi = MoI()
    if moi.check_conn() is False:
        return render_template('main/index.html', date = date_now, db_info=False)

    agents          = Agents.query.filter_by(user_id=current_user.id, condition_id=4).count()
    sensor          = Sensor.query.filter_by(user_id=current_user.id, condition_id=4).count()

    date            = today.strftime("%Y-%m-%d")
    ts_today        = datetime.datetime.strptime(date, "%Y-%m-%d")
    today_attack    = moi.logs.sensor_event_statistics(identifier= current_user.identifier, date= ts_today)
    
    today_events    = 0
    dionaea_events  = 0
    cowrie_events   = 0
    glastopf_events = 0
    for attack in today_attack:
        today_events += attack.get("counts",0)
        if attack.get("label") == "dionaea":
            dionaea_events += attack.get("counts",0)
        elif attack.get("label") == "glastopf":
            glastopf_events += attack.get("counts",0)
        else:
            cowrie_events += attack.get("counts",0)

    recent_attacks = moi.logs.recent_attacks(options={ 'limit': 10, "order_by": "-timestamp"}, identifier= current_user.identifier)
    attack_daily_stats = moi.daily.get(options={ "order_by": "date" },identifier= current_user.identifier, months_ago=1 )
    

    return render_template(
        'main/index.html',
        title=title,
        date=date_now,
        today_attack=today_events,
        agents=agents,
        sensor=sensor,
        dionaea_events=dionaea_events,
        cowrie_events=cowrie_events,
        glastopf_events=glastopf_events,
        recent_attacks=recent_attacks,
        attack_daily_stats=attack_daily_stats
    )