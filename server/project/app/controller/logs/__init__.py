
from flask import Blueprint, request, jsonify, render_template

logs = Blueprint('logs', __name__)


from . import controllers