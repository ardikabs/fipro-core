

from flask import jsonify, request, send_file, url_for, current_app, make_response
from flask_restplus import Namespace, Resource, fields
from flask_login import current_user
from app.models import User, ApiKey, DeployKey, Agents
from app.controller.api import api
from app import db, csrf

ns = api.namespace('agent', description='Agent related operations')

@ns.route("/")
class Agent(Resource):
    
    # Get List of Agent
    def get(self):
        api_key = ApiKey.query.filter_by(api_key=request.args.get('api_key')).first()
        if api_key:
            agents = [agent.to_dict() for agent in Agent.query.filter_by(user_id=api_key.user.id)]
            return make_response(
                jsonify(dict(
                    agents = agents,
                    status = True
                )), 200)

        return make_response(
            jsonify(dict(
                status=False,
                message="ApiKey are missing"
            )), 404)


    # Create Agent
    def post(self):
        data        = request.json
        api_key     = ApiKey.query.filter_by(api_key=data['api_key']).first()
        deploy_key  = DeployKey.query.filter_by(deploy_key=data['deploy_key']).first()

        if api_key and deploy_key:
            identifier = api_key.user.identifier
            agent = Agents(
                name    = deploy_key.name, 
                ipaddr  = request.remote_addr,
                user_id = api_key.user.id)
            db.session.add(agent)
            deploy_key.status = False
            
            db.session.commit()

            return make_response(
                jsonify(dict(
                    agent = agent.to_dict(),
                    ip_server = current_app.config['SERVER_IP'],
                    ip_agent = request.remote_addr,
                    identifier= identifier,
                    status=True
                )), 200)
            
        
        return make_response(
            jsonify(dict(
                status=False,
                message= "ApiKey or DeployKey are missing or not authorized"
            )), 404)
        
            
 