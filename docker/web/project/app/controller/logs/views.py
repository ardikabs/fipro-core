

from flask import jsonify, render_template, request, make_response
from flask_login import(
    current_user,
    login_required,
    login_user,
    logout_user
)
from app.commons.MongoInterface import MongoInterface as MoI
from . import logs

@logs.route('/')
def index():
    return render_template('logs/index.html')

@logs.route('/dionaea/')
def dionaea_index():
    return render_template('logs/dionaea_index.html')
    
@logs.route('/cowrie/')
def cowrie_index():

    moi = MoI("mongodb://192.168.1.100:27017/")

    cowrie_logs = moi.logs.get(options={'limit': 1000, 'order_by': 'session'},identifier= current_user.identifier, honeypot= "cowrie")

    return render_template('logs/cowrie_index.html',data=cowrie_logs)

@logs.route('/glastopf/')
def glastopf_index():
    return render_template('logs/glastopf_index.html')


@logs.route('/cowrie/<string:session>/')
def cowrie_item(session):
    return render_template('logs/cowrie_item.html')




@logs.route('/cowrie/data-source/')
def source_cowrie():
    options = {'order_by': 'session'}
    if request.args.get('limit'):
        try:
            options['limit'] = int(request.args.get('limit'))
        except (ValueError, TypeError): 
            options['limit'] = 1000

    moi = MoI("mongodb://192.168.1.100:27017/")
    cowrie_logs = moi.logs.get(options=options,identifier= current_user.identifier, honeypot= "cowrie")
    source = [cowrie.to_dict() for cowrie in cowrie_logs]

    return make_response(jsonify(dict(data= source)), 200)

@logs.route('/dionaea/data-source/')
def source_dionaea():
    options = {'order_by': 'session'}
    if request.args.get('limit'):
        try:
            options['limit'] = int(request.args.get('limit'))
        except (ValueError, TypeError): 
            options['limit'] = 1000

    moi = MoI("mongodb://192.168.1.100:27017/")
    dionaea_logs = moi.logs.get(options=options,identifier= current_user.identifier, honeypot= "dionaea")
    source = [dionaea.to_dict() for dionaea in dionaea_logs]

    return make_response(jsonify(dict(data= source)), 200)

@logs.route('/glastopf/data-source/')
def source_glastopf():
    options = {'order_by': 'session'}
    if request.args.get('limit'):
        try:
            options['limit'] = int(request.args.get('limit'))
        except (ValueError, TypeError): 
            options['limit'] = 1000
    
    moi = MoI("mongodb://192.168.1.100:27017/")
    glastopf_logs = moi.logs.get(options=options,identifier= current_user.identifier, honeypot= "glastopf")
    source = [glastopf.to_dict() for glastopf in glastopf_logs]

    return make_response(jsonify(dict(data= source)), 200)


