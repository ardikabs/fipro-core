
import json
import docker
from flask import Flask, flash, request, Response,url_for
from flask import render_template, jsonify


app = Flask(__name__)
client = docker.DockerClient(base_url='unix://var/run/docker.sock')

@app.before_request
def only_json():
    if not request.is_json:
        return jsonify({"status":400,"message":"Only Accept application/json"})

@app.route("/")
def index():
    return jsonify({"message":"Index of Sensor Watcher"})

@app.route("/create",methods=["POST"])
def create():
    data = request.json
    c_name = data["container_name"]
    c_type = data["container_type"]
    
    container = client.containers.run('mongo',command="mongod --smallfiles",detach=True,name=c_name)
    if container.status is "exited":
        container.remove(force=True)

    return jsonify(
        {
            "container_id":container.id,
            "container_name":container.name,
            "status":container.status
        }
    )

@app.route("/remove",methods=["POST"])
def remove():
    data = request.json

    if "prune" in data:
        if data["prune"] is True:
            container = client.containers.prune()
    else:
        pass

    if "container_id" in data:
        container = client.containers.get(data["container_id"])
        print(container.name)
        if container.status == "running":
            container.remove(force=True)

    return jsonify(
        {
            "container_id":container.id,
            "status":"removed"
        }
    )

@app.route("/remove/volume",methods=["POST"])
def remove_volume():
    volumes = client.volumes.prune()
    return jsonify(
        {
            "status":volumes
        }
    )

@app.route("/list",methods=["GET"])
def list():
    container = client.containers.list()
    container_list = []
    for con in container:
        data = con.id, con.name, con.status
        container_list.append(data)
    return jsonify(
        {
            "container_list":container_list
        }
    )

@app.route("/cekdata",methods=["POST"])
def cek():
    data = request.json
    return jsonify({
        "status":"OK"
    })
if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
