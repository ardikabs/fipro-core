
import docker
import time
from flask import jsonify, request
from flask_restplus import Namespace, Resource, fields
from app.api.sensor import config

api = Namespace('sensor', description='Sensor related operations')
client = docker.DockerClient(base_url='unix://var/run/docker.sock')


@api.route('/')
class HoneypotCollection(Resource):
    def get(self):
        try:
            containers = client.containers.list()
            response = {
                'status': True,
                'sensors': [
                    {
                        'sensor_id': container.id,
                        'sensor_name': container.name,
                        'sensor_status': container.status,
                        'timestamps': time.time()
                    } for container in containers
                ]
            }
            return jsonify(response)
        except docker.errors.APIError:
            response = {'status': False,'message': "There is a problem in sensor server !"}
            return jsonify(response), 500

    def post(self):
        data = request.json
        sensor_name = data["sensor_name"]
        sensor_type = data["sensor_type"]
        sensor_image = data["sensor_image"] or "ardikabs/"+sensor_type+":1.0"

        try:
            container = client.containers.run(image=sensor_image, 
                                            name=sensor_name,
                                            restart_policy={"Name": "always"},
                                            ports= config.container_attributes[sensor_type]['ports'],
                                            volumes= config.container_attributes[sensor_type]['volumes'],
                                            detach=True)

            response = {
                'status': True,
                'sensor_name': sensor_name,
                'sensor_id': container.id,
                'message': "Sensor "+ sensor_name +" successfully has been added",
                'timestamps': time.time()
            }

            return jsonify(response)
        
        except docker.errors.APIError:
            response = {'status': False,'message': "There is a problem in sensor server !"}
            return jsonify(response), 500

@api.route('/<string:sensor_id>')
class HoneypotItem(Resource):
    def get(self, sensor_id):
        try:
            container= client.containers.get(sensor_id)
            response = {
                'status': True,
                'sensor': {
                    'sensor_id': container.id, 
                    'sensor_name': container.name, 
                    'sensor_status': container.status
                },
                'timestamps': time.time()
            }

            return jsonify(response)
            
        except docker.errors.NotFound:
            response = {"status":False,"message":"Container not Found"}
            return jsonify(response), 404
    
    def put(self, sensor_id):
        data = request.json
        sensor_name = data["sensor_name"]
        print (sensor_name)
        try:
            container = client.containers.get(sensor_id)
            container.rename(name=sensor_name)

            response = {
                'status': True,
                'sensor_id': container.id,
                'sensor_name': sensor_name,
                'message': "Sensor "+ container.name +" has been renamed with "+sensor_name,
                'timestamps': time.time()
            }

            return jsonify(response)
        
        except docker.errors.APIError:
            response = {'status': False,'message': "There is a problem in sensor server !"}
            return jsonify(response), 500


    def delete(self, sensor_id):
        try:
            container = client.containers.get(sensor_id)
            container.remove(force=True)

            response = {
                'status': True,
                'sensor_id': container.id,
                'sensor_name': container.name,
                'message': "Sensor "+ container.name +" has been removed",
                'timestamps': time.time()
            }

            return jsonify(response)
        
        except docker.errors.APIError:
            response = {'status': False,'message': "There is a problem in sensor server !"}
            return jsonify(response), 500
