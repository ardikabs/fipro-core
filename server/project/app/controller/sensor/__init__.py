
from flask import Blueprint, request, jsonify, render_template

sensor = Blueprint('sensor', __name__, url_prefix='/sensor')


from . import controllers