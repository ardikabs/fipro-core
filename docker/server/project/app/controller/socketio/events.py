from flask import jsonify, make_response, current_app
from flask_socketio import emit
from flask_login import(
    current_user,
    login_required,
    login_user,
    logout_user
)
from . import socketio
from .worker import Worker
from app.decorators import authenticated_only

worker = None

############################
'''
Events SocketIO
'''
############################

@socketio.on("get_recent_attacks", namespace="/socket.io")
@authenticated_only
def request_recent_attacks(data):
    global worker
    worker = Worker(socketio)
    socketio.start_background_task(target=worker.run, args=(current_app._get_current_object(),), **{'identifier':current_user.identifier})








############################
'''
Connection SocketIO
'''
############################

@socketio.on("connect", namespace="/socket.io")
@authenticated_only
def on_connect():
    print ("Connected to Socket.io with user: {}".format(current_user.fullname()))

@socketio.on("disconnect", namespace="/socket.io")
@authenticated_only
def on_disconnect():
    if worker is not None:
        worker.stop()
    print ("Disconnected from Socket.io user:{}".format(current_user.fullname()))
    # TODO Disconnect from mqtt