       

from flask import jsonify, request, send_file, url_for, make_response, current_app
from flask_restplus import Namespace, Resource, fields
from flask_login import current_user
from app.models import User, ApiKey, DeployKey, Agents
from app.controller.api import api
from app import db, csrf

ns = api.namespace('deploy', description='Deploy related operations')

@ns.route('/')
class Deploy(Resource):

    def get(self):
        api_key  = ApiKey.query.filter_by(api_key=request.args.get('api_key')).first()
        
        if api_key:
            text = current_app.send_static_file('deploy.txt')
            response = make_response(text)
            response.headers['Content-Disposition'] = 'attachment; filename=deploy.sh'
            return response
        else:
            return jsonify(dict(
                message= "API Key and/or DEPLOY Key is Missing or not Available",
                status= False)
            )
    def post(self):
        api_key  = ApiKey.query.filter_by(api_key=request.args.get('api_key')).first()

        if api_key:
            uid = api_key.user.id

            deploy_key = DeployKey(user_id=uid)
            db.session.add(deploy_key)
            db.session.commit()

            return jsonify(dict(
                data=deploy_key.to_dict(),
                status=True)
            )
        else:
            return jsonify(dict(
                message= "API Key is Missing or not Authorized",
                status= False)
            )