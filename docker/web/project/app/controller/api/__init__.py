
from flask import Blueprint, request, jsonify, render_template
from flask_restplus import Api

api_v1 = Blueprint('api', __name__, url_prefix="/api/v1")
api = Api(
    api_v1, 
    version='1.0', 
    title='Server-Side API',
    description='Server-Side API'
)

from .v1 import *