import os
from app import create_app
import eventlet
eventlet.monkey_patch()

application = create_app(os.getenv('FLASK_CONFIG') or 'default')