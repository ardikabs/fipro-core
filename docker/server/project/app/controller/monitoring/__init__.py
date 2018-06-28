
from flask import Blueprint, request, jsonify, render_template

monitoring = Blueprint('monitoring', __name__)


from . import views