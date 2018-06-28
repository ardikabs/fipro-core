
import datetime
import pytz
from flask import (
    current_app, 
    jsonify, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash
)

from flask_login import (
    current_user,
    login_required
)
from app import db, csrf
from app.models import ApiKey, DeployKey, User
from app.utils import rand_str
from . import deploy
from .forms import AddDeployKeyForm


@deploy.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = AddDeployKeyForm()

    if request.form.get('_method') == "PUT" :
        deploy_key = DeployKey.query.filter_by(id=request.form.get('id')).first()
        deploy_key.name = request.form.get('name')
        deploy_key.expired_at = datetime.datetime.strptime(request.form.get('expired_date'), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Jakarta'))
        db.session.commit()
        msg = "Successfully edited deploy key {0} ({1})".format(deploy_key.name,deploy_key.deploy_key)
        flash(msg,"alert-warning")
        return redirect(url_for('deploy.index'))


    if request.form.get('_method') == "DELETE" :
        deploy_key = DeployKey.query.filter_by(id=request.form.get('id')).first()
        db.session.delete(deploy_key)
        db.session.commit()

        msg = ("Success!","Deleted deploy key {0} ({1})".format(deploy_key.name,deploy_key.deploy_key))
        flash(msg,"alert-danger")
        return redirect(url_for('deploy.index'))

        
    if form.validate_on_submit():
        expired_date = form.expired_date.data.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Jakarta'))
        deploy_key = DeployKey(
            name= form.name.data,
            expired_at= expired_date,
            deploy_key= rand_str(8),
            user_id= current_user.id
        )
        db.session.add(deploy_key)
        db.session.commit()
        
        msg = ("Success!","Added deploy key {0} ({1})".format(deploy_key.name,deploy_key.deploy_key))
        flash(msg,"alert-success")
        return redirect(url_for('deploy.index'))


    api_key = ApiKey.query.filter_by(user_id=current_user.id).first()
    host_url = request.host_url[:-1]
    deploy_key_lists = DeployKey.query.all()

    if deploy_key_lists:
        return render_template('deploy/index.html', 
            api_key = api_key.api_key,
            host_url = host_url,
            deploy_key_lists = deploy_key_lists,
            form=form
        )

    else:
        return render_template('deploy/index.html', 
            form=form
        )

    