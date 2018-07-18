import functools
from flask_login import current_user
from flask_socketio import disconnect
from app import socket

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


@socket.on("connect", namespace="/socket.io")
@authenticated_only
def on_connect():
    print ("Connected to Socket.io with user: {}".format(current_user.fullname()))

@socket.on("disconnect", namespace="/socket.io")
@authenticated_only
def on_disconnect():
    print ("Disconnected from Socket.io user:{}".format(current_user.fullname()))
    # TODO Disconnect from mqtt
    # mqtt.unsubscribe_all()
