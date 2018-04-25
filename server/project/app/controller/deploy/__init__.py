
from flask import Blueprint, request, jsonify, render_template

deploy = Blueprint('deploy', __name__, url_prefix='/deploy')


from . import controllers