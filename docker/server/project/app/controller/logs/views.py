

from flask import (
    current_app, 
    jsonify, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash,
    make_response
)
from flask_login import(
    current_user,
    login_required,
    login_user,
    logout_user
)
from app.commons.MongoInterface import MongoInterface as MoI
from . import logs

@logs.route('/')
@login_required
def index():
    return redirect(url_for('main.index'))

@logs.route('/master/')
@login_required
def master_index():
    moi = MoI(mongodburl=current_app.config['MONGODB_URL'])
    if moi.check_conn() is False:
        return render_template('logs/master_index.html', db_info=False)
    
    return render_template('logs/master_index.html', db_info=True)


@logs.route('/dionaea/')
@login_required
def dionaea_index():
    moi = MoI(mongodburl=current_app.config['MONGODB_URL'])
    if moi.check_conn() is False:
        return render_template('logs/dionaea_index.html', db_info=False)
    
    return render_template('logs/dionaea_index.html', db_info=True)
    
@logs.route('/cowrie/')
@login_required
def cowrie_index():
    moi = MoI(mongodburl=current_app.config['MONGODB_URL'])
    if moi.check_conn() is False:
        return render_template('logs/cowrie_index.html', db_info=False)
    
    return render_template('logs/cowrie_index.html', db_info=True)

@logs.route('/glastopf/')
@login_required
def glastopf_index():
    moi = MoI(mongodburl=current_app.config['MONGODB_URL'])
    if moi.check_conn() is False:
        return render_template('logs/glastopf_index.html', db_info=False)
    
    return render_template('logs/glastopf_index.html', db_info=True)


@logs.route('/cowrie/data/ajax')
def source_cowrie():
    moi = MoI(mongodburl=current_app.config['MONGODB_URL'])
    if moi.check_conn() is False:
        return make_response(jsonify([]), 500)

    skip = request.args.get("start",0)
    limit = request.args.get("length",10)
    options = dict(limit=limit, skip=skip, order_by="-timestamp")    


    cowrie_logs = moi.logs.get(options=options,identifier= current_user.identifier, sensor= "cowrie")
    total_data = moi.logs.count(identifier= current_user.identifier, sensor= "cowrie")
    source = [cowrie.to_dict() for cowrie in cowrie_logs]
    response = dict(
        draw=request.args.get("draw"),
        recordsTotal=total_data,
        recordsFiltered=total_data,
        data=source
    )

    return make_response(jsonify(response), 200)

@logs.route('/dionaea/data/ajax')
def source_dionaea():
    moi = MoI(mongodburl=current_app.config['MONGODB_URL'])
    if moi.check_conn() is False:
        return make_response(jsonify([]), 500)

    skip = request.args.get("start",0)
    limit = request.args.get("length",10)
    options = dict(limit=limit, skip=skip, order_by="-timestamp")    

    dionaea_logs = moi.logs.get(options=options,identifier= current_user.identifier, sensor= "dionaea")
    total_data = moi.logs.count(identifier= current_user.identifier, sensor= "dionaea")
    source = [dionaea.to_dict() for dionaea in dionaea_logs]
    response = dict(
        draw=request.args.get("draw"),
        recordsTotal=total_data,
        recordsFiltered=total_data,
        data=source
    )

    return make_response(jsonify(response), 200)

@logs.route('/glastopf/data/ajax')
def source_glastopf():
    print (request.args)
    moi = MoI(mongodburl=current_app.config['MONGODB_URL'])
    if moi.check_conn() is False:
        return make_response(jsonify([]), 500)
    
    skip = request.args.get("start",0)
    limit = request.args.get("length",10)
    options = dict(limit=limit, skip=skip, order_by="-timestamp")    
   
    glastopf_logs = moi.logs.get(options=options,identifier= current_user.identifier, sensor= "glastopf")

    total_data = moi.logs.count(identifier= current_user.identifier, sensor= "glastopf")
    source = [glastopf.to_dict() for glastopf in glastopf_logs]

    response = dict(
        draw=request.args.get("draw"),
        recordsTotal=total_data,
        recordsFiltered=total_data,
        data=source
    )
    return make_response(jsonify(response), 200)


@logs.route('/master/data/ajax')
def source_master():
    moi = MoI(mongodburl=current_app.config['MONGODB_URL'])
    if moi.check_conn() is False:
        return make_response(jsonify([]), 500)
    
    skip = request.args.get("start",0)
    limit = request.args.get("length",10)
    options = dict(limit=limit, skip=skip, order_by="-timestamp")    
   
   
    master_logs = moi.logs.get(options=options,identifier= current_user.identifier)
    total_data = moi.logs.count(identifier= current_user.identifier)
    
    source = [master.to_dict() for master in master_logs]
    response = dict(
        draw=request.args.get("draw"),
        recordsTotal=total_data,
        recordsFiltered=total_data,
        data=source
    )
    return make_response(jsonify(response), 200)


@logs.route('/cowrie/details/<string:session>')
@login_required
def cowrie_item(session):
    return render_template('logs/cowrie_item.html')