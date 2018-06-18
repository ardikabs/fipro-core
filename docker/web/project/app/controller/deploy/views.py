

from flask import current_app, jsonify, render_template, request
from flask_login import (
    current_user,
    login_required

)
from app.models import ApiKey
from . import deploy

@deploy.route('/')
def index():
    api_key = ApiKey.query.filter_by(user_id=current_user.id).first()
    host_url = request.host_url[:-1]
    deploy_script = "wget " + host_url + "/api/v1/deploy/script/?api_key=" + api_key.api_key + " -O deploy.sh && sudo bash deploy.sh "\
                    + host_url + " " + api_key.api_key + " " + "CuKX" + ";sudo rm -rf deploy.sh"

    return render_template('deploy/index.html', deploy_script=deploy_script)