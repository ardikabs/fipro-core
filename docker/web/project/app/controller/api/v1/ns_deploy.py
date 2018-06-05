       

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
            deploy_key = [deploy_key.to_dict() for deploy_key in DeployKey.query.filter_by(user_id=api_key.user.id)]
            return make_response(
                jsonify(dict(
                    deploy_key = deploy_key,
                    status= True
                )), 200)

        return make_response(
            jsonify(dict(
                message= "API Key is missing or not Authorized",
                status= False
            )), 401)

    def post(self):
        api_key  = ApiKey.query.filter_by(api_key=request.args.get('api_key')).first()

        if api_key:
            uid = api_key.user.id

            deploy_key = DeployKey(user_id=uid)
            db.session.add(deploy_key)
            db.session.commit()

            return make_response(
                jsonify(dict(
                    data=deploy_key.to_dict(),
                    status=True
                )), 201)
        else:
            return make_response(
                jsonify(dict(
                    message= "API Key is Missing or not Authorized",
                    status= False
                )), 401)

@ns.route('/<string:deploy_key>')
class DeployKeyItem(Resource):
    def get(self, deploy_key):
        pass
    
    def delete(sellf, deploy_key):
        pass

@ns.route('/script')
@ns.route('/script/')
class DeployScript(Resource):

    def get(self):
        api_key  = ApiKey.query.filter_by(api_key=request.args.get('api_key')).first()
        
        if api_key:
            text = current_app.send_static_file('deploy.sh')
            response = make_response(text)
            response.headers['Content-Disposition'] = 'attachment; filename=deploy.sh'
            return response

        else:
            return make_response(
                jsonify(dict(
                    message= "API Key and/or DEPLOY Key is Missing or not Available",
                    status= False
                )), 404)
