
from flask import Blueprint, request, jsonify, render_template

main = Blueprint('main', __name__)

from . import views