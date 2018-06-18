

from flask import jsonify, render_template
from . import sensor

@sensor.route('/')
def index():
    return render_template('sensor/index.html')


