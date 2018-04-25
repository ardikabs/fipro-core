

from flask import Flask, request, jsonify
from config import config

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    config[config_name].init_app(app)

    # Blueprint Configuration
    from .controller.main import main as main_blueprint
    from .controller.sensor import sensor as sensor_blueprint
    from .controller.deploy import deploy as deploy_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(sensor_blueprint)
    app.register_blueprint(deploy_blueprint)
    return app

