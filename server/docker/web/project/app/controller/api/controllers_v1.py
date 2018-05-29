

from flask import jsonify, request, send_file, url_for
from flask_restplus import Namespace, Resource, fields
from flask_login import current_user
from app.models import User, ApiKey
ns_agent = Namespace('agent', description='Script related operations')

@ns_agent.route("/")
class Agent(Resource):
    def post(self):
        apikey = ApiKey.query.filter_by(apikey=request.args.get('apikey'))
        
