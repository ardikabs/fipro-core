

from flask import jsonify, render_template
from . import sensor

@sensor.route('/')
def index():
    return jsonify({
        "message":"Hello Sensor"
    })