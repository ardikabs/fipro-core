

from flask import jsonify, request, send_file, url_for, current_app, make_response
from flask_restplus import Namespace, Resource, fields
from flask_login import current_user
from app.models import User, ApiKey, DeployKey, Agents
from app.controller.api import api
from app import db, csrf
import datetime

ns = api.namespace('agent', description='Agent related operations')

@ns.route("/")
class Agent(Resource):
    
    # Get List of Agent
    def get(self):
        api_key = ApiKey.query.filter_by(api_key=request.args.get('api_key')).first()
        if api_key:
            agents = [agent.to_dict() for agent in Agents.query.filter_by(user_id=api_key.user.id)]
            return make_response(
                jsonify(dict(
                    agents = [] if len(agents) == 0 else agents,
                    status = True
                )), 200)

        return make_response(
            jsonify(dict(
                status=False,
                message="ApiKey are missing"
            )), 400)


    # Create Agent
    def post(self):
        data        = request.json
        api_key     = ApiKey.query.filter_by(api_key=data['api_key']).first()
        deploy_key  = DeployKey.query.filter_by(deploy_key=data['deploy_key']).first()

        if api_key and deploy_key:
            date_comparison = datetime.datetime.now() > deploy_key.expired_at
            if deploy_key.status is False or date_comparison :
                deploy_key.status = False if date_comparison else deploy_key.status 
                db.session.commit()
                return make_response(
                    jsonify(dict(
                        deploy_key=deploy_key.deploy_key,
                        status= "valid" if deploy_key.status else "expired"
                    )), 400)

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
                )), 201)
                
        
        return make_response(
            jsonify(dict(
                status=False,
                message= "ApiKey or DeployKey are missing or not authorized"
            )), 404)

@ns.route("/<string:string_id>")
@ns.route("/<string:string_id>/")
class AgentItem(Resource):

    def get(self, string_id):
        api_key = ApiKey.query.filter_by(api_key=request.args.get('api_key')).first() 
        agent   = Agents.query.filter_by(string_id=string_id).first()

        if api_key and agent:
            return make_response(
            jsonify(), 200)
        
        return make_response(
            jsonify(dict(
                message="ApiKey is Missing or Agent not Found",
                status=False
            )), 400)

    
    def delete(self, string_id):
        api_key = ApiKey.query.filter_by(api_key=request.args.get('api_key')).first() 
        agent   = Agents.query.filter_by(string_id=string_id).first()

        if api_key and agent:
            db.session.delete(agent)
            db.session.commit()
            return make_response(
                jsonify(dict(
                    agent=agent.to_dict(),
                    status=True,
                    message="Agent {} has been deleted".format(agent.name)                    
                )), 200)
        
        return make_response(
            jsonify(dict(
                message="ApiKey is Missing or Agent not Found",
                status=False
            )), 400)

        
            
 