
from flask import Blueprint, request, jsonify, render_template

agents = Blueprint('agents', __name__)


from . import views