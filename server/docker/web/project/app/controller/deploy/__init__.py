
from flask import Blueprint, request, jsonify, render_template

deploy = Blueprint('deploy', __name__)


from . import controllers