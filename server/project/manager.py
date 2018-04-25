

from flask_script import Manager, Shell
from app import create_app

app = create_app('development')
manager = Manager(app)

@manager.command
def runserver():
    app.run(debug=True, host='0.0.0.0')

if __name__ == "__main__":
    manager.run()