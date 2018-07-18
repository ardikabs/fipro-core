from flask_socketio import emit
from . import socket, authenticated_only


@socket.on("last_attack", namespace="/socket.io")
def last_attack(data):
    print (data)