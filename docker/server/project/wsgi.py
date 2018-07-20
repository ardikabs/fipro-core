import os
from app import create_app
import eventlet
eventlet.monkey_patch()

application = create_app(os.getenv('APP_SETTINGS') or 'default')

if __name__ == '__main__':
    application.run(host='0.0.0.0')
