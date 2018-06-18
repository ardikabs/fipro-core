

from flask import jsonify, render_template, abort, request
from . import main
from flask_login import(
    current_user,
    login_required,
    login_user,
    logout_user
)
import datetime
import pytz

from app.models import ApiKey

@main.route('/')
@login_required
def index():

    timezone = pytz.timezone('America/Los_Angeles')
    today = timezone.localize(datetime.datetime.today())

    date_now        = today.strftime("%b %d")
    attack_daily    = 250
    agents          = 5
    sensor       = 6
    dionaea_events  = 17000
    cowrie_events   = 2000
    glastopf_events = 35000

    return render_template(
        'main/index.html',
        date=date_now,
        attack_daily=attack_daily,
        agents=agents,
        sensor=sensor,
        dionaea_events=dionaea_events,
        cowrie_events=cowrie_events,
        glastopf_events=glastopf_events
    )