
from flask import Blueprint, request, jsonify, render_template
from flask_restplus import Api

api_v1 = Blueprint('api', __name__)
api = Api(
    api_v1, 
    version='1.0', 
    title='Server-Side API',
    description='Server-Side API'
)

from .controllers_v1 import ns_agent
api.add_namespace(ns_agent)