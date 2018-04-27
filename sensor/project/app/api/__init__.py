
from flask_restplus import Api
from flask import Blueprint
from app.api.sensor.routes import api as sensor_api

api_v1 = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(
    api_v1, 
    version='1.0', 
    title='Sensor-Side API',
    description='A Sensor-Side API for Sensor Management with Docker API'
)

api.add_namespace(sensor_api)