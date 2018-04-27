
import os
from app import create_app
from flask_script import Manager, Shell



app = create_app(os.getenv('FLAS_CONFIG') or 'development')
manager = Manager(app)



@manager.command
def runserver():    
    app.run(debug=True, host='0.0.0.0')


if __name__ == "__main__":
    manager.run()