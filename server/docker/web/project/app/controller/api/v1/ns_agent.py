

from flask import jsonify, request, send_file, url_for
from flask_restplus import Namespace, Resource, fields
from flask_login import current_user
from app.models import User, ApiKey, DeployKey, Agents
from app import db, csrf

ns_agent = Namespace('agent', description='Agent related operations')

@ns_agent.route("/")
class Agent(Resource):
    
    # Get List of Agent
    def get(self):
        apikey = ApiKey.query.filter_by(apikey=request.args.get('apikey')).first()
        if apikey:
            agents = [agent.to_dict() for agent in Agent.query.filter_by(user_id=apikey.user.id)]
            return jsonify(
                dict(
                    agents = agents,
                    status = True
                )
            )
        
        return jsonify(
            dict(
                status=False,
                message="ApiKey are missing"
            )
        )

    # Create Agent
    def post(self):
        data        = request.json
        apikey      = ApiKey.query.filter_by(apikey=request.args.get('apikey')).first()
        deploykey   = DeployKey.query.filter_by(deploykey=data['deploykey']).first()

        if apikey and deploykey:
            identifier = apikey.user.identifier
            agent = Agents(
                name    = deploykey.name, 
                ipaddr  = request.remote_addr,
                user_id = apikey.user.id)
            db.session.add(agent)
            deploykey.status = False
                
            db.session.commit()

            return jsonify(dict(
                agent = agent.to_dict(),
                identifier= identifier,
                status=True
            ))
        else:
            return jsonify(dict(
                status=False,
                message= "ApiKey and DeployKey are missing or not authorized"
            ))
            
            
 