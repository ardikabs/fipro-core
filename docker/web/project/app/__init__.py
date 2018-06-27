
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
# from flask_assets import Environment
# from .assets import assets_bundles
from config import config
from app import errors as err
basedir = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy()
csrf = CSRFProtect()

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "accounts.login"


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    ''' Application Configuration '''
    config[config_name].init_app(app)

    ''' Extension Configuration '''
    with app.app_context():
        db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    ''' Assets Configuration '''
    '''
    assets_env = Environment(app)
    assets_env.debug = True
    dirs = ['assets/styles', 'assets/scripts']
    for path in dirs:
        assets_env.append_path(os.path.join(basedir,path))
    assets_env.url_expire = True
    
    for key in assets_bundles:
        assets_env.register(key, assets_bundles[key])
        assets_env[key].build()
    '''
    
    ''' Configure SSL if platform supports it '''
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        app.config['SERVER_BASE_URL'][0] = "https://"
        SSLify(app)
   

    ''' Blueprint Configuration '''
    from .controller.main import main as main_blueprint
    from .controller.accounts import accounts as accounts_blueprint
    from .controller.agents import agents as agents_blueprint
    from .controller.sensor import sensor as sensor_blueprint
    from .controller.deploy import deploy as deploy_blueprint
    from .controller.logs import logs as logs_blueprint
    from .controller.monitoring import monitoring as monitoring_blueprint


    app.register_blueprint(main_blueprint)
    app.register_blueprint(accounts_blueprint, url_prefix='/accounts')
    app.register_blueprint(agents_blueprint, url_prefix='/agents')
    app.register_blueprint(sensor_blueprint, url_prefix='/sensor')
    app.register_blueprint(deploy_blueprint, url_prefix='/deploy')
    app.register_blueprint(logs_blueprint, url_prefix='/logs')
    app.register_blueprint(monitoring_blueprint, url_prefix='/monitoring')
    
    from .controller.api import api_v1 
    app.register_blueprint(api_v1)
    csrf.exempt(api_v1)


    ''' Error Handler Configuration '''
    app.register_error_handler(404,err.page_not_found)
    app.register_error_handler(500,err.internal_problems)        
    
    app.jinja_env.add_extension('jinja2.ext.do')
    return app