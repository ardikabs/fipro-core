

from flask import jsonify, render_template, redirect, url_for
from . import monitoring

@monitoring.route('/')
def index():
    return redirect(url_for('main.index'))

@monitoring.route('/top-attacks/')
def top_attacks():
    return render_template('monitoring/top_attacks.html')

@monitoring.route('/event-statistics/')
def event_statistics():
    return render_template('monitoring/event_statistics.html')

@monitoring.route('/event-hourly-statistics/')
def event_hourly_statistics():
    return render_template('monitoring/event_hourly.html')


