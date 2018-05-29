
from flask import Blueprint, request, jsonify, render_template

sensor = Blueprint('sensor', __name__)


from . import views